import time
import config as c

from gc_nlp import gc_nlp
from gc_datastore import gc_datastore
from gmail import GMail, Message

# redis
r = c.r


def do_nlp(id, msg):
    return gc_nlp.nlp_text(msg)


def save_to_datastore(message):
    chat_id = message.chat.id
    first_name = message.from_user.first_name
    data = {}
    r_date = r.get(str(chat_id) + "date")
    r_no_of_person = r.get(str(chat_id) + "no_persons")
    r_time = r.get(str(chat_id) + "time")

    data["date"] = r_date.decode("utf-8")
    data["person"] = r_no_of_person.decode("utf-8")
    data["time"] = r_time.decode("utf-8")

    curr_time = int(time.time())
    x = {str(curr_time): data}

    gc_datastore.add_data(chat_id, x, first_name=first_name)


def _check_(msg):
    lst = ["Morning", "Afternoon", "Evneing", "Night"]
    for i in lst:
        if i.lower() in msg.lower():
            return i
    return 0


def is_first_time(chat_id):
    return gc_datastore.is_first_time(chat_id)


def get_lastresv_datastore(chat_id):
    return gc_datastore.reterive_data(chat_id)


def set_lastdata_as_new(message):
    chat_id = message.chat.id
    # Get last reservation details,& set in redis as new reservation.
    last_data = get_lastresv_datastore(chat_id)
    last_time = last_data["Last_Reservation"]
    l_time = last_data[last_time]["time"]
    l_date = last_data[last_time]["person"]
    l_person = last_data[last_time]["date"]
    r.set(str(chat_id) + "no_persons", l_person)
    r.set(str(chat_id) + "time", l_time)


def gmail_msg(message):
    name =""
    try:
        name=message.from_user.first_name
    except:
        pass
    try:
        chat_id = message.chat.id
        r_date = r.get(str(chat_id) + "date")
        r_no_of_person = r.get(str(chat_id) + "no_persons")
        r_time = r.get(str(chat_id) + "time")
        msg = f" Hi {name}, \n Your booking are confirmed for {r_no_of_person.decode('utf-8')} persons " \
              f"on {r_date.decode('utf-8')} at {r_time.decode('utf-8')}. "
        gmail = GMail(c.gmail_id, c.gmail_pass)

        mail = Message('Demo_Restaurant', to=str(message.text), text=msg)
        gmail.send(mail)
    except:
        pass


if __name__ == "__main__":
    print(r.get("helll"))
