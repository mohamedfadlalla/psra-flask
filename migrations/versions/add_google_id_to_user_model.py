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
    # Add google_id column to user table
    op.add_column('user', sa.Column('google_id', sa.String(100), nullable=True))
    
    # Create unique index on google_id
    op.create_index('ix_user_google_id', 'user', ['google_id'], unique=True)
    
    # Make password_hash nullable
    op.alter_column('user', 'password_hash',
                    existing_type=sa.String(128),
                    nullable=True)


def downgrade():
    # Remove google_id column
    op.drop_index('ix_user_google_id', table_name='user')
    op.drop_column('user', 'google_id')
    
    # Make password_hash not nullable
    op.alter_column('user', 'password_hash',
                    existing_type=sa.String(128),
                    nullable=False)