"""add created_by to transactions

Revision ID: a1b2c3d4e5f6
Revises: fd8947e03b06
Create Date: 2026-04-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a1b2c3d4e5f6'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_foreign_key('fk_transactions_created_by_users', 'users', ['created_by'], ['id'])


def downgrade():
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transactions_created_by_users', type_='foreignkey')
        batch_op.drop_column('created_by')
