"""empty message

Revision ID: 009a14fb7150
Revises: 21cedca3c6f0
Create Date: 2018-05-17 20:18:55.605636

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '009a14fb7150'
down_revision = '21cedca3c6f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event_group', sa.Column('discount', sa.Numeric(), nullable=True))
    op.add_column('participant', sa.Column('jyps_member', sa.Boolean(), nullable=True))
    op.add_column('participant', sa.Column('team', sa.Text(), nullable=True))
    op.alter_column('participant', 'payment_confirmed',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('participant', 'public',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    op.alter_column('participant', 'sport_voucher',
               existing_type=mysql.TINYINT(display_width=1),
               type_=sa.Boolean(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('participant', 'sport_voucher',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('participant', 'public',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.alter_column('participant', 'payment_confirmed',
               existing_type=sa.Boolean(),
               type_=mysql.TINYINT(display_width=1),
               existing_nullable=True)
    op.drop_column('participant', 'team')
    op.drop_column('participant', 'jyps_member')
    op.drop_column('event_group', 'discount')
    # ### end Alembic commands ###
