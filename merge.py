import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.util import content_type_media
import os
import string
import random

from PyPDF2 import PdfFileMerger, PdfFileReader


def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Yes", callback_data="yes"),
               InlineKeyboardButton("Generate the PDF", callback_data="no"))
    return markup


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


APITOKENPDFMERGE = os.environ.get('APITOKENPDFMERGE')
bot = telebot.TeleBot(APITOKENPDFMERGE)

filesname = []


@bot.message_handler(commands=['start'])
def send_welcome(message):

    filesname[:] = []

    bot.send_message(message.chat.id, "Send your pdf files ")


@bot.message_handler(content_types=content_type_media)
def image_handler(message):

    try:

        fileID = message.document.file_id
        file_info = bot.get_file(fileID)
        filename = get_random_string(16)
        filesname.append(filename+'.pdf')
        downloaded_file = bot.download_file(file_info.file_path)
        with open(filename+'.pdf', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(
            message.chat.id, "Do you have another pdf ?", reply_markup=gen_markup())

    except:

        bot.send_message(message.chat.id, "Send your pdf files ")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    try:
        print(call.data)

        if call.data == 'no' and len(filesname) <= 1:
            bot.send_message(call.from_user.id,
                             "Please send more than 2 pdf files ")
        elif call.data == 'no' and len(filesname) >= 2:
            mergedObject = PdfFileMerger()
            finalfile = get_random_string(16)

            # print(filesname)
            for item in filesname:
                mergedObject.append(PdfFileReader(item, 'rb'))

            mergedObject.write(finalfile+".pdf")

            mergedObject.close()

            mergedfiles = open(finalfile+".pdf", 'rb')
            bot.send_document(call.from_user.id, mergedfiles)

            mergedfiles.close()

            os.remove(finalfile+'.pdf')

            for i in filesname:
                os.remove(i)

            bot.send_message(
                call.from_user.id, "Thank you to use our bot ^_^, to use it again, send any thing")

            filesname[:] = []

        elif call.data == 'yes':
            bot.send_message(call.from_user.id, "Send your pdf file")

    except:
        bot.send_message(call.from_user.id, "Something went wrong ")


@bot.message_handler(func=lambda message: True)
def message_handler(message):
    filesname.clear()
    bot.send_message(message.chat.id, "Send your pdf files")


bot.polling()
