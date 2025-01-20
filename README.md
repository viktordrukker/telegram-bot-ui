# Telegram Bots Management UI

This is a simple web application built with Flask to manage Telegram bots. It provides a user interface where you can add and manage Telegram bot tokens.

## Features
- Add a Telegram bot by entering its token.
- Basic UI for managing bots.

## Prerequisites
- Python 3.12
- Docker (optional, for containerized deployment)

## Installation

### Without Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-bot-ui.git
   cd telegram-bot-ui
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python telegram_bot_ui.py
   ```

### With Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/telegram-bot-ui.git
   cd telegram-bot-ui
   ```

2. Build the Docker image:
   ```bash
   docker build -t telegram-bot-ui .
   ```

3. Run the Docker container:
   ```bash
   docker run -p 53197:53197 telegram-bot-ui
   ```

## Usage
- Access the application at `http://localhost:53197`.
- Use the form to add a Telegram bot by entering its token.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)