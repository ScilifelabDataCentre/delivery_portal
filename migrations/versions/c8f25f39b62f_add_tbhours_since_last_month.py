"""add_tbhours_since_last_month

Revision ID: c8f25f39b62f
Revises: d48ecb4db259
Create Date: 2023-05-31 08:04:09.768951

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "c8f25f39b62f"
down_revision = "d48ecb4db259"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("reporting", sa.Column("tbhours", sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("reporting", "tbhours")
    # ### end Alembic commands ###
