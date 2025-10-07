"""create lyric table

Revision ID: 0001_create_lyric_table
Revises: 
Create Date: 2025-10-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_lyric_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'lyric',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('genre', sa.String(length=100), nullable=False),
        sa.Column('bpm', sa.Integer, nullable=False),
        sa.Column('mood', sa.String(length=100), nullable=False),
        sa.Column('theme', sa.String(length=200), nullable=False),
        sa.Column('lyrics', sa.Text, nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('lyric')
