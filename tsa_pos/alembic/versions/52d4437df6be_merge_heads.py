"""merge heads

Revision ID: 52d4437df6be
Revises: 59ba13abd48d, fbaac20d4155
Create Date: 2025-12-18 10:07:11.922375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52d4437df6be'
down_revision: Union[str, Sequence[str], None] = ('59ba13abd48d', 'fbaac20d4155')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
