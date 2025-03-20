"""fix model avito_account

Revision ID: de60f329ceb6
Revises: 68e1e53820b2
Create Date: 2025-03-20 19:32:51.423634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de60f329ceb6'
down_revision: Union[str, None] = '68e1e53820b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
