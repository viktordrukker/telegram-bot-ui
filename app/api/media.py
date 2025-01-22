from flask import jsonify, request, send_from_directory, current_app
from app.api import bp
from app.api.auth import token_required
from app.services.media_service import media_service
import os

@bp.route('/media/upload', methods=['POST'])
@token_required
def upload_media(current_user):
    """Upload media file"""
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    try:
        url, media_type, mime_type = media_service.save_file(file, file.filename)
        return jsonify({
            'url': url,
            'media_type': media_type,
            'mime_type': mime_type,
            'filename': file.filename
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Error uploading file: {str(e)}')
        return jsonify({'message': 'Failed to upload file'}), 500

@bp.route('/media/<path:filename>')
@token_required
def serve_media(current_user, filename):
    """Serve media files in development"""
    if os.getenv('STORAGE_TYPE') != 'local':
        return jsonify({'message': 'Not available in production'}), 404
    
    try:
        return send_from_directory(
            os.path.join(current_app.root_path, 'uploads'),
            filename
        )
    except Exception as e:
        current_app.logger.error(f'Error serving file: {str(e)}')
        return jsonify({'message': 'File not found'}), 404

@bp.route('/media', methods=['DELETE'])
@token_required
def delete_media(current_user):
    """Delete media file"""
    url = request.json.get('url')
    if not url:
        return jsonify({'message': 'URL is required'}), 400

    try:
        if media_service.delete_file(url):
            return jsonify({'message': 'File deleted successfully'})
        return jsonify({'message': 'Failed to delete file'}), 500
    except Exception as e:
        current_app.logger.error(f'Error deleting file: {str(e)}')
        return jsonify({'message': 'Failed to delete file'}), 500

@bp.route('/media/info')
@token_required
def get_media_info(current_user):
    """Get media file information"""
    url = request.args.get('url')
    if not url:
        return jsonify({'message': 'URL is required'}), 400

    try:
        info = media_service.get_file_info(url)
        return jsonify(info)
    except Exception as e:
        current_app.logger.error(f'Error getting file info: {str(e)}')
        return jsonify({'message': 'Failed to get file information'}), 500