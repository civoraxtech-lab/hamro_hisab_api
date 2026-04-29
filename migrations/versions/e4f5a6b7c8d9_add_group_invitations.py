"""add group_invitations table

Revision ID: e4f5a6b7c8d9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-29 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e4f5a6b7c8d9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'group_invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invited_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invited_by_profile_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], name='fk_group_invitations_group_id'),
        sa.ForeignKeyConstraint(['invited_user_id'], ['users.id'], name='fk_group_invitations_invited_user_id'),
        sa.ForeignKeyConstraint(['invited_by_profile_id'], ['profiles.id'], name='fk_group_invitations_invited_by_profile_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_group_invitations_group_id', 'group_invitations', ['group_id'])
    op.create_index('ix_group_invitations_invited_user_id', 'group_invitations', ['invited_user_id'])


def downgrade():
    op.drop_index('ix_group_invitations_invited_user_id', table_name='group_invitations')
    op.drop_index('ix_group_invitations_group_id', table_name='group_invitations')
    op.drop_table('group_invitations')
