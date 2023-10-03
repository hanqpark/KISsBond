import os
import time
import logging
from typing import Dict
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from crawl import (
    crawl_dart_search,
    crawl_dart_select,
    get_bond_issu_info_service,
    crawl_krx,
    crawl_news,
)


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "company" in user_data:
        del user_data["company"]

    if "bond" in user_data:
        del user_data["bond"]

    if "corp_reg_no" in user_data:
        del user_data["corp_reg_no"]

    await update.message.reply_text(
        f"Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    corp_name = update.message.text
    corp_code = crawl_dart_search(corp_name)
    corp_reg_no = crawl_dart_select(corp_code)
    if corp_reg_no:
        logger.info("Corporation Register Number of %s: %s", corp_name, corp_reg_no)
        await update.message.reply_text(f"{corp_name}의 채권에 대해 알고 싶으시군요?")
        time.sleep(0.5)
        await update.message.reply_text("채권 선택 버튼을 눌러 채권을 골라주세요", reply_markup=markup)
        return CHOOSING
    else:
        logger.info("Corportation doesn't exist!")
        await update.message.reply_text(f"{corp_name} 기업을 찾을 수 없어요 😢")
        time.sleep(0.5)
        await update.message.reply_text("기업명을 다시 정확하게 입력해주세요")
        return COMPANY


async def bond_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    corp_name = update.message.text
    corp_code = crawl_dart_search(corp_name)
    corp_reg_no = crawl_dart_select(corp_code)
    if corp_reg_no:
        logger.info("Corporation Register Number of %s: %s", corp_name, corp_reg_no)
        await update.message.reply_text(f"{corp_name}의 채권에 대해 알고 싶으시군요?")
        time.sleep(0.5)
        await update.message.reply_text("채권 선택 버튼을 눌러 채권을 골라주세요", reply_markup=markup)
        return CHOOSING
    else:
        logger.info("Corportation doesn't exist!")
        await update.message.reply_text(f"{corp_name} 기업을 찾을 수 없어요 😢")
        time.sleep(0.5)
        await update.message.reply_text("기업명을 다시 정확하게 입력해주세요")
        return COMPANY


async def bond_return(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    bond_name = update.message.text
    corp_code = crawl_dart_search(corp_name)
    corp_reg_no = crawl_dart_select(corp_code)
    if corp_reg_no:
        logger.info("Corporation Register Number of %s: %s", corp_name, corp_reg_no)
        await update.message.reply_text(f"{corp_name}의 채권에 대해 알고 싶으시군요?")
        time.sleep(0.5)
        await update.message.reply_text("채권 선택 버튼을 눌러 채권을 골라주세요", reply_markup=markup)
        return CHOOSING
    else:
        logger.info("Corportation doesn't exist!")
        await update.message.reply_text(f"{corp_name} 기업을 찾을 수 없어요 😢")
        time.sleep(0.5)
        await update.message.reply_text("기업명을 다시 정확하게 입력해주세요")
        return COMPANY


async def bond_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    corp_name = context.user_data["company"]
    corp_reg_no = context.user_data["corp_reg_no"]
    bond_list = get_bond_issu_info_service(corp_reg_no)

    if bond_list:
        reply_keyboard = [[bond["isinCdNm"]] for bond in bond_list]
        logger.info(reply_keyboard)
        await update.message.reply_text(
            "어떤 채권에 대해 알려드릴까요?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return BOND
    else:
        logger.info("Bond doesn't exist!")
        await update.message.reply_text(f"{corp_name}의 채권을 찾을 수 없어요 😢")
        await update.message.reply_text("다른 기업의 채권을 찾아보세요")
        return CHOOSING


async def company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    corp_name = update.message.text
    corp_code = crawl_dart_search(corp_name)
    corp_reg_no = crawl_dart_select(corp_code)

    if corp_reg_no:
        context.user_data["company"] = corp_name
        context.user_data["corp_reg_no"] = corp_reg_no

        await update.message.reply_text(f"{corp_name}의 채권에 대해 알고 싶으시군요?")
        time.sleep(0.5)
        await update.message.reply_text("채권 선택 버튼을 눌러 채권을 골라주세요", reply_markup=markup)

        logger.info("Corporation Register Number of %s: %s", corp_name, corp_reg_no)
        return CHOOSING
    else:
        await update.message.reply_text(f"{corp_name} 기업을 찾을 수 없어요 😢")
        time.sleep(0.5)
        await update.message.reply_text("기업명을 다시 정확하게 입력해주세요")

        logger.info("Corportation doesn't exist!")
        return COMPANY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    await update.message.reply_text("안녕하세요! 😆")
    time.sleep(0.5)
    await update.message.reply_text("채권 정보를 빠르고 간편하게\n알려드리는 챗봇이에요 🤖")
    time.sleep(0.5)
    await update.message.reply_text("채권 정보를 알려드리기 위해\n정확한 기업명을 알고 싶어요 🤔")
    time.sleep(0.5)
    await update.message.reply_text("기업명을 정확하게 입력해주세요")

    return COMPANY


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    TOKEN = os.environ.get("PYCON_TELE_TOKEN")
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^기업 변경$"), company),
                MessageHandler(filters.Regex("^기업 뉴스$"), news),
                MessageHandler(filters.Regex("^채권 선택$"), bond_select),
                MessageHandler(filters.Regex("^채권 상세$"), bond_info),
            ],
            COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, company)],
            BOND: [MessageHandler(filters.TEXT & ~filters.COMMAND, bond_return)],
        },
        fallbacks=[MessageHandler(filters.Regex("^종료$"), done)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    CHOOSING, COMPANY, BOND = range(3)
    reply_keyboard = [
        ["기업 변경", "채권 선택"],
        ["기업 뉴스", "채권 상세"],
        ["종료"],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    main()
