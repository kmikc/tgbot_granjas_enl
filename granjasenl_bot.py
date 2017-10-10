#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from peewee import *
from telegram.ext import Updater, CommandHandler, Job, ConversationHandler, MessageHandler, Filters
import logging

from models import Granja, Participantes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

FECHA, LUGAR, COMENTARIO = range(3)


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "%s"
                              "You can tell me more, or change your opinion on something."
                              % facts_to_str(user_data),
                              reply_markup=markup)
    return FECHA

#
#
# INFO
#
#

def info(bot, update):
    print "Info"

#
#
# GRANJA
#
#

def granja(bot, update):
    print bot
    print update
    chat_id = update.message.chat.id
    msg_str = "Granja!"
    update.message.reply_text(msg_str)


def cancel(bot, update):
    print "Cancel"
    update.message.reply_text('Cancel')
    return ConversationHandler.END

#
#
# ConversationHandler
#
#

conv_handler = ConversationHandler(
    entry_points = [CommandHandler('granja', granja)],

    states = {
        FECHA: [MessageHandler(Filters.text, received_information, pass_user_data=True)],
        LUGAR: [MessageHandler(Filters.text, received_information, pass_user_data=True)],
        COMENTARIO: [MessageHandler(Filters.text, received_information, pass_user_data=True)]
    },

    fallbacks = [CommandHandler('cancel', cancel)]
)

# TOKEN
token = open('TOKEN').read().rstrip('\n')
updater = Updater(token)

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('info', info))
#updater.dispatcher.add_handler(CommandHandler('granja', granja))

updater.dispatcher.add_handler(conv_handler)

# JOB QUEUE
#jobqueue = updater.job_queue
#checkpoint_queue = Job(notify_checkpoint, 10.0)
#jobqueue.put(checkpoint_queue, next_t=5.0)

updater.start_polling()
updater.idle()
