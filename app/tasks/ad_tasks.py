from app.tasks import create_celery
from app.models.advertisement import Advertisement
from app.models.bot import Bot
from app.models.analytics import Analytics
from app import db
from datetime import datetime
import json
import logging
import telegram
from telegram.error import TelegramError
from celery.schedules import crontab

celery = create_celery()
logger = logging.getLogger(__name__)

@celery.task(bind=True, max_retries=3)
def broadcast_advertisement(self, ad_id, bot_ids=None):
    try:
        ad = Advertisement.query.get(ad_id)
        if not ad:
            raise ValueError(f'Advertisement {ad_id} not found')

        # Get target bots
        target_bots = Bot.query.filter(Bot.id.in_(bot_ids or [])).all() if bot_ids else []
        if not target_bots:
            raise ValueError('No target bots specified')

        results = {
            'total_bots': len(target_bots),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for bot in target_bots:
            try:
                # Initialize bot
                telegram_bot = telegram.Bot(token=bot.bot_token)
                
                # Get chat IDs for this bot
                chat_ids = get_bot_chat_ids(bot.id)
                
                # Track metrics for this broadcast
                broadcast_metrics = {
                    'total_recipients': len(chat_ids),
                    'successful': 0,
                    'failed': 0
                }

                # Send message to each chat
                for chat_id in chat_ids:
                    try:
                        # Handle different message types
                        if ad.media_urls:
                            # Send media message
                            send_media_message(telegram_bot, chat_id, ad)
                        else:
                            # Send text message
                            telegram_bot.send_message(
                                chat_id=chat_id,
                                text=ad.content,
                                parse_mode='HTML'
                            )
                        broadcast_metrics['successful'] += 1
                    except Exception as e:
                        broadcast_metrics['failed'] += 1
                        logger.error(f'Error sending message to chat {chat_id}: {str(e)}')

                # Save broadcast metrics
                save_broadcast_metrics(ad.id, bot.id, broadcast_metrics)
                
                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'bot_id': bot.id,
                    'error': str(e)
                })
                logger.error(f'Error broadcasting through bot {bot.id}: {str(e)}')

        # Update advertisement status
        ad.status = 'completed' if results['failed'] == 0 else 'partially_completed'
        ad.completed_at = datetime.utcnow()
        db.session.commit()

        return results
    except Exception as e:
        logger.error(f'Error in broadcast task for ad {ad_id}: {str(e)}')
        ad.status = 'failed'
        db.session.commit()
        raise self.retry(exc=e)

def send_media_message(bot, chat_id, ad):
    """Handle different types of media messages"""
    for media_url in ad.media_urls:
        if media_url.endswith(('.jpg', '.jpeg', '.png')):
            bot.send_photo(chat_id=chat_id, photo=media_url, caption=ad.content)
        elif media_url.endswith(('.mp4', '.avi', '.mov')):
            bot.send_video(chat_id=chat_id, video=media_url, caption=ad.content)
        elif media_url.endswith(('.mp3', '.wav')):
            bot.send_audio(chat_id=chat_id, audio=media_url, caption=ad.content)
        else:
            bot.send_document(chat_id=chat_id, document=media_url, caption=ad.content)

def save_broadcast_metrics(ad_id, bot_id, metrics):
    """Save metrics for the broadcast"""
    analytics = Analytics(
        bot_id=bot_id,
        metric_type='broadcast_metrics',
        metric_value={
            'ad_id': ad_id,
            'timestamp': datetime.utcnow().isoformat(),
            **metrics
        }
    )
    db.session.add(analytics)
    db.session.commit()

@celery.task
def process_scheduled_broadcasts():
    """Process advertisements scheduled for broadcast"""
    now = datetime.utcnow()
    
    # Find ads scheduled for now
    scheduled_ads = Advertisement.query.filter(
        Advertisement.status == 'pending',
        Advertisement.scheduled_for <= now
    ).all()

    for ad in scheduled_ads:
        broadcast_advertisement.delay(ad.id, ad.target_bots)

# Schedule periodic tasks
@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Check for scheduled broadcasts every minute
    sender.add_periodic_task(
        60.0,
        process_scheduled_broadcasts.s(),
        name='check_scheduled_broadcasts'
    )

def get_bot_chat_ids(bot_id):
    """Get all chat IDs for a bot"""
    # TODO: Implement this function to get chat IDs from the database
    # For now, return an empty list
    return []