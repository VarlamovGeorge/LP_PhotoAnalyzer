"""add to some fileds dropb prefix

Revision ID: 2b60e333111d
Revises: 7b89eb809900
Create Date: 2019-02-03 00:16:05.224553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b60e333111d'
down_revision = '7b89eb809900'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('photos', 'revision', new_column_name='dropb_file_rev')
    op.alter_column('photos', 'content_hash', new_column_name='dropb_hash')

def downgrade():
    op.alter_column('photos', 'dropb_file_rev', new_column_name='revision') 
    op.alter_column('photos', 'dropb_hash', new_column_name='content_hash') 
