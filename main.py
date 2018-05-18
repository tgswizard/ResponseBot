# -*- coding: utf-8 -*-
from telegram import Bot
from telegram.ext import Updater, Dispatcher, MessageHandler, CommandHandler, Filters, ConversationHandler
import sys
import os
import config
import pickle
import logging
NEW_MESSAGE = "NEW_MESSAGE"
NEW_KEYWORD = "NEW_KEYWORD"
LINK_MESSAGE= "LINK_MESSAGE"


def message_received(bot,update):
    msg = update.message.text
    if "$" in msg:
        return
    try:
        KEY_WORDS = pickle.load(open("key_words.p", "rb"))
    except FileNotFoundError:
        KEY_WORDS = []
    try:
        MESSAGES = pickle.load(open("messages.p", "rb"))
    except FileNotFoundError:
        MESSAGES = []
    if update.message.from_user.is_bot is True:
        return

    for keyword in KEY_WORDS:
        if keyword is None:
            continue
        if keyword in msg:
            for message in MESSAGES:
                try:
                    if message[0] == keyword:
                        update.message.reply_text(message[1])
                except IndexError:
                    continue


def add_keyword(bot,update):
    if update.message.from_user.id in config.ADMINS:
        update.message.reply_text("אנא כתוב את המילת מפתח אותה אתה רוצה להוסיף.")
        return NEW_KEYWORD


def add_message(bot,update):
    if update.message.from_user.id in config.ADMINS:
        update.message.reply_text("אנא כתוב את ההודעה אותה אתה רוצה להוסיף.")
        return NEW_MESSAGE


def message_add_op(bot,update,user_data):
    msg = update.message.text
    user_data["msg"] = msg
    update.message.reply_text("כתוב את מילת המפתח אליה אתה רוצה לקשר את ההודעה")
    return LINK_MESSAGE


def keyword_add_op(bot,update):
    msg = update.message.text
    KEY_WORDS = pickle.load(open("key_words.p", "rb"))
    if msg in KEY_WORDS:
        update.message.reply_text("המילה כבר מילת מפתח!")
        return ConversationHandler.END

    KEY_WORDS.append(msg)
    pickle.dump(KEY_WORDS, open("key_words.p", "wb"))
    update.message.reply_text("המילת מפתח נוספה")
    return ConversationHandler.END


def link_message_op(bot,update,user_data):
    keyword = update.message.text
    msg = user_data["msg"]
    MESSAGES = pickle.load(open("messages.p", "rb"))
    for i in range(0,len(MESSAGES)):
        try:
            if keyword in message[0]:
                message = [message[0],msg]
                MESSAGES[i] = message
                pickle.dump(MESSAGES, open("messages.p", "wb"))
                update.message.reply_text("ההודעה נוספה")
                return ConversationHandler.END
        except IndexError:
            continue
    MESSAGES.append([keyword,msg])
    pickle.dump(MESSAGES, open("messages.p", "wb"))
    update.message.reply_text("ההודעה נוספה")
    return ConversationHandler.END


conv_handler = ConversationHandler(entry_points=[CommandHandler(command="/newmessage", callback=add_message),
                                                 CommandHandler(command="/newkeyword", callback=add_keyword)],
                                   states={
                                       NEW_MESSAGE : [MessageHandler(callback=message_add_op,
                                                                                    filters=Filters.text,pass_user_data=True)],
                                       NEW_KEYWORD: [MessageHandler(callback=keyword_add_op,
                                                                                   filters=Filters.text)],
                                       LINK_MESSAGE : [MessageHandler(callback=link_message_op,filters=Filters.text,pass_user_data=True)]},
                                   fallbacks=[])
def main():

    updater = Updater(config.TOKEN)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(callback=message_received, filters=Filters.group))
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

# Add logging to file to be able to debug more easily
# Add signal handler to change logging level / Reload config.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    main()
