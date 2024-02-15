"""add tmplink to DraftModel

Revision ID: c4098caf6fbd
Revises: 913b1d483431
Create Date: 2024-02-15 15:31:37.313131

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4098caf6fbd"
down_revision: str | None = "913b1d483431"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("drafts", sa.Column("tmplink", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("drafts", "tmplink")
    # ### end Alembic commands ###
