"""added_multicolumn_unique_constraint_to

Revision ID: 5110495eb85a
Revises: 897b12b21fbe
Create Date: 2019-02-06 17:51:04.776676

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5110495eb85a'
down_revision = '897b12b21fbe'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("folders_local_path_key", "folders")
    op.create_unique_constraint("uix_1", "folders", ["local_path", "storage_user_id"])


def downgrade():
    op.create_unique_constraint("folders_local_path_key", "folders", ["local_path"])
    op.drop_constraint("uix_1", "folders")
