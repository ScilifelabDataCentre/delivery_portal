"""adding_totp

Revision ID: 6f68e3673bd5
Revises: 666003748d14
Create Date: 2022-03-03 08:32:21.500977

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects import mysql
from dds_web.database import models

# revision identifiers, used by Alembic.
revision = "6f68e3673bd5"
down_revision = "666003748d14"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("totp_enabled", sa.Boolean(), nullable=False))
    op.add_column("users", sa.Column("_totp_secret", sa.LargeBinary(length=64), nullable=True))
    op.add_column("users", sa.Column("totp_last_verified", sa.DateTime(), nullable=True))

    session = Session(bind=op.get_bind())
    all_user_rows = session.query(models.User).all()
    for user in all_user_rows:
        user.totp_enabled = False
    session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "totp_last_verified")
    op.drop_column("users", "_totp_secret")
    op.drop_column("users", "totp_enabled")
    # ### end Alembic commands ###
