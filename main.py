import os
import json
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
from db import *
from crawl import *


def krx_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered KRX bond info."""

    facts = [
        f"채권명: {user_data['ISU_ABBRV']}",
        f"채권유형: {user_data['BND_TP_NM']}",
        f"선후순위구분: {user_data['DEBT_REPAY_RANK_TP_NM']}",
        f"발행금액: {user_data['ISU_AMT']}원",
        f"발행일: {user_data['ISU_DD']}",
        f"상환일: {user_data['REDMPT_DD']}",
        f"표면이율: {user_data['COUPN_RT']}%",
    ]
    if user_data["BYINST_CREDIT_VALU_GRD1"]:
        facts.append(f"신용평가_나이스: {user_data['BYINST_CREDIT_VALU_GRD1']}")
    if user_data["BYINST_CREDIT_VALU_GRD2"]:
        facts.append(f"신용평가_한신평: {user_data['BYINST_CREDIT_VALU_GRD2']}")
    if user_data["BYINST_CREDIT_VALU_GRD3"]:
        facts.append(f"신용평가_한기평: {user_data['BYINST_CREDIT_VALU_GRD3']}")
    if user_data["BYINST_CREDIT_VALU_GRD4"]:
        facts.append(f"신용평가_서신정: {user_data['BYINST_CREDIT_VALU_GRD4']}")
    if user_data["CALL_EXER_STRT_DD1"]:
        facts.append(f"1차 CALL옵션행사개시일: {user_data['CALL_EXER_STRT_DD1']}")
    if user_data["CALL_EXER_STRT_DD2"]:
        facts.append(f"2차 CALL옵션행사개시일: {user_data['CALL_EXER_STRT_DD2']}")
    return "\n".join(facts).join(["\n", "\n"])


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    await update.message.reply_text("✔ 기능 설명")
    time.sleep(0.5)
    await update.message.reply_text(reply_dict["help_function"])
    time.sleep(0.5)
    await update.message.reply_text("✔ 명령어 설명")
    time.sleep(0.5)
    await update.message.reply_text(reply_dict["help_command"])


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete information input by user and end the conversation."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    user_data = context.user_data
    if "company" in user_data:
        del user_data["company"]

    if "corp_reg_no" in user_data:
        del user_data["corp_reg_no"]

    await update.message.reply_text(
        reply_dict["done_bye"],
        reply_markup=ReplyKeyboardMarkup([["/start"]], one_time_keyboard=True),
    )

    user_data.clear()
    return ConversationHandler.END


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the news of company input by user."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    corp_name = context.user_data["company"]
    news_links = crawl_news(corp_name)
    for news_link in news_links:
        await update.message.reply_text(news_link)
        time.sleep(0.5)
    await update.message.reply_text(reply_dict["choosing_guide"], reply_markup=markup)

    return CHOOSING


async def bond_return(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the information of bond selected by user."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    corp_name = context.user_data["company"]
    bond_name = update.message.text
    bond_info = read_bond_info(corp_name, bond_name)
    bond_code = bond_info["isinCd"]
    krx_bond_info = crawl_krx(bond_code, bond_name)
    await update.message.reply_text(f"{krx_to_str(krx_bond_info)}")
    time.sleep(0.5)
    await update.message.reply_text(reply_dict["choosing_guide"], reply_markup=markup)

    return CHOOSING


async def bond_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the list of bonds of company input by user."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    corp_name = context.user_data["company"]
    corp_reg_no = context.user_data["corp_reg_no"]

    from_api = False
    if bond_list := read_bond_list(corp_name):
        reply_keyboard = [[bond] for bond in bond_list]

    elif bond_list := get_bond_issu_info_service(corp_reg_no):
        reply_keyboard = []
        for bond in bond_list:
            reply_keyboard.append([bond["isinCdNm"]])
            bond["bondIsurNm"] = corp_name
        from_api = True

    else:
        await update.message.reply_text(
            reply_dict["bond_select_no_1"].format(corp_name)
        )
        time.sleep(0.5)
        await update.message.reply_text(
            reply_dict["bond_select_no_2"], reply_markup=markup
        )

        return CHOOSING

    await update.message.reply_text(
        reply_dict["bond_select_ok_1"],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    if from_api:
        write_db(bond_list)

    return BOND


async def change_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """The function of changing company."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    await update.message.reply_text(reply_dict["change_1"])
    time.sleep(0.5)
    await update.message.reply_text(
        reply_dict["change_2"], reply_markup=ReplyKeyboardRemove()
    )

    return COMPANY


async def company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the function of chat bot if company name exists, else reask for the name of company."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    corp_name = update.message.text
    corp_code = crawl_dart_search(corp_name)
    corp_reg_no = crawl_dart_select(corp_code)

    if corp_reg_no:
        context.user_data["company"] = corp_name
        context.user_data["corp_reg_no"] = corp_reg_no
        await update.message.reply_text(reply_dict["company_ok_1"].format(corp_name))
        time.sleep(0.5)
        await update.message.reply_text(
            reply_dict["company_ok_2"].format(corp_name), reply_markup=markup
        )
        return CHOOSING
    else:
        await update.message.reply_text(reply_dict["company_no_1"].format(corp_name))
        time.sleep(0.5)
        await update.message.reply_text(reply_dict["company_no_2"])
        return COMPANY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for company name."""
    with open("./reply.json", "r") as reply_json:
        reply_dict = json.load(reply_json)

    await update.message.reply_text(reply_dict["start_1"])
    time.sleep(0.5)
    await update.message.reply_text(reply_dict["start_2"])
    time.sleep(0.5)
    await update.message.reply_text(reply_dict["start_3"])
    time.sleep(0.5)
    await update.message.reply_text(
        reply_dict["start_4"], reply_markup=ReplyKeyboardRemove()
    )
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
                MessageHandler(filters.Regex("^기업 뉴스$"), news),
                MessageHandler(filters.Regex("^기업 변경$"), change_company),
                MessageHandler(filters.Regex("^채권 선택$"), bond_select),
            ],
            COMPANY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, company),
            ],
            BOND: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, bond_return),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^대화 종료$"), done),
        ],
    )

    # Add application handler with start, quit, help and conversation handler
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quit", done))
    application.add_handler(CommandHandler("help", help))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    CHOOSING, COMPANY, BOND = range(3)
    reply_keyboard = [
        ["기업 뉴스", "채권 선택"],
        ["기업 변경", "대화 종료"],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    main()
