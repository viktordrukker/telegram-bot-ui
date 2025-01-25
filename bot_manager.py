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
    """Entry point for bot management service"""
    try:
        app = create_app()
        logger.info("Initialized bot manager application")
        
        # Start background scheduler
        from app.tasks import scheduler
        scheduler.start()
        
        return app

    except Exception as e:
        logger.critical(f"Failed to initialize bot manager: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()