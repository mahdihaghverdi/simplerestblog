"""add totp_hash to UserModel

Revision ID: 6fec2f86d644
Revises: 8cd7bf6413dc
Create Date: 2024-03-25 21:54:56.310595

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6fec2f86d644"
down_revision: str | None = "8cd7bf6413dc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("totp_hash", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "totp_hash")
    # ### end Alembic commands ###