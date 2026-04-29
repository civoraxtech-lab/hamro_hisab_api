"""add verification status to transactions and liabilities

Revision ID: f6a7b8c9d0e1
Revises: e4f5a6b7c8d9
Create Date: 2026-04-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f6a7b8c9d0e1'
down_revision = 'e4f5a6b7c8d9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('status', sa.String(20), nullable=True, server_default='approved')
        )

    with op.batch_alter_table('liabilities', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('verification_status', sa.String(20), nullable=True, server_default='approved')
        )
        batch_op.add_column(
            sa.Column('verified_via', sa.String(10), nullable=True)
        )
        batch_op.add_column(
            sa.Column('verified_at', sa.DateTime(), nullable=True)
        )
        batch_op.drop_column('is_verified')


def downgrade():
    with op.batch_alter_table('liabilities', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false')
        )
        batch_op.drop_column('verified_at')
        batch_op.drop_column('verified_via')
        batch_op.drop_column('verification_status')

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_column('status')
