"""empty message

Revision ID: cdea62dd9fec
Revises: 
Create Date: 2024-11-08 11:08:33.767335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdea62dd9fec'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('real_estate',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('area_type', sa.String(length=100), nullable=False),
    sa.Column('availability', sa.String(length=50), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=False),
    sa.Column('size', sa.String(length=50), nullable=False),
    sa.Column('society', sa.String(length=200), nullable=True),
    sa.Column('total_sqft', sa.Float(), nullable=False),
    sa.Column('bath', sa.Integer(), nullable=False),
    sa.Column('balcony', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=150), nullable=False),
    sa.Column('password', sa.String(length=150), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('real_estate')
    # ### end Alembic commands ###
