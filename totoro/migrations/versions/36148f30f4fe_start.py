"""start

Revision ID: 36148f30f4fe
Revises: None
Create Date: 2016-07-21 13:21:43.085378

"""

# revision identifiers, used by Alembic.
revision = '36148f30f4fe'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tournament', 'set_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tournament', 'set_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    ### end Alembic commands ###
