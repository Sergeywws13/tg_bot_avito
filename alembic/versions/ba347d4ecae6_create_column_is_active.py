"""Create column is_active

Revision ID: ba347d4ecae6
Revises: bbb50f96732e
Create Date: 2025-03-18 19:40:36.380947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba347d4ecae6'
down_revision: Union[str, None] = 'bbb50f96732e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
