"""add job applications table

Revision ID: 232e10052396
Revises: eb8617734a0a
Create Date: 2026-02-20 15:06:15.873909

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '232e10052396'
down_revision = 'eb8617734a0a'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    if 'job_applications' not in inspector.get_table_names():
        op.create_table(
            'job_applications',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('job_id', sa.Integer(), nullable=False),
            sa.Column('applicant_id', sa.Integer(), nullable=False),
            sa.Column('cover_letter', sa.Text(), nullable=True),
            sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='applicationstatus', create_type=False), nullable=True),
            sa.Column('applied_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['applicant_id'], ['user.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if 'job_applications' in inspector.get_table_names():
        op.drop_table('job_applications')
