"""create device_tokens table

Revision ID: d601414f493f
Revises: b2c3d4e5f6a7
Create Date: 2026-04-29 13:50:33.949891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd601414f493f'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'device_tokens',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.UUID, sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('fcm_token', sa.String(255), nullable=False, index=True),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('browser', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true'))
    )

def downgrade():
    op.drop_table('device_tokens')
