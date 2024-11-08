"""empty message

Revision ID: 57665a81711d
Revises: ff5d5421ed17
Create Date: 2024-11-08 01:16:04.879623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57665a81711d'
down_revision = 'ff5d5421ed17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.String(length=100), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('study_hours_per_week', sa.Float(), nullable=True),
    sa.Column('attendance_rate', sa.Float(), nullable=True),
    sa.Column('gpa', sa.Float(), nullable=True),
    sa.Column('major', sa.String(length=100), nullable=True),
    sa.Column('part_time_job', sa.String(length=50), nullable=True),
    sa.Column('extra_curricular_activities', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students')
    # ### end Alembic commands ###
