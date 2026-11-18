# ✨ Nova: Personal Assistant (n8n + Gemini + Streamlit)

Nova is a personal assistant that runs as an AI agent in **n8n** and is used through a
small **Streamlit** chat page. You type a request, the app sends it to an n8n webhook, the
agent picks the right Google tool, and the answer comes back to the chat.

## What it can do

| Area | Abilities |
|---|---|
| Ask anything | Answer questions, live web search (SerpApi) |
| Calendar | Create an event, get one event, list events, delete an event |
| Email | Read recent emails, read one email, summarize, send or reply |
| Tasks | Create, get one, list all, delete |
| Notes | Create a Google Doc, add text to it, read it |
| Expenses | Add an expense, list expenses, calculate totals (Google Sheets) |

## How it works

```
Streamlit app  ->  n8n Webhook  ->  AI Agent (Gemini + memory + tools)  ->  Respond to Webhook  ->  Streamlit app
```

The agent's behaviour is defined by the system prompt in [`sysprompt.md`](sysprompt.md).

## Project files

| File | Purpose |
|---|---|
| `app.py` | Streamlit chat interface |
| `test_webhook.py` | Sends one test message to the webhook |
| `workflow.json` | The n8n workflow (personal IDs removed) |
| `sysprompt.md` | The agent's system prompt |
| `requirements.txt` | Python libraries |
| `.env.example` | Template for your private `.env` file |

## Requirements

- Docker Desktop
- Python 3.10 or newer
- A Google account
- A Google AI Studio API key (Gemini)
- A SerpApi key (free plan is enough) for web search

## Setup

### 1. Start n8n with Docker

```
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 -e GENERIC_TIMEZONE="Asia/Kolkata" -e TZ="Asia/Kolkata" -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Change the timezone to your own. Open http://localhost:5678 and create the owner account.
Keep this terminal open while you use the assistant. Your workflows are saved in the
`n8n_data` volume.

### 2. Set up Google access

1. Create a project in [Google Cloud Console](https://console.cloud.google.com).
2. Enable these APIs: **Google Sheets, Google Drive, Gmail, Google Calendar, Google Docs, Google Tasks**.
3. Configure the **OAuth consent screen** (External) and add your own Google account as a **test user**.
4. Create an **OAuth client ID** (Web application) and add this redirect URI:
   `http://localhost:5678/rest/oauth2-credential/callback`
5. Copy the **Client ID** and **Client Secret**. Keep the secret private.

### 3. Create the other keys

- **Gemini:** create an API key at [Google AI Studio](https://aistudio.google.com).
- **SerpApi:** create a free key at [serpapi.com](https://serpapi.com).

### 4. Prepare the Google files

- **Expenses sheet:** create a Google Sheet with these headers in row 1:
  `ID`, `Date`, `Expense_Category`, `Expense`, `Remarks`
- **Tasks:** make sure you have a Google Tasks list.

### 5. Import the workflow

1. In n8n, create a new workflow, open the **⋯** menu, choose **Import**, and select `workflow.json`.
2. Create credentials in n8n and select them on the nodes: **Google Calendar, Gmail, Google Sheets,
   Google Docs, Google Tasks, Google Gemini (PaLM), SerpApi**. Use the same Client ID and Secret for the Google ones.
3. The export has personal IDs replaced by placeholders, so re-select these:
   - **Calendar nodes:** choose your own calendar.
   - **Add_Expense and Get_Expenses:** choose your Expenses sheet and Sheet1.
   - **Task nodes:** choose your task list.
4. **Calendar event titles:** open **Create_Calendar_Event**, add **Summary** under *Additional Fields*,
   and set it to **Defined by agent**. Without this, events are created as "(No title)".
5. **Webhook path:** open the **Webhook** node and change the path from `your-webhook-id` to a long
   random string. Anyone who knows the URL can trigger your assistant, so keep it secret.
6. **System prompt:** the AI Agent's *System Message* must be in **Expression** mode so `{{ $now }}`
   becomes the current date.
7. Check the Gemini model on the **Google Gemini Chat Model** node. Model names and free limits change,
   so pick one that works for you.

### 6. Publish the workflow

Click **Publish** in n8n. Open the **Webhook** node, switch to the **Production URL** tab, and copy the URL.

### 7. Configure the app

```
copy .env.example .env
```

Open `.env` and replace the example with your real Production URL:

```
N8N_WEBHOOK_URL=http://localhost:5678/webhook/your-long-random-string
```

`.env` is listed in `.gitignore`, so it is never uploaded to GitHub.

### 8. Run the app

```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. You can also test only the webhook with `python test_webhook.py`.

## Notes and limits

- Docker and n8n must be running for the assistant to answer.
- The Gemini free tier has daily request limits. An agent run uses several requests, so heavy testing
  can hit a `429 Too Many Requests` error. Switch to another model or wait for the quota to reset.
- Simple Memory lives in n8n's memory only and resets when n8n restarts.
- Use the Production URL for the app. The Test URL (`/webhook-test/`) only works after clicking
  *Listen for test event* in n8n.

## Security

- Never commit `.env`, API keys, the Client Secret or your real webhook URL.
- If a secret is ever pushed by mistake, delete it at its source and create a new one.
- This project is meant to run on your own computer. Do not expose your n8n to the internet without protection.
