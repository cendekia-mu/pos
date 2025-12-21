"""merge fix

Revision ID: bcd50919e629
Revises: 52d4437df6be
Create Date: 2025-12-18 10:08:01.011966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcd50919e629'
down_revision: Union[str, Sequence[str], None] = '52d4437df6be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
