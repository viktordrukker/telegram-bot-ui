import os
import subprocess
from flask import current_app
import logging

class BotManager:
    def __init__(self):
        self.supervisor_conf_dir = '/etc/supervisor/conf.d'
        self.logger = logging.getLogger(__name__)

    def create_bot_config(self, bot):
        """Create supervisor configuration for a bot"""
        config_content = f"""
[program:bot_{bot.id}]
command=python3 /app/bot_scripts/bot_runner.py --token {bot.bot_token}
directory=/app/bot_scripts
autostart=true
autorestart=true
stderr_logfile=/var/log/bot_{bot.id}.err.log
stdout_logfile=/var/log/bot_{bot.id}.out.log
"""
        config_path = os.path.join(self.supervisor_conf_dir, f'bot_{bot.id}.conf')
        
        try:
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Reload supervisor
            subprocess.run(['supervisorctl', 'reread'])
            subprocess.run(['supervisorctl', 'update'])
            
            self.logger.info(f'Created supervisor config for bot {bot.id}')
        except Exception as e:
            self.logger.error(f'Failed to create supervisor config for bot {bot.id}: {str(e)}')
            raise

    def start_bot(self, bot):
        """Start a bot using supervisor"""
        try:
            subprocess.run(['supervisorctl', 'start', f'bot_{bot.id}'])
            self.logger.info(f'Started bot {bot.id}')
        except Exception as e:
            self.logger.error(f'Failed to start bot {bot.id}: {str(e)}')
            raise

    def stop_bot(self, bot):
        """Stop a bot using supervisor"""
        try:
            subprocess.run(['supervisorctl', 'stop', f'bot_{bot.id}'])
            self.logger.info(f'Stopped bot {bot.id}')
        except Exception as e:
            self.logger.error(f'Failed to stop bot {bot.id}: {str(e)}')
            raise

    def restart_bot(self, bot):
        """Restart a bot using supervisor"""
        try:
            subprocess.run(['supervisorctl', 'restart', f'bot_{bot.id}'])
            self.logger.info(f'Restarted bot {bot.id}')
        except Exception as e:
            self.logger.error(f'Failed to restart bot {bot.id}: {str(e)}')
            raise

    def get_bot_status(self, bot):
        """Get bot status from supervisor"""
        try:
            result = subprocess.run(
                ['supervisorctl', 'status', f'bot_{bot.id}'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception as e:
            self.logger.error(f'Failed to get status for bot {bot.id}: {str(e)}')
            raise