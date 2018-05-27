import os
from google.cloud import datastore

import config as c

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = c.AUTH_FILE

dbclient = datastore.Client(project='probable-axon-205116')
kind = "Demo_Restaurant"


def add_data(id, data, first_name):
    '''id: User/Chat id'''
    key = dbclient.key(kind, str(id))
    entity = datastore.Entity(key=key, )

    entity["Last_Reservation"] = str(list(data.keys())[0])
    entity["email"] = "srvgarg011@gmail.com"
    entity["Name"] = str(first_name)

    old_resv = {}
    try:
        old_data = reterive_data(id)
        old_resv = (dict(old_data["Reservations"]))

    except:
        pass

    entity["Reservations"] = {**old_resv, **data}
    dbclient.put(entity)


def reterive_data(id):
    key = dbclient.key(kind, str(id))
    return (dbclient.get(key))


def is_first_time(id):
    with dbclient.transaction():
        key = dbclient.key(kind, str(id))
        task = dbclient.get(key)

        res = 0 if (task) else 1
        return (res)


if __name__ == "__main__":
    # add_data(526699328, data="d")
    is_first_time(526699328)
    # reterive_data(526699328)
