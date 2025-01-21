from app.tasks import create_celery
from app.models.bot import Bot
from app.models.analytics import Analytics
from app import db
from datetime import datetime
import json
import logging
import telegram
from telegram.error import TelegramError

celery = create_celery()
logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def start_bot(self, bot_id):
    try:
        bot = Bot.query.get(bot_id)
        if not bot:
            raise ValueError(f'Bot {bot_id} not found')

        # Initialize Telegram bot
        telegram_bot = telegram.Bot(token=bot.bot_token)
        
        # Test connection
        telegram_bot.get_me()

        # Update bot status
        bot.status = 'running'
        bot.last_active = datetime.utcnow()
        db.session.commit()

        # Start metrics collection
        collect_bot_metrics.delay(bot_id)

        return {'status': 'success', 'message': f'Bot {bot.bot_name} started successfully'}
    except TelegramError as e:
        logger.error(f'Telegram error starting bot {bot_id}: {str(e)}')
        bot.status = 'error'
        db.session.commit()
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f'Error starting bot {bot_id}: {str(e)}')
        bot.status = 'error'
        db.session.commit()
        raise

@celery.task(bind=True, max_retries=3)
def stop_bot(self, bot_id):
    try:
        bot = Bot.query.get(bot_id)
        if not bot:
            raise ValueError(f'Bot {bot_id} not found')

        # Update bot status
        bot.status = 'stopped'
        db.session.commit()

        return {'status': 'success', 'message': f'Bot {bot.bot_name} stopped successfully'}
    except Exception as e:
        logger.error(f'Error stopping bot {bot_id}: {str(e)}')
        raise self.retry(exc=e)

@celery.task(bind=True)
def collect_bot_metrics(self, bot_id):
    try:
        bot = Bot.query.get(bot_id)
        if not bot or bot.status != 'running':
            return

        # Initialize Telegram bot
        telegram_bot = telegram.Bot(token=bot.bot_token)
        
        # Collect basic metrics
        updates = telegram_bot.get_updates(timeout=0)
        
        metrics = {
            'total_updates': len(updates),
            'unique_users': len(set(update.message.from_user.id for update in updates if update.message)),
            'message_types': {}
        }

        # Analyze message types
        for update in updates:
            if update.message:
                msg_type = update.message.content_type
                metrics['message_types'][msg_type] = metrics['message_types'].get(msg_type, 0) + 1

        # Save metrics
        analytics = Analytics(
            bot_id=bot_id,
            metric_type='hourly_stats',
            metric_value=metrics,
            timestamp=datetime.utcnow()
        )
        db.session.add(analytics)
        db.session.commit()

        # Schedule next collection in 1 hour if bot is still running
        if bot.status == 'running':
            collect_bot_metrics.apply_async(args=[bot_id], countdown=3600)

    except Exception as e:
        logger.error(f'Error collecting metrics for bot {bot_id}: {str(e)}')
        raise

@celery.task(bind=True)
def broadcast_message(self, bot_id, message_data):
    try:
        bot = Bot.query.get(bot_id)
        if not bot:
            raise ValueError(f'Bot {bot_id} not found')

        telegram_bot = telegram.Bot(token=bot.bot_token)
        
        # Get all chat IDs for this bot (you need to implement this)
        chat_ids = get_bot_chat_ids(bot_id)
        
        results = {
            'total': len(chat_ids),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for chat_id in chat_ids:
            try:
                if message_data.get('type') == 'text':
                    telegram_bot.send_message(
                        chat_id=chat_id,
                        text=message_data['content'],
                        parse_mode=message_data.get('parse_mode', 'HTML')
                    )
                elif message_data.get('type') == 'media':
                    # Handle different media types
                    pass

                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'chat_id': chat_id,
                    'error': str(e)
                })

        return results
    except Exception as e:
        logger.error(f'Error broadcasting message for bot {bot_id}: {str(e)}')
        raise

def get_bot_chat_ids(bot_id):
    # TODO: Implement this function to get all chat IDs for a bot
    # This should be stored when users interact with the bot
    return []