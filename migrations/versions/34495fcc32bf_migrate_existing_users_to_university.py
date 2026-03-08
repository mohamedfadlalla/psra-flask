"""migrate existing users to university

Revision ID: 34495fcc32bf
Revises: 820e3367e38f
Create Date: 2026-03-08 22:53:26.137331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34495fcc32bf'
down_revision = '820e3367e38f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE profiles SET university_id = 1 WHERE university_id IS NULL")
    op.execute("UPDATE departments SET university_id = 1 WHERE university_id IS NULL")

def downgrade():
    op.execute("UPDATE profiles SET university_id = NULL WHERE university_id = 1")
    op.execute("UPDATE departments SET university_id = NULL WHERE university_id = 1")
