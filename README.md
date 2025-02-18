# MirrorBot
A Telegram bot that mimics your communication style using GPT. It learns from your chats and replies just like you! Simple, fun, and personalized.

## Simple Echo Bot

This bot will echo any received messages.

### Setup and Installation

1. Create and activate virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Linux/Mac
    # or
    venv\Scripts\activate  # On Windows
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create `.env` file and add your bot token:
    ```sh
    echo "BOT_TOKEN=your_actual_token_here" > .env
    ```

4. Run the bot:
    ```sh
    python bot.py
    ```

### Development

- Always activate virtual environment before running the bot:
    ```sh
    source venv/bin/activate  # On Linux/Mac
    # or
    venv\Scripts\activate  # On Windows
    ```
