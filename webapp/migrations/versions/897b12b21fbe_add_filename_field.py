"""add filename field

Revision ID: 897b12b21fbe
Revises: 2b60e333111d
Create Date: 2019-02-06 12:53:02.061532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '897b12b21fbe'
down_revision = '2b60e333111d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('photos', sa.Column('filename', sa.String()))
    op.add_column('photos', sa.Column('status_cnn', sa.Integer()))
    op.alter_column('photos', 'status', new_column_name='status_sync')


def downgrade():
    op.drop_column('photos', 'filename')
    op.drop_column('photos', 'status_cnn')
    op.alter_column('photos', 'status_sync', new_column_name='status')
