# -*- coding: utf-8 -*-

from multiprocessing.managers import Token

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import logging
import asyncio
import nest_asyncio
import dorm
from asgiref.sync import sync_to_async

dorm.setup()
from game.models import ElemetsGame

nest_asyncio.apply()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


HELP_TEXT = '''Описание игры:\nЭто описание игры \n\n 
Доступные команды:
/new - Новая игра
/help - Показать помощь по игре
'''

from typing import Dict

# Add after the logger initialization
user_game_step: Dict[int, str] = {}  # user_id -> step_number

async def button_callback(update: Update, context: CallbackContext):

    query = update.callback_query
    user_id = query.from_user.id

    # Get current step or set to 0 if not exists
    current_step = user_game_step.get(user_id, 0)
    game = await sync_to_async(ElemetsGame.objects.filter(name=current_step).first)()
    true_aswer = game.true_rez

    await query.answer()

    if query.data == 'btn2' and game.name == '1':

        await query.message.reply_text(
            HELP_TEXT,
        )
    elif query.data == 'btn'+str(true_aswer) :
        await query.message.reply_text(
            game.itog_txt,
        )
        user_game_step[user_id] = str(int(current_step) + 1)
        await game_step(update, context)
    elif query.data == 'btn_game_step':
        user_game_step[user_id] = '2'
        await game_step(update, context)
    else:
        await query.message.reply_text(
            "Неправильно. Попробуй еще раз.",
        )
        await game_step(update, context)


async def frame(update: Update, context: CallbackContext, game):

    btns_text = game.button_text.split(',')
    keyboard = []

    for ind, el in enumerate(btns_text, 1):
        if (game.name == '1' or game.true_rez == 100) and ind == 1:
            keyboard.append([InlineKeyboardButton(el, callback_data='btn_game_step')])
        else:
            keyboard.append([InlineKeyboardButton(el, callback_data=f'btn{ind}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Using a reliable image URL
    # img_url = 'img/telegram-bot.png'
    img_url = str(game.image)

    with open(img_url, 'rb') as photo:
        # Check if the update is from a callback query or a message
        if update.callback_query:
            await update.callback_query.message.reply_photo(
                photo=photo,
                caption=game.description,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_photo(
                photo=photo,
                caption=game.description,
                reply_markup=reply_markup
            )




async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_game_step[user_id] = "1"
    game = await sync_to_async(ElemetsGame.objects.first)()

    await frame(update, context, game)

async def game_step(update: Update, context: CallbackContext):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.message.from_user.id

    current_step = user_game_step.get(user_id, 0)
    game = await sync_to_async(ElemetsGame.objects.filter(name=current_step).first)()
    print(current_step)
    if game.true_rez == 100:
        user_game_step[user_id] = '1'
    await frame(update, context, game)


async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        HELP_TEXT,
    )

async def new_game(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_game_step[user_id] = "1"
    game = await sync_to_async(ElemetsGame.objects.first)()
    await frame(update, context, game)

async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)

async def main():
    try:
        Token = ""
        application = Application.builder().token(Token).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("new", new_game))
        application.add_handler(CommandHandler("game_step", game_step))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        application.add_handler(CallbackQueryHandler(button_callback))

        await application.run_polling()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == '__main__':

    asyncio.run(main())