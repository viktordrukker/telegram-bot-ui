"""User management

Revision ID: 002
Revises: 001
Create Date: 2024-01-21 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to users table
    op.add_column('users', sa.Column('email', sa.String(120), unique=True))
    op.add_column('users', sa.Column('status', sa.String(20), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('last_login', sa.DateTime))
    op.add_column('users', sa.Column('last_active', sa.DateTime))

    # Create user_api_keys table
    op.create_table(
        'user_api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key_hash', sa.String(128), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime()),
        sa.Column('expires_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_activities table
    op.create_table(
        'user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('details', sa.JSON()),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_preferences', sa.JSON(), nullable=False),
        sa.Column('theme', sa.String(20), nullable=False, server_default='light'),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'),
        sa.Column('language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('dashboard_layout', sa.JSON()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create default settings for existing users
    conn = op.get_bind()
    users = conn.execute('SELECT id FROM users').fetchall()
    default_preferences = {
        'email': True,
        'web': True,
        'bot_status': True,
        'broadcast_status': True,
        'security_alerts': True
    }
    
    for user in users:
        conn.execute(
            'INSERT INTO user_settings (user_id, notification_preferences) VALUES (:user_id, :prefs)',
            user_id=user[0],
            prefs=default_preferences
        )

def downgrade():
    op.drop_table('user_settings')
    op.drop_table('user_activities')
    op.drop_table('user_api_keys')
    op.drop_column('users', 'last_active')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'status')
    op.drop_column('users', 'email')