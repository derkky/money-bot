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
from datetime import date

from variables import *
from util import *
from sheets import *

# Add new transaction

async def add_new_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    keyboard = [
        [
            InlineKeyboardButton("Name", callback_data=str(NEW_NAME)),
            InlineKeyboardButton("Value", callback_data=str(NEW_VALUE)),
            InlineKeyboardButton("Category", callback_data=str(NEW_CATEGORY)),
            InlineKeyboardButton("Done", callback_data=str(NEW_DONE))
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)


    if query is not None: # Previous action was button press
        await query.answer()
        await query.edit_message_text("Input transaction details", reply_markup=reply_markup)

    else: # Previous action was message
        await update.message.reply_text("Got it, update remaining details", reply_markup=reply_markup)

    return SELECTING_TRANSACTION_DETAIL

async def input_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["CURRENT_FEATURE"] = query.data

    await query.edit_message_text("Input detail")

    return ENTERING_INFO

async def new_select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    context.user_data["CURRENT_FEATURE"] = query.data
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


    await query.edit_message_text("Select category", reply_markup=reply_markup)

    return ENTERING_INFO


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query

    if query is not None:
        await query.answer()
        user_data[user_data["CURRENT_FEATURE"]] = query.data
    else:
        user_data[user_data["CURRENT_FEATURE"]] = update.message.text

    return await add_new_transaction(update, context)

async def new_transaction_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    query = update.callback_query

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=str(NEW_DONE_YES)),
            InlineKeyboardButton("No", callback_data=str(NEW_DONE_NO))
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    transaction_details = {
        "Name": user_data.get(str(NEW_NAME)),
        "Value": user_data.get(str(NEW_VALUE)),
        "Category": user_data.get(str(NEW_CATEGORY))
    }

    await query.edit_message_text(f"Transaction details: {transaction_details}. Confirm?", reply_markup=reply_markup)

    return NEW_TRANSACTION_END

async def new_done_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    _values = [[
        "=ROW()", 
        date.today().strftime("%d/%m/%Y"), 
        user_data.get(str(NEW_NAME)), 
        user_data.get(str(NEW_VALUE)),
        user_data.get(str(NEW_CATEGORY))
        ]]

    append_values("USER_ENTERED", _values)
    return await start_over(update, context)