import pandas as pd
import io
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app import db
from app.models.bot import Bot
from app.models.analytics import Analytics
from app.models.advertisement import Advertisement
from app.models.message import Message
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.export_formats = {
            'csv': self._export_csv,
            'excel': self._export_excel,
            'json': self._export_json
        }

    def get_bot_metrics(self, bot_id, start_date=None, end_date=None):
        """Get metrics for a specific bot"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()

            metrics = Analytics.query.filter(
                Analytics.bot_id == bot_id,
                Analytics.timestamp.between(start_date, end_date)
            ).order_by(Analytics.timestamp.desc()).all()

            # Aggregate metrics
            aggregated = {
                'total_users': 0,
                'total_messages': 0,
                'message_types': {},
                'hourly_activity': {},
                'ads_performance': {}
            }

            for metric in metrics:
                if metric.metric_type == 'users':
                    aggregated['total_users'] += metric.metric_value.get('count', 0)
                elif metric.metric_type == 'messages':
                    aggregated['total_messages'] += metric.metric_value.get('count', 0)
                    for msg_type, count in metric.metric_value.get('types', {}).items():
                        aggregated['message_types'][msg_type] = (
                            aggregated['message_types'].get(msg_type, 0) + count
                        )
                elif metric.metric_type == 'hourly_stats':
                    hour = metric.timestamp.strftime('%Y-%m-%d %H:00')
                    aggregated['hourly_activity'][hour] = metric.metric_value

            return aggregated
        except Exception as e:
            logger.error(f'Error getting bot metrics: {str(e)}')
            raise

    def get_advertisement_metrics(self, ad_id):
        """Get metrics for a specific advertisement"""
        try:
            metrics = Analytics.query.filter(
                Analytics.metric_type == 'broadcast_metrics',
                Analytics.metric_value['ad_id'].astext.cast(db.Integer) == ad_id
            ).all()

            aggregated = {
                'total_recipients': 0,
                'successful': 0,
                'failed': 0,
                'bots': {},
                'timeline': []
            }

            for metric in metrics:
                data = metric.metric_value
                aggregated['total_recipients'] += data.get('total_recipients', 0)
                aggregated['successful'] += data.get('successful', 0)
                aggregated['failed'] += data.get('failed', 0)
                
                bot_id = str(metric.bot_id)
                if bot_id not in aggregated['bots']:
                    aggregated['bots'][bot_id] = {
                        'total': 0,
                        'successful': 0,
                        'failed': 0
                    }
                
                bot_stats = aggregated['bots'][bot_id]
                bot_stats['total'] += data.get('total_recipients', 0)
                bot_stats['successful'] += data.get('successful', 0)
                bot_stats['failed'] += data.get('failed', 0)

                aggregated['timeline'].append({
                    'timestamp': metric.timestamp.isoformat(),
                    'bot_id': bot_id,
                    'metrics': data
                })

            return aggregated
        except Exception as e:
            logger.error(f'Error getting advertisement metrics: {str(e)}')
            raise

    def export_bot_analytics(self, bot_id, format='csv', start_date=None, end_date=None):
        """Export bot analytics in specified format"""
        try:
            if format not in self.export_formats:
                raise ValueError(f'Unsupported format: {format}')

            # Get metrics
            metrics = self.get_bot_metrics(bot_id, start_date, end_date)
            
            # Get messages
            messages = Message.query.filter(
                Message.bot_id == bot_id,
                Message.sent_at.between(start_date, end_date)
            ).all()

            # Get advertisements
            ads = Advertisement.query.join(
                Analytics,
                and_(
                    Analytics.metric_type == 'broadcast_metrics',
                    Analytics.bot_id == bot_id
                )
            ).filter(
                Advertisement.created_at.between(start_date, end_date)
            ).all()

            # Prepare data for export
            export_data = {
                'metrics': metrics,
                'messages': [msg.to_dict() for msg in messages],
                'advertisements': [ad.to_dict() for ad in ads]
            }

            # Export in requested format
            return self.export_formats[format](export_data)
        except Exception as e:
            logger.error(f'Error exporting bot analytics: {str(e)}')
            raise

    def _export_csv(self, data):
        """Export data as CSV"""
        output = io.StringIO()
        
        # Export metrics
        metrics_df = pd.DataFrame({
            'Metric': ['Total Users', 'Total Messages'],
            'Value': [data['metrics']['total_users'], data['metrics']['total_messages']]
        })
        metrics_df.to_csv(output, index=False)
        output.write('\n')

        # Export message types
        msg_types_df = pd.DataFrame([
            {'Type': k, 'Count': v}
            for k, v in data['metrics']['message_types'].items()
        ])
        msg_types_df.to_csv(output, index=False)
        output.write('\n')

        # Export hourly activity
        hourly_df = pd.DataFrame([
            {'Hour': k, **v}
            for k, v in data['metrics']['hourly_activity'].items()
        ])
        hourly_df.to_csv(output, index=False)
        output.write('\n')

        # Export messages
        messages_df = pd.DataFrame(data['messages'])
        messages_df.to_csv(output, index=False)
        output.write('\n')

        # Export advertisements
        ads_df = pd.DataFrame(data['advertisements'])
        ads_df.to_csv(output, index=False)

        return output.getvalue()

    def _export_excel(self, data):
        """Export data as Excel"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Export metrics
            metrics_df = pd.DataFrame({
                'Metric': ['Total Users', 'Total Messages'],
                'Value': [data['metrics']['total_users'], data['metrics']['total_messages']]
            })
            metrics_df.to_excel(writer, sheet_name='Summary', index=False)

            # Export message types
            msg_types_df = pd.DataFrame([
                {'Type': k, 'Count': v}
                for k, v in data['metrics']['message_types'].items()
            ])
            msg_types_df.to_excel(writer, sheet_name='Message Types', index=False)

            # Export hourly activity
            hourly_df = pd.DataFrame([
                {'Hour': k, **v}
                for k, v in data['metrics']['hourly_activity'].items()
            ])
            hourly_df.to_excel(writer, sheet_name='Hourly Activity', index=False)

            # Export messages
            messages_df = pd.DataFrame(data['messages'])
            messages_df.to_excel(writer, sheet_name='Messages', index=False)

            # Export advertisements
            ads_df = pd.DataFrame(data['advertisements'])
            ads_df.to_excel(writer, sheet_name='Advertisements', index=False)

        return output.getvalue()

    def _export_json(self, data):
        """Export data as JSON"""
        return data

analytics_service = AnalyticsService()