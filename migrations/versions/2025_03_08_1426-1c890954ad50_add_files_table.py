"""add files table

Revision ID: 1c890954ad50
Revises:
Create Date: 2025-03-08 14:26:21.740643

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1c890954ad50"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "files",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("object_id", sa.String(length=36), nullable=False),
        sa.Column("object_name", sa.String(length=40), nullable=False),
        sa.Column("backet_name", sa.String(length=40), nullable=False),
        sa.Column(
            "upload_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("object_name"),
    )
    op.create_index(
        op.f("ix_files_object_id"), "files", ["object_id"], unique=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_files_object_id"), table_name="files")
    op.drop_table("files")
    # ### end Alembic commands ###
