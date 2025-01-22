from flask import jsonify, request, current_app
from app.api import bp
from app.api.auth import token_required
from app.models.advertisement import Advertisement
from app.models.bot import Bot
from app import db
from datetime import datetime
from app.tasks.ad_tasks import broadcast_advertisement as broadcast_task

@bp.route('/advertisements', methods=['GET'])
@token_required
def get_advertisements(current_user):
    ads = Advertisement.query.filter_by(user_id=current_user.id).order_by(Advertisement.created_at.desc()).all()
    return jsonify([ad.to_dict() for ad in ads])

@bp.route('/advertisements', methods=['POST'])
@token_required
def create_advertisement(current_user):
    data = request.get_json()

    required_fields = ['title', 'content', 'price', 'target_bots']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields!'}), 400

    try:
        new_ad = Advertisement(
            user_id=current_user.id,
            title=data['title'],
            content=data['content'],
            media_urls=data.get('media_urls', []),
            price=float(data['price']),
            target_bots=data['target_bots'],
            status='pending',
            scheduled_for=datetime.fromisoformat(data['scheduled_for']) if data.get('scheduled_for') else None
        )
        
        db.session.add(new_ad)
        db.session.commit()

        # If not scheduled, broadcast immediately
        if not new_ad.scheduled_for:
            broadcast_task.delay(new_ad.id, new_ad.target_bots)
            new_ad.status = 'broadcasting'
            db.session.commit()

        return jsonify({
            'message': 'Advertisement created successfully!',
            'advertisement': new_ad.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Failed to create advertisement: {str(e)}')
        return jsonify({'message': 'Failed to create advertisement!'}), 500

@bp.route('/advertisements/<int:ad_id>/broadcast', methods=['POST'])
@token_required
def broadcast_advertisement(current_user, ad_id):
    ad = Advertisement.query.filter_by(id=ad_id, user_id=current_user.id).first()
    if not ad:
        return jsonify({'message': 'Advertisement not found!'}), 404

    if ad.status == 'broadcasting':
        return jsonify({'message': 'Advertisement is already broadcasting!'}), 400

    # Verify bot status
    bots = Bot.query.filter(
        Bot.id.in_(ad.target_bots),
        Bot.user_id == current_user.id,
        Bot.status == 'running'
    ).all()

    if not bots:
        return jsonify({'message': 'No active bots found for broadcast!'}), 400

    try:
        # Start broadcasting process
        ad.status = 'broadcasting'
        db.session.commit()

        # Start background task
        broadcast_task.delay(ad.id, ad.target_bots)

        return jsonify({
            'message': 'Broadcasting started successfully!',
            'advertisement': ad.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f'Failed to broadcast advertisement: {str(e)}')
        return jsonify({'message': 'Failed to start broadcasting!'}), 500

@bp.route('/advertisements/<int:ad_id>', methods=['DELETE'])
@token_required
def delete_advertisement(current_user, ad_id):
    ad = Advertisement.query.filter_by(id=ad_id, user_id=current_user.id).first()
    if not ad:
        return jsonify({'message': 'Advertisement not found!'}), 404

    if ad.status == 'broadcasting':
        return jsonify({'message': 'Cannot delete advertisement while broadcasting!'}), 400

    try:
        db.session.delete(ad)
        db.session.commit()
        return jsonify({'message': 'Advertisement deleted successfully!'})
    except Exception as e:
        current_app.logger.error(f'Failed to delete advertisement: {str(e)}')
        return jsonify({'message': 'Failed to delete advertisement!'}), 500

@bp.route('/advertisements/<int:ad_id>/status', methods=['GET'])
@token_required
def get_advertisement_status(current_user, ad_id):
    ad = Advertisement.query.filter_by(id=ad_id, user_id=current_user.id).first()
    if not ad:
        return jsonify({'message': 'Advertisement not found!'}), 404

    # Get broadcast metrics if available
    metrics = None
    if ad.status in ['broadcasting', 'completed', 'partially_completed']:
        metrics = get_broadcast_metrics(ad.id)

    return jsonify({
        'status': ad.status,
        'metrics': metrics,
        'scheduled_for': ad.scheduled_for.isoformat() if ad.scheduled_for else None,
        'completed_at': ad.completed_at.isoformat() if ad.completed_at else None
    })

def get_broadcast_metrics(ad_id):
    """Get aggregated metrics for an advertisement broadcast"""
    from app.models.analytics import Analytics
    
    metrics = Analytics.query.filter(
        Analytics.metric_type == 'broadcast_metrics',
        Analytics.metric_value['ad_id'].astext.cast(db.Integer) == ad_id
    ).all()

    if not metrics:
        return None

    aggregated = {
        'total_recipients': 0,
        'successful': 0,
        'failed': 0,
        'bots': len(metrics)
    }

    for metric in metrics:
        data = metric.metric_value
        aggregated['total_recipients'] += data.get('total_recipients', 0)
        aggregated['successful'] += data.get('successful', 0)
        aggregated['failed'] += data.get('failed', 0)

    return aggregated