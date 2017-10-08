#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from peewee import *
from telegram.ext import Updater, CommandHandler, Job
import logging

from models import Granja, Participantes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def info(bot, update):
    print "Info"


# TOKEN
token = open('TOKEN').read().rstrip('\n')
updater = Updater(token)

# COMANDOS
updater.dispatcher.add_handler(CommandHandler('info', info))

# JOB QUEUE
#jobqueue = updater.job_queue
#checkpoint_queue = Job(notify_checkpoint, 10.0)
#jobqueue.put(checkpoint_queue, next_t=5.0)

updater.start_polling()
updater.idle()
