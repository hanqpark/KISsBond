import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Create the Application and pass it your bot's token.
YOUR_BOT_TOKEN = os.environ.get("PYCON_TELE_TOKEN")
application = Application.builder().token(YOUR_BOT_TOKEN).build()

# Define a dictionary to store user data
user_data = {}


# Command handler to start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_data[user_id] = {}  # Initialize user data for this user
    reply_markup = {
        "keyboard": [[str(i + 1)] for i in range(10)],
        "one_time_keyboard": True,
        "resize_keyboard": False,
    }
    await update.message.reply_text(
        "Please choose an option:", reply_markup=reply_markup
    )


# Handler to process user's choice
async def process_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text
    user_data[user_id]["choice"] = text
    await update.message.reply_text(f"You selected: {text}")


# Handler to stop the conversation
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_data:
        del user_data[user_id]  # Remove user data when the conversation ends
    await update.message.reply_text("Conversation ended.")


# Add handlers to the application
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_choice))
application.add_handler(CommandHandler("stop", stop))

# Run the bot until the user presses Ctrl-C
application.run_polling(allowed_updates=Update.ALL_TYPES)
