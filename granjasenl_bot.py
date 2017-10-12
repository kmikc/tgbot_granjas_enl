#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from peewee import *
from telegram.ext import Updater, CommandHandler, Job, ConversationHandler, MessageHandler, Filters
import logging

from models import Granja, Participantes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

FECHA, LUGAR, COMENTARIO = range(3)


#
#
# GRANJA
#
#

def granja(bot, update):
    chat_id = update.message.chat.id
    msg_str = "Organicemos la granja\nPongámosle fecha y hora"
    update.message.reply_text(msg_str)

    return FECHA


#
#
# Guarda fecha y pregunta por lugar
#
#

def save_fecha(bot, update, user_data):
    print "save_fecha"
    text = update.message.text
    user_data['fecha'] = text
    update.message.reply_text('¿Cuál será el punto de reunión?')

    return LUGAR


#
#
# Guarda lugar y pregunta por uncomentario extra
#
#

def save_lugar(bot, update, user_data):
    print "save_lugar"
    text = update.message.text
    user_data['lugar'] = text
    update.message.reply_text('¿Algún comentario extra para agregar?')

    return COMENTARIO


#
#
# Guarda comentario extra y crea registro en bd
#
#

def save_comentario(bot, update, user_data):
    print "save_comentario"
    text = update.message.text
    user_data['comentario'] = text
    update.message.reply_text('Listo!\nGuardando los datos...')

    save_granja(bot, update, user_data)


#
#
# Guarda registro de nueva granja
#
#

def save_granja(bot, update, user_data):
    print "Guardando granja..."

    p_lugar = user_data['lugar']
    p_fecha = user_data['fecha']
    p_comentario = user_data['comentario']
    p_creador = update.message.chat.id
    p_titulo = "Granja!"
    p_status = 1

    print "p_lugar: %s" % p_lugar
    print "p_fecha: %s" % p_fecha
    print "p_comentario: %s" % p_comentario
    print "p_creador: %s" % p_creador

    q = Granja.insert(titulo=p_titulo, fecha=p_fecha, lugar=p_lugar, comentario=p_comentario, id_creador=p_creador, status=p_status)
    q.execute()

    user_data.clear()
    return ConversationHandler.END

#
#
# INFO
#
#

def info(bot, update):
    print "Info"
    print update


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
        FECHA: [MessageHandler(Filters.text, save_fecha, pass_user_data=True)],
        LUGAR: [MessageHandler(Filters.text, save_lugar, pass_user_data=True)],
        COMENTARIO: [MessageHandler(Filters.text, save_comentario, pass_user_data=True)]
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
