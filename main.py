
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

from add_new_transaction import *
from categorize_transactions import *

from variables import *
from util import *
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Add new transaction", callback_data=str(ADD_NEW_TRANSACTION)),
            InlineKeyboardButton("Categorize transactions", callback_data=str(CATEGORIZE_TRANSACTIONS))
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Choose an action", reply_markup=reply_markup)

    return SELECTING_ACTION


if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(add_new_transaction, pattern="^" + str(ADD_NEW_TRANSACTION) + "$"),
                CallbackQueryHandler(select_transaction)
            ],
            SELECTING_TRANSACTION_DETAIL: [
                CallbackQueryHandler(new_transaction_done, pattern="^" + str(NEW_DONE) + "$"),
                CallbackQueryHandler(new_select_category, pattern="^" + str(NEW_CATEGORY) + "$"),
                CallbackQueryHandler(input_detail),
            ],
            ENTERING_INFO: [
                MessageHandler(filters.TEXT, save_input), # TODO: filter commands
                CallbackQueryHandler(save_input)
            ],
            NEW_TRANSACTION_END: [
                CallbackQueryHandler(new_done_yes, pattern="^" + str(NEW_DONE_YES) + "$"),
                CallbackQueryHandler(add_new_transaction)
            ],
            SELECTING_TRANSACTION: [
                CallbackQueryHandler(categorize_transaction)
            ],
            SELECTING_CATEGORY: [
                CallbackQueryHandler(categorize_transaction_done)
            ],
            CATEGORIZE_TRANSACTIONS_END: [
                CallbackQueryHandler(categorize_transaction_yes, pattern="^" + str(NEW_DONE_YES) + "$"),
                CallbackQueryHandler(select_transaction)
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()