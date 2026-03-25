# Telebot for Restaurant Reservation

A Telegram chatbot that lets customers **browse a restaurant menu**, **reserve a table**, and **receive an e-mail + QR confirmation** — all inside a Telegram conversation. The bot uses Google Cloud NLP to understand free-text queries, Google Cloud Datastore for persistent storage, and Redis for session caching.

> **Demo Video:** [Watch on Google Drive](https://drive.google.com/open?id=10cuko9LRsFTMmNHQZA1SM_-ENbvpo4LD)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Bot Conversation Flow](#bot-conversation-flow)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Deploying to Google App Engine](#deploying-to-google-app-engine)
- [Telegram Commands & Queries](#telegram-commands--queries)

---

## Features

| Feature | Details |
|---|---|
| 🆕 New-user detection | Greets first-time visitors, offers a 30 % first-booking discount |
| 🔁 Returning-user flow | Fetches last reservation from Cloud Datastore and offers to re-book with the same details |
| 📋 Menu display | Sends the restaurant menu as a photo |
| 📅 Interactive calendar | Inline calendar keyboard for date selection |
| ⏰ Time-slot selection | Four time-slot buttons (Morning / Afternoon / Evening / Night) |
| 👥 Party-size selection | Numeric keyboard for 1–9 guests |
| 🔖 QR confirmation | Generates a unique QR code (using `qrcode`) sent in-chat |
| 📧 E-mail confirmation | Sends a booking summary to the customer's e-mail via Gmail |
| 🧠 NLP intent detection | Google Cloud Natural Language API extracts entities & sentiment from free-text messages |
| ☁️ Cloud persistence | Reservations stored in Google Cloud Datastore |
| ⚡ Session caching | Redis stores per-user state across message handlers |

---

## Architecture

```
┌──────────────┐     Telegram Bot API      ┌──────────────────────────┐
│   Telegram   │ ◄────────────────────────► │   main.py  (TeleBot)     │
│   Client     │                            │                          │
└──────────────┘                            │  ┌────────────────────┐  │
                                            │  │  utility.py        │  │
                                            │  │  (orchestration)   │  │
                                            │  └────────┬───────────┘  │
                                            │           │              │
                          ┌─────────────────┼───────────┼──────────┐  │
                          │                 │           │          │  │
                   ┌──────▼──────┐  ┌───────▼───────┐  │  ┌───────▼──┴──┐
                   │  gc_nlp     │  │  gc_datastore  │  │  │   Redis     │
                   │  (Google    │  │  (Google Cloud │  │  │  (session   │
                   │   NLP API)  │  │   Datastore)   │  │  │   cache)    │
                   └─────────────┘  └────────────────┘  │  └─────────────┘
                                                         │
                                                  ┌──────▼──────┐
                                                  │  Gmail API  │
                                                  │  (e-mail    │
                                                  │  confirm.)  │
                                                  └─────────────┘
```

**Hosted on:** Google App Engine (Flexible Environment, Python 3)

---

## Bot Conversation Flow

```
/start
  │
  ├─ New user ──► Welcome + 30% discount offer
  │                │
  │                ├─ "Menu"          ──► Send menu photo ──► Offer table reservation
  │                └─ "Reserve Table" ──► Ask party size ──► Calendar ──► Time slot
  │                                                                │
  │                                                                └─► Booking summary
  │                                                                    ──► QR code
  │                                                                    ──► E-mail confirmation
  │
  └─ Returning user ──► Show last reservation details
                         │
                         ├─ "Yes" (same details) ──► Calendar ──► QR + E-mail
                         └─ "No"  (new details)  ──► Menu or new reservation flow

Free-text queries (via Google NLP):
  "can I see the menu?"          ──► Menu flow
  "reserve a table for me"       ──► Reservation flow
  "what are your timings?"       ──► Opening hours message
```

---

## Project Structure

```
Telebot-for-Restaurant-Reservation/
├── main.py                  # Bot entry-point; all Telegram handlers
├── utility.py               # Helper functions (NLP, Datastore, Gmail)
├── config.py                # Configuration (tokens, credentials, Redis)
├── app.yaml                 # Google App Engine deployment config
├── requirements.txt         # Python dependencies
├── tox.ini                  # Tox configuration
├── task_flow.txt            # Original task specification & solution notes
│
├── gc_nlp/
│   └── gc_nlp.py            # Google Cloud Natural Language API wrapper
│
├── gc_datastore/
│   ├── gc_datastore.py      # Google Cloud Datastore CRUD helpers
│   └── index.yaml           # Datastore composite index definitions
│
├── others/
│   ├── calender.py          # Inline calendar keyboard builder
│   └── menu.jpg             # Restaurant menu image
│
└── Demo_Video/
    └── Demo_Video.mp4       # Recorded demo
```

---

## Prerequisites

- Python **3.6+**
- A **Telegram Bot token** — create one via [@BotFather](https://t.me/BotFather)
- A **Google Cloud Platform** project with the following APIs enabled:
  - Cloud Natural Language API
  - Cloud Datastore API
- A **Google service-account JSON key** with roles for Datastore and NLP
- **Redis** server (local or hosted, e.g. [Redis Labs](https://redislabs.com/))
- A **Gmail account** with "Allow less secure apps" enabled (or an App Password)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/SouravAggarwal/Telebot-for-Restaurant-Reservation.git
cd Telebot-for-Restaurant-Reservation

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server
sudo service redis-server start
```

---

## Configuration

Edit **`config.py`** and replace the placeholder values:

```python
RESTAURANT_NAME = "Your Restaurant Name"

# Telegram Bot token from @BotFather
TELGRAM_TOKEN = '<your-telegram-bot-token>'

# Absolute path to your GCP service-account JSON key
AUTH_FILE = '/path/to/your-service-account.json'

# Gmail credentials for sending confirmation e-mails
gmail_id   = "your-email@gmail.com"
gmail_pass = "your-password"        # Use an App Password if 2FA is enabled

# Redis connection (local default shown; switch to hosted if needed)
r = redis.StrictRedis(host='localhost', port=6379, db=0)
```

> ⚠️ **Never commit real credentials to version control.** Consider using environment variables or a secrets manager in production.

---

## Running Locally

```bash
# Make sure Redis is running
sudo service redis-server start

# Start the bot
python main.py
```

The bot will begin long-polling Telegram for updates. Open Telegram, find your bot by its username, and send `/start`.

---

## Deploying to Google App Engine

The project includes an `app.yaml` configured for the **App Engine Flexible Environment**:

```yaml
runtime: python
env: flex
entrypoint: gunicorn -b :$PORT main:app
runtime_config:
  python_version: 3
```

```bash
# Authenticate with GCP
gcloud auth login
gcloud config set project <your-gcp-project-id>

# Deploy
gcloud app deploy app.yaml
```

> **Note:** The current `main.py` uses `bot.polling()` (long-polling), which is suitable for local development. For App Engine deployment, switch to a **webhook**-based approach using Flask to expose a `/webhook` endpoint and call `bot.process_new_updates()`.

---

## Telegram Commands & Queries

| Command / Query | Description |
|---|---|
| `/start` | Begin or restart the conversation |
| `/new` | Trigger the new-user menu (Menu or Reserve a Table) |
| `/hello` | Simple ping to check if the bot is alive |
| `"can I see the menu?"` | NLP-detected → sends the menu photo |
| `"reserve a table for me"` | NLP-detected → starts the reservation flow |
| `"what are your timings?"` | NLP-detected → sends opening hours |

**Opening hours returned by the bot:**
- Weekdays: 9:00 am – 11:00 pm
- Weekends: 8:30 am – 11:30 pm
   
