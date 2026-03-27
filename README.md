# Telegram Inbox Bot (Python, Webhook, SQLite)

A production-ready Telegram inbox relay bot built with **python-telegram-bot v20+**.

It helps teams manage private user messages in one shared Telegram group:

- Any user can DM the bot
- The bot forwards the message to your inbox group with sender details
- If your team replies in the group, the bot sends that reply back to the original user

Supported message types:

- Text
- Photo
- Video
- Document
- Voice
- Sticker

---

## How It Works

1. A user sends a private message to the bot.
2. The bot forwards the message to your configured group.
3. The bot stores a mapping in SQLite: group_message_id -> user_id.
4. A team member replies to that forwarded message in the group.
5. The bot looks up the original user and forwards the reply back to them in DM.

This keeps your support/inbox workflow inside a group while preserving private conversations with users.

---

## Project Structure

- `bot.py` - app startup, webhook server, handler registration
- `handlers.py` - message handling logic and error handling
- `database.py` - SQLite initialization and message mapping operations
- `config.py` - environment loading and validation
- `Procfile` - Heroku process definition
- `runtime.txt` - Heroku Python runtime version
- `requirements.txt` - Python dependencies
- `.env.example` - required environment variables template
- `.gitignore` - Python and local environment ignores

---

## Requirements

- Python 3.11+
- A Telegram bot token from BotFather
- A Telegram group where forwarded messages should appear
- Public HTTPS URL for webhook (for production)

---

## Configuration

Create a `.env` file based on `.env.example`:

```env
BOT_TOKEN=123456789:your_bot_token_here
GROUP_ID=-1001234567890
WEBHOOK_URL=https://your-app-name.herokuapp.com
```

Environment variables:

- `BOT_TOKEN` - your Telegram bot token
- `GROUP_ID` - numeric Telegram group chat ID (must be integer)
- `WEBHOOK_URL` - public base URL where the bot is hosted
- `PORT` - optional; defaults to `8443` (Heroku sets this automatically)

### How to Get GROUP_ID

Telegram invite links are **not** the same as chat IDs. You must use the numeric chat ID.

Common methods:

1. Add your bot to the target group.
2. Send a message in that group.
3. Call Telegram API:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

4. Find the group chat object and copy `chat.id` (usually starts with `-100...`).

Tip: If `getUpdates` is empty, make sure webhook is not currently active or use a helper bot like @userinfobot/@RawDataBot (if available) to inspect group metadata.

---

## Local Development

1. Create and activate a virtual environment.
2. Install dependencies.
3. Configure `.env`.
4. Run the bot.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

The bot runs in webhook mode and starts an HTTP listener on `PORT` (default `8443`).
For local webhook testing, use a tunnel tool (for example ngrok) and set `WEBHOOK_URL` to your HTTPS tunnel URL.

---

## Deploying to Heroku

This project is already Heroku-ready.

Included files:

- `Procfile`: `web: python bot.py`
- `runtime.txt`: pinned Python runtime
- `requirements.txt`: dependencies

### Deploy Steps

1. Create a Heroku app.
2. Set config vars in Heroku:
   - `BOT_TOKEN`
   - `GROUP_ID`
   - `WEBHOOK_URL` (example: `https://your-app.herokuapp.com`)
3. Push code to Heroku.
4. Scale dyno:

```bash
heroku ps:scale web=1 -a <your-app-name>
```

5. Check logs:

```bash
heroku logs --tail -a <your-app-name>
```

The bot automatically sets Telegram webhook to:

`<WEBHOOK_URL>/webhook/<BOT_TOKEN>`

---

## Error Handling

The bot includes basic graceful handling:

- Logs unexpected errors
- Handles delivery failures when a user blocks the bot
- Avoids crashing on forbidden or bad request responses

---

## Security Notes

- Never commit `.env` to Git
- Rotate your bot token immediately if exposed
- Restrict who can add the bot to groups (BotFather privacy settings as needed)
- Keep dependencies up to date

---

## Bot Commands

- `/start` - sends a short welcome message in private chat

---

## Troubleshooting

### Bot forwards DMs but replies from group are not delivered

- Ensure team replies are direct replies to a forwarded message in the configured group
- Confirm `GROUP_ID` is correct
- Check logs for forbidden/bad request errors

### Webhook not receiving updates

- Verify `WEBHOOK_URL` is correct and public over HTTPS
- Confirm your app is running and listening on Heroku `PORT`
- Check webhook info:

```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### Cannot determine group ID from invite link

- This is expected. Invite links do not reveal numeric chat ID.
- Use `getUpdates` or metadata helper methods to retrieve chat ID.

---

## License

This repository includes a `LICENSE` file. Use and modify according to that license.

---

## Contributing

Contributions are welcome:

- Bug reports
- Feature requests
- Pull requests

If you propose major changes, open an issue first to discuss design and compatibility.
