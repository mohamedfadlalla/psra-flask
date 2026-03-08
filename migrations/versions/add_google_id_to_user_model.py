"""add google_id to user model

Revision ID: add_google_id
Revises: 
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_google_id_to_user'
down_revision = '9da5f9cf5f7e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('google_id', sa.String(100), nullable=True))
        batch_op.create_index('ix_user_google_id', ['google_id'], unique=True)
        batch_op.alter_column('password_hash',
                        existing_type=sa.String(128),
                        nullable=True)


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_index('ix_user_google_id')
        batch_op.drop_column('google_id')
        batch_op.alter_column('password_hash',
                        existing_type=sa.String(128),
                        nullable=False)
