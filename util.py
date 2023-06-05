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

async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Add new transaction", callback_data=str(ADD_NEW_TRANSACTION)),
            InlineKeyboardButton("Categorize transactions", callback_data=str(CATEGORIZE_TRANSACTIONS))
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Choose an action", reply_markup=reply_markup)

    return SELECTING_ACTION