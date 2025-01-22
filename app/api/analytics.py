from flask import jsonify, request, current_app, send_file
from app.api import bp
from app.api.auth import token_required
from app.models.analytics import Analytics
from app.models.bot import Bot
from app.models.advertisement import Advertisement
from app.services.analytics_service import analytics_service
from app import db
from datetime import datetime, timedelta
import io
import logging

logger = logging.getLogger(__name__)

@bp.route('/analytics/dashboard', methods=['GET'])
@token_required
def get_dashboard_metrics(current_user):
    try:
        # Get time range
        time_range = request.args.get('range', '24h')
        if time_range == '7d':
            since = datetime.utcnow() - timedelta(days=7)
        elif time_range == '30d':
            since = datetime.utcnow() - timedelta(days=30)
        else:  # 24h default
            since = datetime.utcnow() - timedelta(hours=24)

        # Get user's bots
        bots = Bot.query.filter_by(user_id=current_user.id).all()
        bot_ids = [bot.id for bot in bots]

        # Get metrics
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
            'metrics_by_bot': {},
            'message_types': {},
            'user_activity': [],
            'bot_performance': []
        }

        for metric in metrics:
            if metric.metric_type == 'users':
                aggregated['total_users'] += metric.metric_value.get('count', 0)
            elif metric.metric_type == 'messages':
                aggregated['total_messages'] += metric.metric_value.get('count', 0)
                # Aggregate message types
                for msg_type, count in metric.metric_value.get('types', {}).items():
                    aggregated['message_types'][msg_type] = (
                        aggregated['message_types'].get(msg_type, 0) + count
                    )

            # Group metrics by bot
            if metric.bot_id not in aggregated['metrics_by_bot']:
                bot = next((b for b in bots if b.id == metric.bot_id), None)
                if bot:
                    aggregated['metrics_by_bot'][metric.bot_id] = {
                        'id': bot.id,
                        'name': bot.bot_name,
                        'metrics': []
                    }
            if metric.bot_id in aggregated['metrics_by_bot']:
                aggregated['metrics_by_bot'][metric.bot_id]['metrics'].append(metric.to_dict())

        # Format for charts
        for bot_id, data in aggregated['metrics_by_bot'].items():
            bot_metrics = {
                'id': data['id'],
                'name': data['name'],
                'users': 0,
                'messages': 0,
                'success_rate': 0
            }
            for metric in data['metrics']:
                if metric['metric_type'] == 'users':
                    bot_metrics['users'] += metric['metric_value'].get('count', 0)
                elif metric['metric_type'] == 'messages':
                    bot_metrics['messages'] += metric['metric_value'].get('count', 0)
            
            if bot_metrics['messages'] > 0:
                bot_metrics['success_rate'] = (
                    (bot_metrics['messages'] - metric['metric_value'].get('failed', 0))
                    / bot_metrics['messages'] * 100
                )
            
            aggregated['bot_performance'].append(bot_metrics)

        return jsonify(aggregated)
    except Exception as e:
        logger.error(f'Error getting dashboard metrics: {str(e)}')
        return jsonify({'message': 'Failed to get dashboard metrics'}), 500

@bp.route('/analytics/bots/<int:bot_id>', methods=['GET'])
@token_required
def get_bot_analytics(current_user, bot_id):
    try:
        bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
        if not bot:
            return jsonify({'message': 'Bot not found!'}), 404

        # Get time range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)

        metrics = analytics_service.get_bot_metrics(bot_id, start_date, end_date)
        return jsonify(metrics)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f'Error getting bot analytics: {str(e)}')
        return jsonify({'message': 'Failed to get bot analytics'}), 500

@bp.route('/analytics/bots/<int:bot_id>/export', methods=['GET'])
@token_required
def export_bot_analytics(current_user, bot_id):
    try:
        bot = Bot.query.filter_by(id=bot_id, user_id=current_user.id).first()
        if not bot:
            return jsonify({'message': 'Bot not found!'}), 404

        # Get parameters
        format = request.args.get('format', 'csv')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)

        # Get export data
        export_data = analytics_service.export_bot_analytics(
            bot_id,
            format=format,
            start_date=start_date,
            end_date=end_date
        )

        # Prepare response
        if format == 'json':
            return jsonify(export_data)
        else:
            # Create in-memory file
            file_data = io.BytesIO()
            if format == 'csv':
                file_data.write(export_data.encode('utf-8'))
                mimetype = 'text/csv'
                extension = 'csv'
            else:  # excel
                file_data.write(export_data)
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                extension = 'xlsx'

            file_data.seek(0)
            filename = f'bot_{bot_id}_analytics_{datetime.now().strftime("%Y%m%d")}.{extension}'
            
            return send_file(
                file_data,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f'Error exporting bot analytics: {str(e)}')
        return jsonify({'message': 'Failed to export analytics'}), 500

@bp.route('/analytics/advertisements/<int:ad_id>', methods=['GET'])
@token_required
def get_advertisement_analytics(current_user, ad_id):
    try:
        # Verify advertisement ownership
        ad = Advertisement.query.filter_by(id=ad_id, user_id=current_user.id).first()
        if not ad:
            return jsonify({'message': 'Advertisement not found!'}), 404

        metrics = analytics_service.get_advertisement_metrics(ad_id)
        return jsonify(metrics)
    except Exception as e:
        logger.error(f'Error getting advertisement analytics: {str(e)}')
        return jsonify({'message': 'Failed to get advertisement analytics'}), 500