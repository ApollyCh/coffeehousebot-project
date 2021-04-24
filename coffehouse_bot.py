from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CommandHandler

from data import db_session
from data.reservations import Reservation
from data.comments import Comments

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

TOKEN = '1721652183:AAG5alennFducMBxBc5VeWZ1sICP2DS4W5s'
EMAIL = 'coffehouseproject@mail.ru'
PASSWORD = 'polly888'

reply_keyboard = [['/make_a_reservation', '/make_a_preorder'],
                  ['/rate', '/information']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# основные команды /start и /help
def start(update, context):
    update.message.reply_text(
        'Hello! My name is Levi and I will help you to make a decision: ',
        reply_markup=markup
    )


help_kb = [['/start']]
hlp = ReplyKeyboardMarkup(help_kb, one_time_keyboard=True)


def help(update, context):
    update.message.reply_text(
        'You can find more information on our web-site \n'
        'Working time: 9.00 a.m - 8.00 p.m \n'
        'Adress: St. Wonderful 43', reply_markup=hlp)


# ЗАКАЗАТЬ СТОЛИК!!!
NAME, NUMBER, TIME, PEOPLE, BACK = range(5)


def reservation_start(update, context):
    update.message.reply_text(
        'If you want to make a reservation, send your name and surname')
    return NAME


def number(update, context):
    context.user_data['name'] = update.message.text
    update.message.reply_text(
        'Send your phone number')
    return NUMBER


def datetime(update, context):
    context.user_data['number'] = update.message.text
    update.message.reply_text(
        'Send date and time, what you want')
    return TIME


def people(update, context):
    context.user_data['time'] = update.message.text
    update.message.reply_text(
        'Send number of people')
    return PEOPLE


def final_reservation(update, context):
    global EMAIL, PASSWORD
    context.user_data['number of people'] = update.message.text
    update.message.reply_text(
        f'Name: {context.user_data["name"]}\n'
        f'Telephone number: {context.user_data["number"]}\n'
        f'Time: {context.user_data["time"]}\n'
        f'Thank you for the reservation. Manager will call you soon\n'
        f'Print /start to see start message')

    msg = f'New reservation {context.user_data["time"]}'

    body = f'Name: {context.user_data["name"]}\nTelephone number: {context.user_data["number"]}' \
           f'\nTime: {context.user_data["time"]}\n'

    email_push(msg, body)

    res = Reservation()
    res.name = context.user_data['name']
    res.number_of_people = context.user_data['number of people']
    res.phonenumber = context.user_data['number']
    res.date_time = context.user_data['time']

    db_sess = db_session.create_session()

    db_sess.add(res)
    db_sess.commit()

    return ConversationHandler.END


DECISION, YES_DISHES, NO_DISHES, PRE_TIME, PRE_NUMBER = range(5)


# СДЕЛАТЬ ПРЕДЗАКАЗ ЕДЫ!!!
def preorder_start(update, context):
    update.message.reply_text('Do You know what You want to choose?\n'
                              '1 - Yes\n'
                              '0 - No')
    return DECISION


def decision(update, context):
    if update.message.text == '1':
        update.message.reply_text('Specify the dishes You want to order')
        return YES_DISHES
    elif update.message.text == '0':
        update.message.reply_text('You can view the menu on the website www.coffeehouse.com\n'
                                  'Print /start to see start message')
        return ConversationHandler.END


def preorder_time(update, context):
    context.user_data['dishes'] = update.message.text
    update.message.reply_text('What time should we expect You?')
    return PRE_TIME


def pre_number(update, context):
    context.user_data['time'] = update.message.text
    update.message.reply_text('Send your phone number')
    return PRE_NUMBER


def final_preorder(update, context):
    context.user_data['number'] = update.message.text
    update.message.reply_text(
        f'Dishes: {context.user_data["dishes"]}\n'
        f'Phone number: {context.user_data["number"]}\n'
        f'Time: {context.user_data["time"]}\n'
        f'Thank you for the pre-order. Manager will call you soon\n'
        f'Print /start to see start message')

    msg = f'New pre-order {context.user_data["time"]}'

    body = f'Dishes: {context.user_data["dishes"]}\nPhone number: {context.user_data["number"]}\n' \
           f'Time: {context.user_data["time"]}\n'
    email_push(msg, body)

    return ConversationHandler.END


# Отправка сообщений на почту администратору
def email_push(message, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    msg['Subject'] = message
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.mail.ru', 587)
    # server.set_debuglevel(True)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    server.quit()


RATING, POINT, LOW, GOOD, HIGH = range(5)


# ОЦЕНИВАНИЕ КАФЕ
def start_rating(update, context):
    update.message.reply_text('Please sent your order number')
    return RATING


def rating(update, context):
    context.user_data['order number'] = update.message.text
    update.message.reply_text('Please, rate our cafe from 0 to 5, where 0 is "terrible" and 5 is "great"')
    return POINT


def answer_rating(update, context):
    context.user_data['rating'] = update.message.text

    if update.message.text == '0' or update.message.text == '1':
        update.message.reply_text('We are sorry that you have such an opinion.'
                                  '\nTell us why you give such a low rating?')
        return LOW
    elif update.message.text == '2' or update.message.text == '3':
        update.message.reply_text('Not so bad!'
                                  '\nTell us what prevented you from giving a higher rating?')
        return GOOD
    elif update.message.text == '4' or update.message.text == '5':
        update.message.reply_text('Thank you for your high rating!'
                                  '\nWe will be happy if you leave some review')
        return HIGH


def final_rating_low(update, context):
    update.message.reply_text("We understand your wishes.\nIt won't ba happen again\nPrint /start to see start message")
    msg = f'New comment "LOW"'
    body = f'Order number: {context.user_data["order number"]}\nComment: {update.message.text}'
    email_push(msg, body)
    comment_db(context.user_data['rating'], context.user_data['order number'], update.message.text)
    return ConversationHandler.END


def final_rating_good(update, context):
    update.message.reply_text(
        "We understand your wishes.\nThank you for your recommendations\nPrint /start to see start message")
    msg = f'New comment "GOOD"'
    body = f'Order number: {context.user_data["order number"]}\nComment: {update.message.text}'
    email_push(msg, body)
    comment_db(context.user_data['rating'], context.user_data['order number'], update.message.text)
    return ConversationHandler.END


def final_rating_high(update, context):
    update.message.reply_text(
        "Thank you for visiting our cafe.\nWe will be waiting you again\nPrint /start to see start message")
    msg = f'New comment "HIGH"'
    body = f'Order number: {context.user_data["order number"]}\nComment: {update.message.text}'
    email_push(msg, body)
    comment_db(context.user_data['rating'], context.user_data['order number'], update.message.text)
    return ConversationHandler.END


def comment_db(rating, n_of_order, comment):
    com = Comments()
    com.rate = rating
    com.number_of_order = n_of_order
    com.comment = comment

    db_sess = db_session.create_session()

    db_sess.add(com)
    db_sess.commit()


def stop(update, context):
    pass


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    db_session.global_init("db/coffehouse_db.db")

    # СЦЕНАРИЙ БРОНИ СТОЛИКА
    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('make_a_reservation', reservation_start)],

        states={
            NAME: [MessageHandler(Filters.text, number, pass_user_data=True)],
            NUMBER: [MessageHandler(Filters.text, datetime, pass_user_data=True)],
            TIME: [MessageHandler(Filters.text, people, pass_user_data=True)],
            PEOPLE: [MessageHandler(Filters.text, final_reservation, pass_user_data=True)],
            BACK: [MessageHandler(Filters.text, start, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('start', start)]
    )

    # СЦЕНАРИЙ ПРЕДЗАКАЗА ЕДЫ
    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('make_a_preorder', preorder_start)],

        states={
            DECISION: [MessageHandler(Filters.text, decision, pass_user_data=True)],
            YES_DISHES: [MessageHandler(Filters.text, preorder_time, pass_user_data=True)],
            PRE_TIME: [MessageHandler(Filters.text, pre_number, pass_user_data=True)],
            PRE_NUMBER: [MessageHandler(Filters.text, final_preorder, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('start', start)]
    )

    # СЦЕНАРИЙ ОЦЕНИВАНИЯ КАФЕ
    conv_handler3 = ConversationHandler(
        entry_points=[CommandHandler('rate', start_rating)],

        states={
            RATING: [MessageHandler(Filters.text, rating, pass_user_data=True)],
            POINT: [MessageHandler(Filters.text, answer_rating, pass_user_data=True)],
            LOW: [MessageHandler(Filters.text, final_rating_low, pass_user_data=True)],
            GOOD: [MessageHandler(Filters.text, final_rating_good, pass_user_data=True)],
            HIGH: [MessageHandler(Filters.text, final_rating_high, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler((CommandHandler("start", start)))
    dp.add_handler((CommandHandler("information", help)))

    dp.add_handler(conv_handler1)
    dp.add_handler(conv_handler2)
    dp.add_handler(conv_handler3)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
