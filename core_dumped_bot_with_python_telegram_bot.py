#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import re

import telegram
import network_scan as scan
import datetime
import time
import os
from logger import get_logger
from data_loader import DataLoader
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter, RegexHandler
from random import normalvariate
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

reload(sys)
sys.setdefaultencoding('utf8')


def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        logger.exception("remove update.message.chat_id from conversation list")
    except BadRequest:
        logger.exception("handle malformed requests - read more below!")
    except TimedOut:
        logger.exception("handle slow connection problems")
    except NetworkError:
        logger.exception("handle other connection problems")
    except ChatMigrated as e:
        logger.exception("the chat_id of a group has changed, use " + e.new_chat_id + " instead")
    except TelegramError:
        logger.exception("There is some error with Telegram")


class LaughFilter(BaseFilter):
    def filter(self, message):
        lower_message = str(message.text).lower()
        if ('hahaha' in lower_message) or ('jajaja' in lower_message):
            return True
        else:
            return False


class PlayaFilter(BaseFilter):
    def filter(self, message):
        lower_message = str(message.text).lower()
        if ('primera linea de playa' in lower_message) or ('primera línea de playa' in lower_message):
            return True
        else:
            return False


def load_settings():
    global settings
    global last_function_calls
    settings = DataLoader()
    last_function_calls = {}


def is_member(bot, user_id):
    try:
        return bot.get_chat_member(chat_id=settings.admin_chatid,
                                   user_id=user_id).status in ['creator', 'administrator', 'member']
    except BadRequest:
        return False


def is_call_available(name, chat_id, cooldown):
    global last_function_calls
    now = datetime.datetime.now()
    cooldown_time = datetime.datetime.now() - datetime.timedelta(minutes=cooldown)
    if name in last_function_calls.keys():
        if chat_id in last_function_calls[name].keys():
            if last_function_calls[name][chat_id] > cooldown_time:
                last_function_calls[name][chat_id] = now
                return False
            else:
                last_function_calls[name][chat_id] = now
                return True
        else:
            last_function_calls[name] = {chat_id: now}
            return True
    else:
        last_function_calls[name] = {chat_id: now}
        return True


def help(bot, update):
    log_message(update)
    bot.sendMessage(update.message.chat_id, settings.help_string, parse_mode=telegram.ParseMode.MARKDOWN)


def ask(bot, update):
    log_message(update)
    bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
    selected_string = settings.answers[random.randint(0, int(len(settings.answers) - 1))]
    human_texting(selected_string)
    bot.sendMessage(update.message.chat_id, selected_string, parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_to_message_id=update.message.message_id)


def take_rtsp_screenshot(cam_id):
    os.system('rm ' + settings.pictures_directory + '/snapshot.jpg')
    os.system(
        'ffmpeg -i \"' + settings.cam_url(
            cam_id) + '\" -vf "transpose=2,transpose=2" -y -f image2  -frames 1 ' + settings.pictures_directory + '/snapshot.jpg')


def foto(bot, update):
    log_message(update)
    teclado_fotos = [['/fotonova'], ['/fotocore']]
    reply_markup = telegram.ReplyKeyboardMarkup(teclado_fotos)
    bot.send_message(chat_id=update.message.chat_id,
                     text="¿Qué foto quieres?",
                     reply_markup=reply_markup,
                     reply_to_message_id=update.message.message_id)


def log_message(update):
    logger.info("He recibido: \"" + update.message.text + "\" de " + update.message.from_user.username + " [ID: " + str(
        update.message.chat_id) + "]")


def fotonova(bot, update):
    log_message(update)

    if update.message.chat_id == settings.admin_chatid or update.message.chat_id == settings.president_chatid:
        bot.send_chat_action(chat_id=update.message.chat_id, action='upload_photo')
        take_rtsp_screenshot(0)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.sendPhoto(chat_id=update.message.chat_id,
                      photo=open(settings.pictures_directory + '/snapshot.jpg', 'rb'), reply_markup=reply_markup)
        logger.debug(settings.pictures_directory + '/snapshot.jpg')


def fotocore(bot, update):
    log_message(update)
    if update.message.chat_id == settings.admin_chatid or update.message.chat_id == settings.president_chatid or update.message.chat_id == settings.admin_group_chat_id:
        bot.send_chat_action(chat_id=update.message.chat_id, action='upload_photo')
        take_rtsp_screenshot(1)
        reply_markup = telegram.ReplyKeyboardRemove()
        bot.sendPhoto(chat_id=update.message.chat_id,
                      photo=open(settings.pictures_directory + '/snapshot.jpg', 'rb'), reply_markup=reply_markup)
        logger.debug(settings.pictures_directory + 'snapshot.jpg')


def alguien(bot, update):
    logger.info("He recibido petición /alguien")
    if is_call_available("alguien", update.message.chat_id, 15):
        logger.info("Realizando escaneo")
        bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        bot.sendMessage(update.message.chat_id,
                        scan.scan_for_people_in_network()[
                            0] + "\n`No podrás hacer otro /alguien hasta dentro de 15 minutos`.",
                        parse_mode="Markdown")
    else:
        bot.deleteMessage(update.message.message_id)


def human_texting(string):
    wait_time = len(string) * normalvariate(0.1, 0.05)
    if wait_time > 8:
        wait_time = 8
    time.sleep(wait_time)


def jokes(bot, update):
    chat_id = update.message.chat.id
    if is_call_available("joke", chat_id, 30):
        bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        selected_joke = settings.jokes[random.randint(0, int(len(settings.jokes) - 1))]
        human_texting(selected_joke)
        bot.sendMessage(update.message.chat_id, selected_joke,
                        reply_to_message_id=update.message.message_id)


def reload_data(bot, update):
    if update.message.from_user.id == settings.president_chatid:
        load_settings()
        bot.send_message(chat_id=update.message.chat_id, text="Datos cargados")


def playa(bot, update):
    if is_call_available("playa", update.message.chat.id, 10):
        bot.sendSticker(update.message.chat_id, u'CAADBAADyAADD2LqAAEgnSqFgod7ggI')


def the_game(bot, update):
    log_message(update)
    if is_call_available("the_game", update.message.chat.id, 30):
        bot.send_chat_action(chat_id=update.message.chat_id, action='typing')
        selected_game = settings.the_game[random.randint(0, int(len(settings.the_game) - 1))]
        human_texting(selected_game)
        bot.sendMessage(update.message.chat_id, selected_game,
                        reply_to_message_id=update.message.message_id)


def name_changer(bot, job):
    logger.info("Starting scheduled network scan.")
    try:
        if scan.is_someone_there():
            bot.setChatTitle(settings.public_chatid, u">CORE DUMPED_: \U00002705 Abierto")
            logger.info("Hay alguien.")
        else:
            bot.setChatTitle(settings.public_chatid, u">CORE DUMPED_")
            logger.info("No hay nadie.")
    except:
        logger.exception("Error al actualizar el nombre del grupo Core Dumped.")


if __name__ == "__main__":
    print("Core Dumped Bot: Starting...")

    logger = get_logger("bot_starter", True)
    load_settings()

    try:
        logger.info("Conectando con la API de Telegram.")
        updater = Updater(settings.telegram_token)
        dispatcher = updater.dispatcher
        the_game_regex = re.compile(r".*(\b(perdido|game)\b)", re.I | re.U | re.M)
        dispatcher.add_handler(RegexHandler(the_game_regex, the_game))
        dispatcher.add_handler(CommandHandler('help', help))
        dispatcher.add_handler(CommandHandler('ask', ask))
        dispatcher.add_handler(CommandHandler('foto', foto))
        dispatcher.add_handler(CommandHandler('fotonova', fotonova))
        dispatcher.add_handler(CommandHandler('fotocore', fotocore))
        dispatcher.add_handler(CommandHandler('alguien', alguien))
        dispatcher.add_handler(CommandHandler('reload', reload_data))
        joke_filter = LaughFilter()
        dispatcher.add_handler(MessageHandler(joke_filter, jokes))
        # Inside joke
        playa_filter = PlayaFilter()
        dispatcher.add_handler(MessageHandler(playa_filter, playa))
        dispatcher.add_error_handler(error_callback)
    except Exception as ex:
        logger.exception("Error al conectar con la API de Telegram.")
        quit()
    try:
        jobs = updater.job_queue
        job_name_changer = jobs.run_repeating(name_changer, 30 * 60, 300)
        logger.info("Iniciando jobs")
    except Exception as ex:
        logger.exception("Error al cargar la job list. Ignorando jobs...")
    updater.start_polling()
    logger.info("Core Dumped Bot: Estoy escuchando.")
    updater.idle()
