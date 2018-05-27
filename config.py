import redis
from os import path

RESTAURANT_NAME = "Demo Restaurant"
TELGRAM_TOKEN = '613479419:AAE_POPUfhZ2BIl0iJuuhjLuPez9G_TjW1E'
#AUTH_FILE ="D:\GAE_telegram\gc\My First Project-9599e1b29d6a.json"

current_directory = path.abspath(path.dirname(__file__))
AUTH_FILE = path.join(current_directory, "My First Project-9599e1b29d6a.json")

# Use your gmail id and pass and
# On myaccount.google / security  , Allow for less secure app
gmail_id = "srvgarg011@gmail.com"
gmail_pass = "srv123456"


r = redis.StrictRedis(host='localhost', port=6379, db=0)
host="redis-13990.c1.us-east1-2.gce.cloud.redislabs.com"
port=13990
#r = redis.StrictRedis(host=host, port=port, db=0)
