"""empty message

Revision ID: e4fd219f7e9a
Revises: 5d721ede5b2b
Create Date: 2018-03-21 22:49:48.835308

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4fd219f7e9a'
down_revision = '5d721ede5b2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('participant', sa.Column('referencenumber', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('participant', 'referencenumber')
    # ### end Alembic commands ###
