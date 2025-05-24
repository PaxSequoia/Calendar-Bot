# Golarion Calendar Tracker Discord Bot

A Discord bot for tracking and posting daily Golarion (Pathfinder) calendar dates and holidays to your server.

---

## Features

- **Daily Scheduled Posting:** Automatically posts the current Golarion date and the next holiday to a designated channel at 6:00 AM US/Central time.
- **Holiday Tracking:** Notifies about upcoming Golarion holidays.
- **Manual Commands:** Admins and users can manually post the date, check the next holiday, and configure the bot.
- **Persistent Channel Tracking:** Remembers which channel to post in, even after restarts.
- **Timezone Handling:** Correctly accounts for US/Central Daylight Saving Time.

---

## Setup & Administration

### 1. Prerequisites

- Python 3.8+
- Discord bot token ([Create a bot here](https://discord.com/developers/applications))
- (Optional) [virtualenv](https://virtualenv.pypa.io/en/latest/) for isolated Python environments

### 2. Installation

```sh
git clone <your-repo-url>
cd Calendar\ Bot
pip install -r requirements.txt

### 3. Configuration
Create a .env file in the project root<vscode_annotation details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'>: </vscode_annotation><vscode_annotation details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'> </vscode_annotation>``` DISCORD_TOKEN=your-bot-token-here

### 4. Running the Bot
```sh
python main.py

3. Configuration
Create a .env file in the project root<vscode_annotation details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'>: </vscode_annotation><vscode_annotation details='%5B%7B%22title%22%3A%22hardcoded-credentials%22%2C%22description%22%3A%22Embedding%20credentials%20in%20source%20code%20risks%20unauthorized%20access%22%7D%5D'> </vscode_annotation>``` DISCORD_TOKEN=your-bot-token-here

```markdown
# Golarion Calendar Tracker Discord Bot

A Discord bot for tracking and posting daily Golarion (Pathfinder) calendar dates and holidays to your server.

---

## Features

- **Daily Scheduled Posting:** Automatically posts the current Golarion date and the next holiday to a designated channel at 6:00 AM US/Central time.
- **Holiday Tracking:** Notifies about upcoming Golarion holidays.
- **Manual Commands:** Admins and users can manually post the date, check the next holiday, and configure the bot.
- **Persistent Channel Tracking:** Remembers which channel to post in, even after restarts.
- **Timezone Handling:** Correctly accounts for US/Central Daylight Saving Time.

---

## Setup & Administration

### 1. Prerequisites

- Python 3.8+
- Discord bot token ([Create a bot here](https://discord.com/developers/applications))
- (Optional) [virtualenv](https://virtualenv.pypa.io/en/latest/) for isolated Python environments

### 2. Installation

```sh
git clone <your-repo-url>
cd Calendar\ Bot
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:

```
DISCORD_TOKEN=your-bot-token-here
```

### 4. Running the Bot

```sh
python main.py
```

---

## Administration Commands

| Command                       | Description                                                      | Permissions      |
|-------------------------------|------------------------------------------------------------------|------------------|
| `!set_channel #channel`       | Set the channel for daily updates                                | Admin only       |
| `!current_channel`            | Show the currently set channel for daily updates                 | Anyone           |
| `!post_date`                  | Manually post the current Golarion date                          | Anyone           |
| `!next_holiday`               | Show the next upcoming holiday and days until it                 | Anyone           |
| `!set_year_offset <offset>`   | Adjust the Golarion year offset                                  | Admin only       |
| `!calendar_help`              | Display help and command list                                    | Anyone           |
| `!ping`                       | Check if the bot is responsive                                   | Anyone           |

---

## Notes for Administrators

- **Channel Setup:** Use `!set_channel #channel` in your desired channel to enable daily posts.
- **Permissions:** Only users with Administrator permissions can set the posting channel or change the year offset.
- **Database:** The bot uses a local SQLite database (`bot_database.db`) to store channel and holiday data.
- **Timezone:** All scheduled posts are made at 6:00 AM US/Central, with automatic DST adjustment.
- **Logs:** Errors are printed to the console. For production, consider redirecting logs to a file.

---

## Troubleshooting

- **Bot Not Posting:** Ensure the bot has permission to send messages in the target channel.
- **Scheduler Issues:** The scheduler starts on bot login. If you restart the bot, the scheduled job will persist.
- **Holiday/Date Errors:** Check that your system time is correct and the bot is running continuously.

---

## Updating Holidays

To add or modify holidays, update the `populate_holidays()` function in main.py and restart the bot.

---

## Security

- **Keep your .env file private** and never share your bot token.
- **Do not run the bot as a privileged user** on your system.

---

## License

For internal/administrative use only. Not for public distribution.

---