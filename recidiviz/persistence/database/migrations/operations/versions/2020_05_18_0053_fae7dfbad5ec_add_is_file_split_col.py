# pylint: skip-file
"""add_is_file_split_col

Revision ID: fae7dfbad5ec
Revises: d2da3c60651c
Create Date: 2020-05-18 00:53:59.003664

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fae7dfbad5ec"
down_revision = "d2da3c60651c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "direct_ingest_ingest_file_metadata",
        sa.Column("is_file_split", sa.Boolean(), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("direct_ingest_ingest_file_metadata", "is_file_split")
    # ### end Alembic commands ###
