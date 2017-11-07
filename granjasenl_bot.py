#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from peewee import *
import re

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, ConversationHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
import logging
from uuid import uuid4
from emoji import emojize

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

#
#
# CANCEL
#
#

def cancel(bot, update):
    update.message.reply_text('OK =)')
    return ConversationHandler.END

#
#
# CERRAR
#
#

def cerrar(bot, update):
    update.message.reply_text("En desarrollo...")


#
#
# INLINE
#
#

def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    user_id = update.inline_query.from_user.id
    query = update.inline_query.query

    if query:
        q_granjas = Granja.select().where((Granja.fecha.contains(query)) & (Granja.status==1) & (Granja.id_creador==user_id))
    else:
        q_granjas = Granja.select().where((Granja.status==1) & (Granja.id_creador==user_id))

    results = list()
    for itemGranja in q_granjas:
        keyboard = [[InlineKeyboardButton(emojize("In :thumbsup:", use_aliases=True), callback_data='IN:' + str(itemGranja.id), kwargs={'granja_id': itemGranja.id}),
                    InlineKeyboardButton(emojize("Out :thumbsdown:", use_aliases=True), callback_data='OUT:' + str(itemGranja.id), kwargs={'granja_id': itemGranja.id}),
                    InlineKeyboardButton(emojize("mmm... :confused:", use_aliases=True), callback_data='MAYBE:' + str(itemGranja.id), kwargs={'granja_id': itemGranja.id})]]
#                    InlineKeyboardButton(emojize("Actualizar", use_aliases=True), callback_data='REFRESH:' + str(itemGranja.id), kwargs={'granja_id': itemGranja.id})]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        results.append(InlineQueryResultArticle(id=uuid4(), title=itemGranja.fecha + '\n' + itemGranja.lugar, input_message_content=InputTextMessageContent(itemGranja.titulo + '\nFecha: ' + itemGranja.fecha + '\nLugar de encuentro: ' + itemGranja.lugar + '\nComentarios: ' + itemGranja.comentario + get_participantes(itemGranja.id)), reply_markup=reply_markup))

    update.inline_query.answer(results, cache_time=0)


#    results = list()
#    results.append(InlineQueryResultArticle(id=uuid4(), title="Caps", input_message_content=InputTextMessageContent(query.upper())))
#    results.append(InlineQueryResultArticle(id=uuid4(), title="Bold", input_message_content=InputTextMessageContent("*%s*" % escape_markdown(query), parse_mode=ParseMode.MARKDOWN)))
#    results.append(InlineQueryResultArticle(id=uuid4(), title="Italic", input_message_content=InputTextMessageContent("_%s_" % escape_markdown(query), parse_mode=ParseMode.MARKDOWN)))


def button(bot, update):
    query = update.callback_query
    print query
    p_userid = query.from_user.id

    if not query.from_user.username:
        p_username = ''
    else:
        p_username = '@' + query.from_user.username

    p_userselection = query.data.split(':')[0]
    p_granjaid = query.data.split(':')[1]

    if p_userselection == "REFRESH":
        print "REFRESH"
        print update

#        keyboard = [[InlineKeyboardButton(emojize("In :thumbsup:", use_aliases=True), callback_data='IN:' + str(p_granjaid), kwargs={'granja_id': p_granjaid}),
#                    InlineKeyboardButton(emojize("Out :thumbsdown:", use_aliases=True), callback_data='OUT:' + str(p_granjaid), kwargs={'granja_id': p_granjaid}),
#                    InlineKeyboardButton(emojize("mmm... :confused:", use_aliases=True), callback_data='MAYBE:' + str(p_granjaid), kwargs={'granja_id': p_granjaid}),
#                    InlineKeyboardButton(emojize("Actualizar", use_aliases=True), callback_data='REFRESH:' + str(p_granjaid), kwargs={'granja_id': p_granjaid})]]
#        reply_markup = InlineKeyboardMarkup(keyboard)
#        bot.edit_message_text(text="Bla, bla, bla...", chat_id=None, message_id=update.callback_query.inline_message_id, reply_markup=reply_markup)
    else:
        if not query.from_user.first_name:
            p_userfirstname = ''
        else:
            p_userfirstname = query.from_user.first_name

        if not query.from_user.last_name:
            p_userlastname = ''
        else:
            p_userlastname = query.from_user.last_name

        print "---------------"
        print "user id        : %s" % p_userid
        print "username       : %s" % p_username
        print "user first_name: %s" % p_userfirstname
        print "user last_name : %s" % p_userlastname
        print "selection      : %s" % p_userselection
        print "granja id      : %s" % p_granjaid

        count_regs = Participantes.select().where( (Participantes.granja_id == p_granjaid) & (Participantes.user_id == p_userid) ).count()
        print "count_regs     : %s" % count_regs
        q = Participantes.insert(user_id=p_userid, granja_id=p_granjaid, user_name=p_userfirstname + ' ' + p_userlastname, user_nick=p_username, status=p_userselection)
        q.execute()

    #bot.edit_message_text(text="Selected option: {}".format(query.data), chat_id=query.message.chat_id, message_id=query.message.message_id)

#
#
# Listado de particpantes
#
#

def get_participantes(p_granja_id):
    q_participantes = Participantes.select().where(Participantes.granja_id == p_granja_id).group_by(Participantes.user_id).order_by(Participantes.id.desc())

    participantes_in = list()
    participantes_out = list()
    participantes_maybe = list()

    for participante in q_participantes:
        if participante.status == 'IN':
            participantes_in.append(participante.user_nick)

        if participante.status == 'OUT':
            participantes_out.append(participante.user_nick)

        if participante.status == 'MAYBE':
            participantes_maybe.append(participante.user_nick)

    str_in = "\n".join(participantes_in)
    str_out = "\n".join(participantes_out)
    str_maybe = "\n".join(participantes_maybe)

    str_return = "\n\nConfirmados:\n" + str_in + "\n\nNo van:\n" + str_out + "\n\nIndecisos:\n" + str_maybe
    return str_return

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

# COMANDOS - TO DO: Agregar comando para eliminar granjas pasadas
updater.dispatcher.add_handler(CommandHandler('info', info))
updater.dispatcher.add_handler(CommandHandler('cerrar', cerrar))
#updater.dispatcher.add_handler(CommandHandler('granja', granja))

updater.dispatcher.add_handler(CallbackQueryHandler(button))

# HANDLER - Para crear granja
updater.dispatcher.add_handler(conv_handler)

# HANDLER - inline_query para listar granjas disponibles
updater.dispatcher.add_handler(InlineQueryHandler(inlinequery))

# JOB QUEUE
#jobqueue = updater.job_queue
#checkpoint_queue = Job(notify_checkpoint, 10.0)
#jobqueue.put(checkpoint_queue, next_t=5.0)

updater.start_polling()
updater.idle()
