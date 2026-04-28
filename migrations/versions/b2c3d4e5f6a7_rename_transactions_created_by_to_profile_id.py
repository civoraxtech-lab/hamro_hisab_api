"""rename transactions.created_by to profile_id

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transactions_created_by_users', type_='foreignkey')
        batch_op.alter_column('created_by', new_column_name='profile_id')
        batch_op.create_foreign_key(
            'fk_transactions_profile_id_profiles', 'profiles', ['profile_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transactions_profile_id_profiles', type_='foreignkey')
        batch_op.alter_column('profile_id', new_column_name='created_by')
        batch_op.create_foreign_key(
            'fk_transactions_created_by_users', 'users', ['created_by'], ['id']
        )
