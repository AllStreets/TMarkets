"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('change_pct', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_market_data_fetched_at'), 'market_data', ['fetched_at'], unique=False)
    op.create_index(op.f('ix_market_data_symbol'), 'market_data', ['symbol'], unique=False)

    op.create_table(
        'trump_signals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('posted_at', sa.DateTime(), nullable=False),
        sa.Column('signal_type', sa.String(length=50), nullable=True),
        sa.Column('affected_tickers', sa.JSON(), nullable=True),
        sa.Column('affected_sectors', sa.JSON(), nullable=True),
        sa.Column('directional_bias', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('llm_reasoning', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_trump_signals_posted_at'), 'trump_signals', ['posted_at'], unique=False)

    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('signal_id', sa.Integer(), nullable=False),
        sa.Column('buy_list', sa.JSON(), nullable=False),
        sa.Column('short_list', sa.JSON(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('horizon_days', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_predictions_created_at'), 'predictions', ['created_at'], unique=False)
    op.create_index(op.f('ix_predictions_signal_id'), 'predictions', ['signal_id'], unique=False)

    op.create_table(
        'news_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('headline', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_news_articles_published_at'), 'news_articles', ['published_at'], unique=False)

    op.create_table(
        'macro_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('indicator', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_macro_data_indicator'), 'macro_data', ['indicator'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_macro_data_indicator'), table_name='macro_data')
    op.drop_table('macro_data')
    op.drop_index(op.f('ix_news_articles_published_at'), table_name='news_articles')
    op.drop_table('news_articles')
    op.drop_index(op.f('ix_predictions_signal_id'), table_name='predictions')
    op.drop_index(op.f('ix_predictions_created_at'), table_name='predictions')
    op.drop_table('predictions')
    op.drop_index(op.f('ix_trump_signals_posted_at'), table_name='trump_signals')
    op.drop_table('trump_signals')
    op.drop_index(op.f('ix_market_data_symbol'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_fetched_at'), table_name='market_data')
    op.drop_table('market_data')
