import logging
import os
from app import create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize Flask app
        app = create_app()
        logger.info("Bot manager started successfully")
        
        # Keep the script running
        while True:
            pass
            
    except Exception as e:
        logger.error(f"Error in bot manager: {str(e)}")
        raise

if __name__ == "__main__":
    main()