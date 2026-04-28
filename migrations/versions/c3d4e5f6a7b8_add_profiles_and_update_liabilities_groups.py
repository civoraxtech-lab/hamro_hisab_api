"""add profiles table and update liabilities/groups to use profile_id

Revision ID: c3d4e5f6a7b8
Revises: fd8947e03b06
Create Date: 2026-04-28 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c3d4e5f6a7b8'
down_revision = 'fd8947e03b06'
branch_labels = None
depends_on = None


def upgrade():
    # Create profiles table
    op.create_table(
        'profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_profiles_user_id_users'),
        sa.PrimaryKeyConstraint('id'),
    )

    # liabilities: drop user_id FK + column, add profile_id column + FK
    with op.batch_alter_table('liabilities', schema=None) as batch_op:
        batch_op.drop_constraint('liabilities_user_id_fkey', type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.add_column(sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_foreign_key(
            'fk_liabilities_profile_id_profiles', 'profiles', ['profile_id'], ['id']
        )

    # groups: rewire created_by FK from users → profiles
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_constraint('groups_created_by_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_groups_created_by_profiles', 'profiles', ['created_by'], ['id']
        )


def downgrade():
    # groups: revert created_by FK back to users
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_constraint('fk_groups_created_by_profiles', type_='foreignkey')
        batch_op.create_foreign_key(
            'groups_created_by_fkey', 'users', ['created_by'], ['id']
        )

    # liabilities: drop profile_id, restore user_id
    with op.batch_alter_table('liabilities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_liabilities_profile_id_profiles', type_='foreignkey')
        batch_op.drop_column('profile_id')
        batch_op.add_column(sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.create_foreign_key(
            'liabilities_user_id_fkey', 'users', ['user_id'], ['id']
        )

    op.drop_table('profiles')
