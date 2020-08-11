#!/usr/bin/env python
import logging
import os
import yt
import subprocess

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, RegexHandler, MessageHandler, Filters
from telegram.ext import Updater


telegram_token = os.environ['TELEGRAM_TOKEN']
allowed_user = int(os.environ.get('MY_TELEGRAM_USER_ID') or 0)
youtube_url = None
formats = None


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send Youtube links my way... I will figure out")



def ask_for_formats(bot, update):
    # Make sure this is used only by myself
    user = update.message.from_user
    if allowed_user != 0 and user.id != allowed_user:
        bot.send_message(chat_id=chat_id, text="Sorry, you are not who I expected")
        return

    # Delete message sent by user to reduce clutter
    chat_id = update.message.chat_id
    bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)

    # Download format information and ask user which one to download
    global youtube_url
    global formats
    youtube_url = update.message.text
    formats = yt.pull_formats(youtube_url)

    if len(formats) > 0:
        print(formats)
        sizes_info = ' | '.join([f"{f} `{int(formats[f]['filesize'] / 1024 / 1024)}mb`" for f in formats if formats[f]['filesize'] > 0])
        bot.send_message(
            chat_id=chat_id,
            text=f'OK. I will download `{youtube_url}`.\nWhat format do you prefer? File sizes: {sizes_info}',
            parse_mode='markdown',
            reply_markup=ReplyKeyboardMarkup(
                [formats.keys()],
                one_time_keyboard=True))
    else:
        # If we failed to get the formats, just download the default
        proceed_with_download(bot, update)



def proceed_with_download(bot, update):
    global youtube_url
    global formats
    chat_id = update.message.chat_id
    format_chosen = update.message.text

    if youtube_url is None:
        bot.send_message(
            chat_id=chat_id,
            text='Hmm I do not remember asking you anything')
        return

    bot.send_message(
        chat_id=chat_id,
        text='All right. Hang up tight. This might take a while')
    try:
        print(f'Download {youtube_url} with {formats.get(format_chosen)}')
        format_id = formats.get(format_chosen)['format_id'] if format_chosen in formats else None
        caption, file_path = yt.download_video(youtube_url, format_id)
        caption = f'{caption} -- `{youtube_url}`'
        with open(file_path, 'rb') as f:
            logging.info('Uploading video to Telegram...')
            bot.send_video(chat_id, video=f, caption=caption, parse_mode='markdown', timeout=1200)

        # remove video file when done
        os.remove(file_path)
    except Exception as e:
        logging.exception("Failed to download/upload video")
        bot.send_message(
            chat_id=chat_id,
            text=f'I failed you... {e}')

    # clean global vars
    youtube_url = None
    formats = None



def error_callback(bot, update, error):
    logging.error('An error happened: %s update: %s', error, update)



def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater = Updater(token=telegram_token)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(RegexHandler('https://:*', ask_for_formats))
    dispatcher.add_handler(RegexHandler('240p|360p|480p|720p|1080p', proceed_with_download))
    dispatcher.add_error_handler(error_callback)

    # Start polling
    updater.start_polling()
    logging.info("Started polling...")



if __name__ == "__main__":
    main()
