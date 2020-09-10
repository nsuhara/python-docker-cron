"""Create Table
Revision ID: 62fb1bcf0a8a
Revises:
Create Date: 2020-09-09 21:03:07.509339
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as db

# revision identifiers, used by Alembic.
revision = '62fb1bcf0a8a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'qiita',
        sa.Column('id', db.INTEGER, primary_key=True),
        sa.Column('date', db.DATE, nullable=False),
        sa.Column('title', db.VARCHAR(255), nullable=False),
        sa.Column('page_views_count', db.INTEGER, nullable=False),
        sa.Column('likes_count', db.INTEGER, nullable=False),
        sa.Column('url', db.VARCHAR(255), nullable=False),
        sa.Column('created_at', db.TIMESTAMP, nullable=False),
    )


def downgrade():
    pass
