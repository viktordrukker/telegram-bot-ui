from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_bot', methods=['POST'])
def add_bot():
    bot_token = request.form['bot_token']
    # Add logic to handle the bot token (e.g., store it in a database)
    return f"Bot with token {bot_token} added successfully!"

if __name__ == '__main__':
    app.run(port=53197, debug=True)