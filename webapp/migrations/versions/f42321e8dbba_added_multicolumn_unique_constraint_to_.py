"""Added multicolumn unique constraint to FOLDERS

Revision ID: f42321e8dbba
Revises: 7b89eb809900
Create Date: 2019-02-05 20:25:52.485121

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f42321e8dbba'
down_revision = '7b89eb809900'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("local_path", "folders")
    op.create_unique_constraint("uix_1", "folders", "local_path", "storage_user_id")


def downgrade():
    op.create_unique_constraint("local_path", "folders")
    op.drop_constraint("uix_1", "folders", "local_path", "storage_user_id")

