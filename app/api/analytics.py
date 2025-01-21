from flask import jsonify, request
from app.api import bp
from app.api.auth import token_required
from app.models.analytics import Analytics
from app.models.bot import Bot
from app import db
from datetime import datetime, timedelta

@bp.route('/analytics/dashboard', methods=['GET'])
@token_required
def get_dashboard_metrics(current_user):
    # Get user's bots
    bots = Bot.query.filter_by(user_id=current_user.id).all()
    bot_ids = [bot.id for bot in bots]

    # Get metrics for the last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    metrics = Analytics.query.filter(
        Analytics.bot_id.in_(bot_ids),
        Analytics.timestamp >= since
    ).order_by(Analytics.timestamp.desc()).all()

    # Aggregate metrics
    aggregated = {
        'total_users': 0,
        'total_messages': 0,
        'active_bots': len([bot for bot in bots if bot.status == 'running']),
        'total_bots': len(bots),
        'metrics_by_bot': {}
    }

    for metric in metrics:
        if metric.metric_type == 'users':
            aggregated['total_users'] += metric.metric_value.get('count', 0)
        elif metric.metric_type == 'messages':
            aggregated['total_messages'] += metric.metric_value.get('count', 0)

        # Group metrics by bot
        if metric.bot_id not in aggregated['metrics_by_bot']:
            aggregated['metrics_by_bot'][metric.bot_id] = []
        aggregated['metrics_by_bot'][metric.bot_id].append(metric.to_dict())

    return jsonify(aggregated)

@bp.route('/analytics/bots/<int:bot_id>', methods=['GET'])
@token_required
def get_bot_analytics(current_user, bot_id):
    bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
    if not bot:
        return jsonify({'message': 'Bot not found!'}), 404

    # Get time range from query parameters
    days = int(request.args.get('days', 7))
    since = datetime.utcnow() - timedelta(days=days)

    metrics = Analytics.query.filter(
        Analytics.bot_id == bot_id,
        Analytics.timestamp >= since
    ).order_by(Analytics.timestamp.desc()).all()

    return jsonify([metric.to_dict() for metric in metrics])

@bp.route('/analytics/export', methods=['GET'])
@token_required
def export_analytics(current_user):
    # Get user's bots
    bots = Bot.query.filter_by(user_id=current_user.id).all()
    bot_ids = [bot.id for bot in bots]

    # Get time range from query parameters
    days = int(request.args.get('days', 30))
    since = datetime.utcnow() - timedelta(days=days)

    metrics = Analytics.query.filter(
        Analytics.bot_id.in_(bot_ids),
        Analytics.timestamp >= since
    ).order_by(Analytics.timestamp.desc()).all()

    # Format data for export
    export_data = []
    for metric in metrics:
        bot = next((bot for bot in bots if bot.id == metric.bot_id), None)
        if bot:
            export_data.append({
                'timestamp': metric.timestamp.isoformat(),
                'bot_name': bot.bot_name,
                'metric_type': metric.metric_type,
                'metric_value': metric.metric_value
            })

    return jsonify(export_data)