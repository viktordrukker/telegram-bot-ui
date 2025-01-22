# Telegram Bot Management Platform

A unified platform for managing multiple Telegram bots and broadcasting advertisements across them.

## Features

- Centralized bot management through UI/API
- Single-instance bot control (start/stop/restart)
- Advertisement broadcasting system
- Comprehensive metrics and statistics dashboard
- Raw database viewer for requests and moderation
- Error handling and logging system

## Prerequisites

- Docker Desktop
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/viktordrukker/telegram-bot-ui.git
cd telegram-bot-ui
```

2. Build and run with Docker Compose:
```bash
docker compose up --build
```

3. Access the application:
- Web UI: http://localhost:50328
- Task Monitor: http://localhost:5555

## Project Structure

```
telegram-bot-ui/
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── tasks/             # Background tasks
├── frontend/              # React frontend
│   ├── public/            # Static files
│   └── src/               # React components
├── migrations/            # Database migrations
└── tests/                 # Test suites
```

## Development

### Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Start development server
flask run
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Testing

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend && npm test
```

## Environment Variables

Create a `.env` file in the root directory:

```env
FLASK_ENV=development
DATABASE_URL=postgresql://bot_admin:wewffikp@db:5432/telegram_bot_db
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details