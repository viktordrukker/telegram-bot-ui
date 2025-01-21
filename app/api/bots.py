from flask import jsonify, request, current_app
from app.api import bp
from app.api.auth import token_required
from app.models.bot import Bot
from app.models.analytics import Analytics
from app import db
from app.services.bot_manager import BotManager
import subprocess

bot_manager = BotManager()

@bp.route('/bots', methods=['GET'])
@token_required
def get_bots(current_user):
    bots = Bot.query.filter_by(user_id=current_user.id).all()
    return jsonify([bot.to_dict() for bot in bots])

@bp.route('/bots', methods=['POST'])
@token_required
def add_bot(current_user):
    data = request.get_json()

    if not data or not data.get('bot_token') or not data.get('bot_name'):
        return jsonify({'message': 'Missing required fields!'}), 400

    if Bot.query.filter_by(bot_token=data['bot_token']).first():
        return jsonify({'message': 'Bot already exists!'}), 400

    new_bot = Bot(
        user_id=current_user.id,
        bot_token=data['bot_token'],
        bot_name=data['bot_name']
    )
    
    db.session.add(new_bot)
    db.session.commit()

    # Create supervisor config for the bot
    try:
        bot_manager.create_bot_config(new_bot)
    except Exception as e:
        current_app.logger.error(f'Failed to create bot config: {str(e)}')
        return jsonify({'message': 'Failed to configure bot!'}), 500

    return jsonify({
        'message': 'Bot added successfully!',
        'bot': new_bot.to_dict()
    }), 201

@bp.route('/bots/<int:bot_id>/start', methods=['POST'])
@token_required
def start_bot(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found!'}), 404

    try:
        bot_manager.start_bot(bot)
        bot.update_status('running')
    except Exception as e:
        current_app.logger.error(f'Failed to start bot: {str(e)}')
        return jsonify({'message': 'Failed to start bot!'}), 500

    return jsonify({'message': 'Bot started successfully!'})

@bp.route('/bots/<int:bot_id>/stop', methods=['POST'])
@token_required
def stop_bot(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found!'}), 404

    try:
        bot_manager.stop_bot(bot)
        bot.update_status('stopped')
    except Exception as e:
        current_app.logger.error(f'Failed to stop bot: {str(e)}')
        return jsonify({'message': 'Failed to stop bot!'}), 500

    return jsonify({'message': 'Bot stopped successfully!'})

@bp.route('/bots/<int:bot_id>/restart', methods=['POST'])
@token_required
def restart_bot(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found!'}), 404

    try:
        bot_manager.restart_bot(bot)
        bot.update_status('running')
    except Exception as e:
        current_app.logger.error(f'Failed to restart bot: {str(e)}')
        return jsonify({'message': 'Failed to restart bot!'}), 500

    return jsonify({'message': 'Bot restarted successfully!'})

@bp.route('/bots/<int:bot_id>/status', methods=['GET'])
@token_required
def get_bot_status(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found!'}), 404

    return jsonify({'status': bot.status})

@bp.route('/bots/<int:bot_id>/metrics', methods=['GET'])
@token_required
def get_bot_metrics(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found!'}), 404

    metrics = Analytics.query.filter_by(bot_id=bot_id).order_by(Analytics.timestamp.desc()).limit(100).all()
    return jsonify([metric.to_dict() for metric in metrics])