"""merge heads

Revision ID: 1b4c39dc1171
Revises: f9c6bbd9db18, fdda119ef9f1
Create Date: 2026-10-09 21:18:05.770348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b4c39dc1171'
down_revision: Union[str, Sequence[str], None] = ('f9c6bbd9db18', 'fdda119ef9f1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
