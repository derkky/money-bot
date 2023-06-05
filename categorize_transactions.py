from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

from variables import *

from util import *
from sheets import *


# Categorize transactions
async def select_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    RANGE_NAME = 'Uncategorized!A2:F'
    transactions = get_values(RANGE_NAME)

    context.user_data["UNCATEGORIZED_TRANSACTIONS"] = transactions

    if context.user_data.get("UPDATED_TRANSACTIONS") is None:
        context.user_data["UPDATED_TRANSACTIONS"] = {}

    keyboard = []
    lst = []

    for trans in transactions:
        if len(trans) < 3: # Some missing info
            continue

        str_trans = str(trans)

        if len(lst) < 2:
            lst.append(InlineKeyboardButton(str_trans, callback_data=trans[0]))
        else:
            keyboard.append(lst)
            lst = []
            lst.append(InlineKeyboardButton(str_trans, callback_data=trans[0]))

    keyboard.append(lst)

    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    await query.edit_message_text("Select transaction", reply_markup=reply_markup)

    return SELECTING_TRANSACTION

async def categorize_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    context.user_data["CURRENT_TRANSACTION"] = query.data # Stores IDX
    categories = ["Leisure", "Food", "Travel"] # TODO: Link to google sheets api

    keyboard = []
    lst = []

    for cat in categories:
        if len(lst) < 2:
            lst.append(InlineKeyboardButton(cat, callback_data=cat))
        else:
            keyboard.append(lst)
            lst = []
            lst.append(InlineKeyboardButton(cat, callback_data=cat))

    keyboard.append(lst)

    reply_markup = InlineKeyboardMarkup(keyboard)

    selected_transaction = [trans for trans in context.user_data["UNCATEGORIZED_TRANSACTIONS"] if trans[0] == query.data][0]


    await query.edit_message_text(f"Selected transaction: {selected_transaction}, Select category", reply_markup=reply_markup)
    return SELECTING_CATEGORY

async def categorize_transaction_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query

    user_data["UPDATED_TRANSACTIONS"][user_data["CURRENT_TRANSACTION"]] = query.data

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=str(NEW_DONE_YES)),
            InlineKeyboardButton("No", callback_data=str(NEW_DONE_NO))
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    updated_transactions_idxs = list(user_data["UPDATED_TRANSACTIONS"].keys())

    updated_transactions = [trans + [query.data] for trans in user_data["UNCATEGORIZED_TRANSACTIONS"] if trans[0] in updated_transactions_idxs]

    await query.edit_message_text(f"Updated transactions: {updated_transactions}. Confirm/finish?", reply_markup=reply_markup) # TODO: pretty print

    return CATEGORIZE_TRANSACTIONS_END

async def categorize_transaction_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    updates = list(user_data["UPDATED_TRANSACTIONS"].items())

    data = [{"range": f"Transactions!E{updt[0]}", "values": [[updt[1]]]} for updt in updates]
    batch_update_values("USER_ENTERED", data)

    user_data["UPDATED_TRANSACTIONS"] = {}

    return await start_over(update, context)
