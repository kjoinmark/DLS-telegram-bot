#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a bot using decorators and webhook with aiohttp
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import ssl

from aiohttp import web

import telebot

API_TOKEN = '5592278771:AAHjv-KggUzfHsBRpktcX5Lwd9K4VTnMJ4Q' # put here our telegram api token

WEBHOOK_HOST = 'https://ef-telegram-bot.herokuapp.com/'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = '/home/matrs011/ssl_key/url_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = '/home/matrs011/ssl_key/url_private.key'  # Path to the ssl private key

WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.AsyncTeleBot(API_TOKEN)

app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)


import tensorflow as tf
import IPython.display as display

import numpy as np
import PIL.Image
import time
import functools

import tensorflow_hub as hub
hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/1')

def tensor_to_image(tensor):
  tensor = tensor*255
  tensor = np.array(tensor, dtype=np.uint8)
  if np.ndim(tensor)>3:
    assert tensor.shape[0] == 1
    tensor = tensor[0]
  return PIL.Image.fromarray(tensor)

def load_img(path_to_img):
  max_dim = 512
  img = tf.io.read_file(path_to_img)
  img = tf.image.decode_image(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.float32)

  shape = tf.cast(tf.shape(img)[:-1], tf.float32)
  long_dim = max(shape)
  scale = max_dim / long_dim

  new_shape = tf.cast(shape * scale, tf.int32)

  img = tf.image.resize(img, new_shape)
  img = img[tf.newaxis, :]
  return img

def model(content_path, dict_users, chat_id):
    content_image = load_img(content_path)
    style_image = load_img(dict_users[chat_id][1])
    stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    final_image = tensor_to_image(stylized_image)
    final_path = str(chat_id) + 'final_image.png'
    final_image.save(final_path, 'PNG')
    return final_path
# dictionary where the key is chat_id, an element is a list ['style_path', 0 if bot has a style_photo else 0]
dict_users = {}
'''
in all functions used 'try' to avoid ConnectionError after some time bot is not used
'''
# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    chat_id = message.chat.id
    if not chat_id in dict_users.keys():
        dict_users[chat_id] = [0,'']
    try:
        bot.send_message(message.chat.id,
                     ("Hi there, I am Style-transfer-Bot.\n"
                      "I'll transform your photos by changing the style."))
        bot.send_message(message.chat.id,
                    ("First send me a photo with example of the style,\n"
                    "then send a photo you'd like to transform."))
    except:
        bot.send_message(message.chat.id,
                    ("Hi there, I am Style-transfer-Bot.\n"
                    "I'll transform your photos by changing the style."))
        bot.send_message(message.chat.id,
                    ("First send me a photo with example of the style,\n"
                    "then send a photo you'd like to transform."))
# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def default_message(message):
    chat_id = message.chat.id
    if not chat_id in dict_users.keys():
        dict_users[chat_id] = [0,'']
    try:
        bot.send_message(message.chat.id, ("OK, let's start.\n"
                                            "Waiting for your photos."))
    except:
        bot.send_message(message.chat.id, ("OK, let's start.\n"
                                            "Waiting for your photos."))
    print(dict_users)
@bot.message_handler(content_types=['photo'])
def getting_photo(message):
    global ind, style_path, content_path
    try:
        chat_id = message.chat.id
        if not chat_id in dict_users.keys():
            dict_users[chat_id] = [0,'']
        # getting style_photo
        if dict_users[chat_id][0] == 0:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()
            style_path = '/home/matrs011/files/' + str(chat_id) + 'style_im.jpg'
            dict_users[chat_id][1] = style_path
            with open(style_path, 'wb') as new_file:
            	new_file.write(downloaded_file)
            bot.send_message(chat_id, "I've got the style_photo.\n"
                                        "Send a photo you'd like to transform.")
            dict_users[chat_id][0] += 1

        # getting content_photo and processing
        elif dict_users[chat_id][0] == 1:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()
            content_path = '/home/matrs011/files/' + str(chat_id) + 'content_im.jpg'
            with open(content_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(chat_id, "OK. Here is a style_transfered photo:")
            dict_users[chat_id][0] = 0

            final_path = model(content_path, dict_users, chat_id)
            photo = open(final_path, 'rb')
            bot.send_photo(chat_id, photo).wait()
            photo.close()


        else:
            bot.send_message(chat_id, "!!!something wrong with ind_variable!!!")

    except:
        chat_id = message.chat.id
        if not chat_id in dict_users.keys():
            dict_users[chat_id] = [0,'']
        if dict_users[chat_id][0] == 0:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()
            style_path = '/home/matrs011/files/' + str(chat_id) + 'style_im.jpg'
            dict_users[chat_id][1] = style_path
            with open(style_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(chat_id, "I've got the style_photo.\n"
                                        "Send a photo you'd like to transform.")
            dict_users[chat_id][0] = 1

        elif dict_users[chat_id][0] == 1:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file_info = file_info.wait()
            downloaded_file = bot.download_file(file_info.file_path)
            downloaded_file = downloaded_file.wait()
            content_path = '/home/matrs011/files/' + str(chat_id) + 'content_im.jpg'
            with open(content_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(chat_id, "OK. Here is a style_transfered photo:")
            dict_users[chat_id][0] = 0

            final_path = model(content_path, dict_users, chat_id)
            photo = open(final_path, 'rb')
            bot.send_photo(chat_id, photo).wait()
            photo.close()

        else:
            bot.send_message(chat_id, "!!!something wrong with ind_variable!!!")

# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# Start aiohttp server
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
