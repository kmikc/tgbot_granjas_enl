#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from peewee import *
import re

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, CommandHandler, Job, ConversationHandler, MessageHandler, Filters, InlineQueryHandler
import logging
from uuid import uuid4

from models import Granja, Participantes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

FECHA, LUGAR, COMENTARIO = range(3)


#
#
# GRANJA
#
#

def granja(bot, update, user_data):
    user_id = update.message.from_user.id
    user_data['id_creador'] = user_id
    msg_str = "Organicemos la granja\nPongámosle fecha y hora"
    update.message.reply_text(msg_str)

    print user_data

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

    print user_data

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

    print user_data

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
    update.message.reply_text('Guardando los datos...')

    print user_data

    save_granja(bot, update, user_data)

    update.message.reply_text('Listo!\nEl siguiente paso es publicarla en un grupo o canal.\nEscribiendo @granjas_enl_bot y buscando en el listado de granjas disponibles.')
    return ConversationHandler.END


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
    p_creador = user_data['id_creador']
    p_titulo = "Granja!"
    p_status = 1

    print "p_lugar: %s" % p_lugar
    print "p_fecha: %s" % p_fecha
    print "p_comentario: %s" % p_comentario
    print "p_creador: %s" % p_creador

    q = Granja.insert(titulo=p_titulo, fecha=p_fecha, lugar=p_lugar, comentario=p_comentario, id_creador=p_creador, status=p_status)
    q.execute()

    user_data.clear()


#
#
# INFO
#
#

def info(bot, update):
    print "Info"
    print update


def cancel(bot, update):
    update.message.reply_text('OK =)')
    return ConversationHandler.END






def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    query = update.inline_query.query

    results = list()

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Caps",
                                            input_message_content=InputTextMessageContent(
                                                query.upper())))

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Bold",
                                            input_message_content=InputTextMessageContent(
                                                "*%s*" % escape_markdown(query),
                                                parse_mode=ParseMode.MARKDOWN)))

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Italic",
                                            input_message_content=InputTextMessageContent(
                                                "_%s_" % escape_markdown(query),
                                                parse_mode=ParseMode.MARKDOWN)))

    update.inline_query.answer(results)


#
#
# ConversationHandler
#
#

conv_handler = ConversationHandler(
    entry_points = [CommandHandler('granja', granja, pass_user_data=True)],

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

updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))

# JOB QUEUE
#jobqueue = updater.job_queue
#checkpoint_queue = Job(notify_checkpoint, 10.0)
#jobqueue.put(checkpoint_queue, next_t=5.0)

updater.start_polling()
updater.idle()
