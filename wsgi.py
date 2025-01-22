from app import create_app
from flask import send_from_directory, current_app
import os

app = create_app()

# Serve static files and handle SPA routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve(path):
    if path != 'index.html' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    
    # Log the request for debugging
    current_app.logger.info(f'Serving index.html for path: {path}')
    current_app.logger.info(f'Static folder: {app.static_folder}')
    current_app.logger.info(f'Files in static: {os.listdir(app.static_folder) if os.path.exists(app.static_folder) else "folder not found"}')
    
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)