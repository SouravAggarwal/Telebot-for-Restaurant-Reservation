import telebot
import time
import qrcode
import random
import re
import datetime
from telebot import types
from io import BytesIO

import config as c
import utility as util
from others.calender import create_calendar

current_shown_dates = {}
# Redis
r = c.r

bot = telebot.TeleBot(c.TELGRAM_TOKEN)
print("starting..., About Bot", bot.get_me())


@bot.message_handler(commands=['start'])
def welcome_msg(message):
    chat_id = message.chat.id
    welcome_new1 = ["Hey {}, Welcome to our Demo_Restaurant.", "Howdy {}, Weclome to our Demo_Restaurant.",
                    "Hello {}, Welcome to our Demo_Restaurant"]

    msg = random.choice(welcome_new1).format(message.from_user.first_name)
    bot.send_message(chat_id, msg)

    welcome_new2 = "\n It Looks like you are a New User. \n You will get 30% discount on your first booking."
    welcom_registered = ["\n Great to have you back.", "\n Glad to see you Back."]

    # If user is not Registered
    if util.is_first_time(chat_id):
        bot.send_message(chat_id, welcome_new2)
        m1 = "Would you like to see the Menu or \n Want to book a Table?"
        r.set(str(chat_id) + "new_user", 1)
        new_person(message, m1)
    else:
        bot.send_message(chat_id, random.choice(welcom_registered))
        r.set(str(chat_id) + "new_user", 0)
        resigtered_person(message)


# argument m1 will work only, if we call through command /new
@bot.message_handler(commands=['new'])
def new_person(message, m1="menu or table"):
    chat_id = message.chat.id
    # Two options Menu or Table Reservation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    b1 = types.KeyboardButton('Menu')
    b2 = types.KeyboardButton('Reserve a Table')
    markup.add(b1, b2)
    bot.send_message(chat_id, m1, reply_markup=markup)


@bot.message_handler(commands=['registered'])
def resigtered_person(message):
    chat_id = message.chat.id

    # Get last Reservation from Google Datastore
    last_data = util.get_lastresv_datastore(chat_id)
    last_time = str(last_data["Last_Reservation"])

    l_time = last_data["Reservations"][last_time]["time"]
    l_date = last_data["Reservations"][last_time]["date"]
    l_person = last_data["Reservations"][last_time]["person"]

    m1 = f"I see your last reservation was on {l_date}. \n "
    m2 = f"for {l_person} persons at {l_time}. \n "
    m3 = "Would you like to book with the same details? \n "

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    b1 = types.KeyboardButton('Yes')
    b2 = types.KeyboardButton('No')
    markup.add(b1, b2)
    sent1 = bot.send_message(chat_id, m1 + m2 + m3, reply_markup=markup)
    bot.register_next_step_handler(sent1, want_tobook_same)


def want_tobook_same(message):
    chat_id = message.chat.id
    if "no" in str(message.text).lower():
        m1 = "So, Would you like to see our New Menu \n "
        m2 = "or \n Want to Reserve Table with new Details. \n "
        new_person(message, m1 + m2)

    if "yes" in str(message.text).lower():
        get_date(message)


def h_menu(chat_id):
    # do nlp, if user want menu.
    menu_photo = open("others/menu.jpg", 'rb')
    bot.send_photo(chat_id, menu_photo)

    t1 = "Our Today's Special is Demo_Dish."
    t2 = "Would you like to Reserve a Table?"

    r.set(str(chat_id) + "last_ques", "TABLE_RESERVATION")
    # button for Reservation
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    b1 = types.KeyboardButton('Reserve a Table')
    markup.add(b1)
    bot.send_message(chat_id, t1)
    bot.send_message(chat_id, t2, reply_markup=markup)


def h_reservation(chat_id, no_of_person=0):
    # do nlp, if user want to Reserve at table
    if not no_of_person:
        t1 = "For How many Persons?"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        b1 = types.KeyboardButton(1);
        b6 = types.KeyboardButton(6)
        b2 = types.KeyboardButton(2);
        b7 = types.KeyboardButton(7)
        b3 = types.KeyboardButton(3);
        b8 = types.KeyboardButton(8)
        b4 = types.KeyboardButton(4);
        b9 = types.KeyboardButton(9)
        b5 = types.KeyboardButton(5);
        b0 = types.KeyboardButton(0)
        markup.row(b1, b2, b3)
        markup.row(b4, b5, b6)
        markup.row(b7, b8, b9)
        sent1 = (bot.send_message(chat_id, t1, reply_markup=markup))
        bot.register_next_step_handler(sent1, save_person)


def save_person(message):
    '''message: no. of persons'''
    try:
        no_of_person = re.findall(r'\d+', message.text)
        r.set(str(message.chat.id) + "no_persons", no_of_person[0])
        get_date(message)
    except:
        pass


def get_date(message):
    '''Send Calender to user and Ask for Date'''
    chat_id = message.chat.id

    # Ask for date
    t1 = "Please Choose a Date for Reservation"
    r.set(str(chat_id) + "Asking_date", 1)
    now = datetime.datetime.now()

    date = (now.year, now.month)
    current_shown_dates[chat_id] = date  # Saving the current date in a dict
    markup = create_calendar(now.year, now.month)
    bot.send_message(chat_id, t1, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_date_input(call):
    '''When user Clicks on a calender date'''
    chat_id = call.message.chat.id
    if int(r.get(str(chat_id) + "Asking_date").decode("utf-8")):
        r.set(str(chat_id) + "Asking_date", 0)
        saved_date = current_shown_dates.get(chat_id)
        if (saved_date is not None):
            day = call.data[13:]
            date = "-".join([str(saved_date[0]), str(saved_date[1]), str(day)])
            # t = datetime.datetime.strptime(date, '%Y-%m-%d')
            t1 = "Ok, on " + str(date)
            r.set(str(chat_id) + "date", date)

            # get time for new user.
            is_new_usr = (r.get(str(chat_id) + "new_user")).decode("utf-8")

            if is_new_usr:
                bot.send_message(chat_id, t1)
                get_time(call.message)
            else:
                sent1 = bot.send_message(chat_id, t1)
                bot.register_next_step_handler(sent1, confirmation)


def get_time(message):
    chat_id = message.chat.id
    t1 = "At What time? "
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    b1 = types.KeyboardButton("9:00 - 12:00 (Morning)")
    b2 = types.KeyboardButton("12:00 - 5:00 (Afternoon)")
    b3 = types.KeyboardButton("5:00 - 7:00 (Evening)")
    b4 = types.KeyboardButton("7:00 - 11:00 (Night)")
    markup.row(b1)
    markup.row(b2)
    markup.row(b3)
    markup.row(b4)
    sent1 = (bot.send_message(chat_id, t1, reply_markup=markup))
    #
    r.set(str(chat_id) + "is_Time_entered", 0)
    bot.register_next_step_handler(sent1, confirmation)


def confirmation(message):
    '''Check the message, if correct'''
    chat_id = message.chat.id
    r.set(str(chat_id) + "is_Time_entered", 1)
    is_new_usr = (r.get(str(chat_id) + "new_user")).decode("utf-8")

    if is_new_usr:
        res = util._check_(message.text)
        # Check res, if new user then it must contain Morn, Even, After, else 0
        if not res:

            t5 = "Sorry, I am not able to understand that. \n Can you Plz pick a option. \n "

            sent4=bot.send_message(chat_id, t5 )
            get_time(message)
            #bot.register_next_step_handler(sent4, get_time)
            return
        r.set(str(chat_id) + "time", res)

    if not is_new_usr:
        # get data ( no_persons, time) from cloud and save it in redis.
        util.set_lastdata_as_new(message)

    # Your booking details
    show_booking_details(message)
    t1 = "Just wait, I will give you a confirmation message,\n  If Available."
    bot.send_message(chat_id, t1)

    # do Actual check at Restaurant.
    time.sleep(2)

    bio = BytesIO()
    img = qrcode.make(str(chat_id))
    img.save(bio)
    bot.send_photo(chat_id, bio.getvalue())

    t2 = "Show this QR at Restaurant's Reception"
    t3 = "Thanks for giving us opportunity to serve you."
    bot.send_message(chat_id, t2)
    bot.send_message(chat_id, t3)
    util.save_to_datastore(message)

    # Ask for gmail
    t5 = "Sending your booking confirmation on your mail as well."
    bot.send_message(chat_id, t5)
    gmail_work1(message)


def gmail_work1(message):
    sent1 = bot.send_message(message.chat.id, "Please Enter your Email id.")
    bot.register_next_step_handler(sent1, gmail_work2)


def gmail_work2(message):
    '''message is Email id'''
    t1 = "Checking your mail Id. \n If found, You will get a confirmation mail. \n Please visit again!"
    util.gmail_msg(message)
    bot.send_message(message.chat.id, t1)


def show_booking_details(message):
    '''This will show the Details entered by user (from Redis)'''
    chat_id = message.chat.id
    r_date = r.get(str(chat_id) + "date")
    r_no_of_person = r.get(str(chat_id) + "no_persons")
    r_time = r.get(str(chat_id) + "time")

    t1 = f"Reserving a Table for {r_no_of_person.decode('utf-8')} persons \n " \
         f"on {r_date.decode('utf-8')} at {r_time.decode('utf-8')} \n "
    bot.send_message(chat_id, t1)


# Just for Hello
@bot.message_handler(commands=['hello'])
def hello(message):
    (r.set(str(message.chat.id) + "msg", "hello"))
    bot.send_message(message.chat.id, "hello")


# For all text entered by user (do nlp)
@bot.message_handler(content_types=['text'])
def raw_text(message):
    chat_id = message.chat.id
    results = util.do_nlp(chat_id, message.text)

    print("NLP RESULTS:", results)

    x = 0

    try:
        y = int(r.get(str(chat_id) + "is_Time_entered").decode("utf-8"))
    except:
        y = 1

    if "menu" in results["wordslist"] or "menu card" in results["wordslist"]:
        h_menu(chat_id)
        x = 1

    elif "table" in results["wordslist"] or "reservation" in results["wordslist"] or \
            ("yes" in (message.text).lower() and
             ((r.get(str(chat_id) + "last_ques").decode("utf-8") == "TABLE_RESERVATION"))
             and "menu" not in results["wordslist"]):
        h_reservation(chat_id)
        x = 1

    elif "timings" in results["wordslist"] or "timing" in results["wordslist"]:
        t1 = "Weekdays (9:00 am to 11:00 pm) \n Weekends (8:30 am to 11:30 pm)"
        bot.send_message(chat_id, t1);
        x = 1
        bot.send_message(chat_id, "To Begin, \n Click /start")


    elif not x and y:

        t2 = "Sorry I didn't get that \n If you want to Start Again.  \n " \
             "Click /start"
        bot.send_message(chat_id, t2)



while True:
    try:
    bot.polling(none_stop=True, interval=0, timeout=20)
    except:
        print("Exception")
