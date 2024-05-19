"""Changes in the models

Revision ID: 157f19eff8ab
Revises: 
Create Date: 2024-05-19 21:44:39.606012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '157f19eff8ab'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('appointments', 'appointment_date',
               existing_type=mysql.DATETIME(),
               type_=sa.String(length=256),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('appointments', 'appointment_date',
               existing_type=sa.String(length=256),
               type_=mysql.DATETIME(),
               existing_nullable=False)
    # ### end Alembic commands ###