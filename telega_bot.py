# -*- coding: utf-8 -*-

from multiprocessing.managers import Token

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import logging
import asyncio
import nest_asyncio
import dorm
from asgiref.sync import sync_to_async
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


dorm.setup()
from game.models import ElemetsGame, BotState
 # Import our new model

nest_asyncio.apply()

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


HELP_TEXT = '''Описание игры:\nЭто описание игры \n\n 
Доступные команды:
/new - Новая игра
/help - Показать помощь по игре
'''

from typing import Dict

# Remove the global dictionary for storing state per user
# user_game_step: Dict[int, str] = {}  # user_id -> step_number

# Helper functions to get and update bot state in the database
async def get_bot_state(user_id: int) -> str:
    bot_state = await sync_to_async(BotState.objects.filter(user_id=user_id).first)()
    if not bot_state:
        bot_state = await sync_to_async(BotState.objects.create)(user_id=user_id, state='1')
    return bot_state.state

async def update_bot_state(user_id: int, state: str) -> None:
    await sync_to_async(BotState.objects.update_or_create)(user_id=user_id, defaults={'state': state})


async def button_callback(update: Update, context: CallbackContext):

    query = update.callback_query
    user_id = query.from_user.id

    # Load current step from the database
    current_step = await get_bot_state(user_id)
    game = await sync_to_async(ElemetsGame.objects.filter(name=current_step).first)()
    true_aswer = game.true_rez

    await query.answer()

    if query.data == 'btn2' and game.name == '1':
        await query.message.reply_text(
            HELP_TEXT,
        )
    elif query.data == 'btn' + str(true_aswer):
        await query.message.reply_text(
            game.itog_txt,
        )
        new_state = str(int(current_step) + 1)
        await update_bot_state(user_id, new_state)
        await game_step(update, context)
    elif query.data == 'btn_game_step':
        await update_bot_state(user_id, '2')
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
    # Set initial state for a new user/game
    await update_bot_state(user_id, "1")
    current_step = await get_bot_state(user_id)
    game = await sync_to_async(ElemetsGame.objects.filter(name=current_step).first)()
    await frame(update, context, game)


async def game_step(update: Update, context: CallbackContext):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.message.from_user.id

    current_step = await get_bot_state(user_id)
    game = await sync_to_async(ElemetsGame.objects.filter(name=current_step).first)()

    if game.true_rez == 100:
        await update_bot_state(user_id, '1')
    await frame(update, context, game)


async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        HELP_TEXT,
    )

async def new_game(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    await update_bot_state(user_id, "1")
    current_step = await get_bot_state(user_id)
    game = await sync_to_async(ElemetsGame.objects.filter(name=current_step).first)()
    await frame(update, context, game)


async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text(update.message.text)


async def main():
    try:
        Token_ = os.getenv("TOKEN")
        application = Application.builder().token(Token_).build()

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
