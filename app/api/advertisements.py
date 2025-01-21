from flask import jsonify, request, current_app
from app.api import bp
from app.api.auth import token_required
from app.models.advertisement import Advertisement
from app.models.bot import Bot
from app import db
from datetime import datetime

@bp.route('/advertisements', methods=['GET'])
@token_required
def get_advertisements(current_user):
    ads = Advertisement.query.filter_by(user_id=current_user.id).all()
    return jsonify([ad.to_dict() for ad in ads])

@bp.route('/advertisements', methods=['POST'])
@token_required
def create_advertisement(current_user):
    data = request.get_json()

    if not data or not data.get('content') or not data.get('price'):
        return jsonify({'message': 'Missing required fields!'}), 400

    new_ad = Advertisement(
        user_id=current_user.id,
        content=data['content'],
        media_urls=data.get('media_urls'),
        price=data['price'],
        scheduled_for=datetime.fromisoformat(data['scheduled_for']) if data.get('scheduled_for') else None
    )
    
    db.session.add(new_ad)
    db.session.commit()

    return jsonify({
        'message': 'Advertisement created successfully!',
        'advertisement': new_ad.to_dict()
    }), 201

@bp.route('/advertisements/<int:ad_id>/broadcast', methods=['POST'])
@token_required
def broadcast_advertisement(current_user, ad_id):
    ad = Advertisement.query.filter_by(id=ad_id, user_id=current_user.id).first()
    if not ad:
        return jsonify({'message': 'Advertisement not found!'}), 404

    data = request.get_json()
    bot_ids = data.get('bot_ids', [])

    if not bot_ids:
        return jsonify({'message': 'No bots selected for broadcast!'}), 400

    # Verify bot ownership and status
    bots = Bot.query.filter(
        Bot.id.in_(bot_ids),
        Bot.user_id == current_user.id,
        Bot.status == 'running'
    ).all()

    if not bots:
        return jsonify({'message': 'No valid bots found for broadcast!'}), 400

    try:
        # Start broadcasting process
        ad.status = 'broadcasting'
        db.session.commit()

        # TODO: Implement actual broadcasting logic
        # This should be handled by a background task

        return jsonify({'message': 'Broadcasting started successfully!'})
    except Exception as e:
        current_app.logger.error(f'Failed to broadcast advertisement: {str(e)}')
        return jsonify({'message': 'Failed to start broadcasting!'}), 500

@bp.route('/advertisements/<int:ad_id>/status', methods=['GET'])
@token_required
def get_advertisement_status(current_user, ad_id):
    ad = Advertisement.query.filter_by(id=ad_id, user_id=current_user.id).first()
    if not ad:
        return jsonify({'message': 'Advertisement not found!'}), 404

    return jsonify({'status': ad.status})