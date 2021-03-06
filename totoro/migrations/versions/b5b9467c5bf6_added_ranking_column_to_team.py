"""added ranking column to team

Revision ID: b5b9467c5bf6
Revises: d5e6aacf8012
Create Date: 2016-08-02 16:15:21.184666

"""

# revision identifiers, used by Alembic.
revision = 'b5b9467c5bf6'
down_revision = 'd5e6aacf8012'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team', sa.Column('ranking', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('team', 'ranking')
    ### end Alembic commands ###
