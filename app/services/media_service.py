import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional, Tuple, List
import mimetypes

logger = logging.getLogger(__name__)

class MediaService:
    ALLOWED_EXTENSIONS = {
        'image': {'png', 'jpg', 'jpeg', 'gif'},
        'video': {'mp4', 'avi', 'mov'},
        'document': {'pdf', 'doc', 'docx', 'txt'},
        'audio': {'mp3', 'wav', 'ogg'}
    }

    def __init__(self):
        self.storage_type = os.getenv('STORAGE_TYPE', 'local')
        if self.storage_type == 's3':
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION')
            )
            self.bucket_name = os.getenv('S3_BUCKET_NAME')
        else:
            self.upload_folder = os.path.join(current_app.root_path, 'uploads')
            os.makedirs(self.upload_folder, exist_ok=True)

    def allowed_file(self, filename: str) -> Tuple[bool, Optional[str]]:
        """Check if the file extension is allowed"""
        if '.' not in filename:
            return False, None
        
        ext = filename.rsplit('.', 1)[1].lower()
        for media_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return True, media_type
        return False, None

    def get_mime_type(self, filename: str) -> str:
        """Get MIME type for the file"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    def save_file(self, file, filename: str) -> Tuple[str, str, str]:
        """Save file and return URL, media type, and MIME type"""
        allowed, media_type = self.allowed_file(filename)
        if not allowed:
            raise ValueError('File type not allowed')

        secure_name = secure_filename(filename)
        unique_filename = f"{uuid.uuid4()}_{secure_name}"
        mime_type = self.get_mime_type(filename)

        if self.storage_type == 's3':
            return self._save_to_s3(file, unique_filename, mime_type), media_type, mime_type
        else:
            return self._save_to_local(file, unique_filename), media_type, mime_type

    def _save_to_s3(self, file, filename: str, mime_type: str) -> str:
        """Save file to S3 and return URL"""
        try:
            extra_args = {
                'ContentType': mime_type,
                'ACL': 'public-read'
            }
            
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                filename,
                ExtraArgs=extra_args
            )

            url = f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
            return url

        except ClientError as e:
            logger.error(f"Error uploading file to S3: {str(e)}")
            raise

    def _save_to_local(self, file, filename: str) -> str:
        """Save file locally and return URL"""
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        
        # Return URL for local file
        return f"/uploads/{filename}"

    def delete_file(self, url: str) -> bool:
        """Delete file from storage"""
        try:
            if self.storage_type == 's3':
                filename = url.split('/')[-1]
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=filename
                )
            else:
                if url.startswith('/uploads/'):
                    filename = url.split('/')[-1]
                    file_path = os.path.join(self.upload_folder, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def get_file_info(self, url: str) -> dict:
        """Get file information"""
        filename = url.split('/')[-1]
        original_filename = '_'.join(filename.split('_')[1:])  # Remove UUID prefix
        mime_type = self.get_mime_type(original_filename)
        _, media_type = self.allowed_file(original_filename)

        return {
            'url': url,
            'filename': original_filename,
            'mime_type': mime_type,
            'media_type': media_type
        }

media_service = MediaService()