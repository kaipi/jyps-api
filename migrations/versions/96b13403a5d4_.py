"""empty message

Revision ID: 96b13403a5d4
Revises: e4fd219f7e9a
Create Date: 2018-03-22 23:28:27.091809

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '96b13403a5d4'
down_revision = 'e4fd219f7e9a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('setting_key', sa.String(length=80), nullable=True))
    op.add_column('settings', sa.Column('setting_value', sa.String(length=80), nullable=True))
    op.drop_column('settings', 'value')
    op.drop_column('settings', 'key')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('key', mysql.VARCHAR(length=80), nullable=True))
    op.add_column('settings', sa.Column('value', mysql.VARCHAR(length=80), nullable=True))
    op.drop_column('settings', 'setting_value')
    op.drop_column('settings', 'setting_key')
    # ### end Alembic commands ###