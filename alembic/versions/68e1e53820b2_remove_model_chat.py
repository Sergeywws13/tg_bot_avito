"""Remove model chat

Revision ID: 68e1e53820b2
Revises: ba347d4ecae6
Create Date: 2025-03-20 17:32:47.028303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68e1e53820b2'
down_revision: Union[str, None] = 'ba347d4ecae6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
