"""Create Lessons table and establish relationship with Courses

Revision ID: 446c3b03d2a2
Revises: 6f888ca06d88
Create Date: 2024-10-13 02:41:22.855506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '446c3b03d2a2'
down_revision = '6f888ca06d88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_filename', sa.String(length=255), nullable=True))
        batch_op.drop_column('image_url')

    with op.batch_alter_table('lesson', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_attachment_filename', sa.String(length=255), nullable=True))
        batch_op.drop_column('image_url')
        batch_op.drop_column('file_attachment_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lesson', schema=None) as batch_op:
        batch_op.add_column(sa.Column('file_attachment_url', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('file_attachment_filename')

    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('image_filename')

    # ### end Alembic commands ###
