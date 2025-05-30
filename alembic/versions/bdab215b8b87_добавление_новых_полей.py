"""Добавление новых полей

Revision ID: bdab215b8b87
Revises: 27d58246ac44
Create Date: 2025-03-16 03:22:31.928849

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdab215b8b87'
down_revision: Union[str, None] = '27d58246ac44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('avito_accounts', sa.Column('refresh_token', sa.Integer(), nullable=True))
    op.add_column('avito_accounts', sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('avito_accounts', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.drop_column('avito_accounts', 'telegram_bot_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('avito_accounts', sa.Column('telegram_bot_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('avito_accounts', 'created_at')
    op.drop_column('avito_accounts', 'expires_at')
    op.drop_column('avito_accounts', 'refresh_token')
    # ### end Alembic commands ###
