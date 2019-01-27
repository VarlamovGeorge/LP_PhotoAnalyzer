"""change first cnn version

Revision ID: 7b89eb809900
Revises: bc19b85ea9a5
Create Date: 2019-01-27 18:08:36.171189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b89eb809900'
down_revision = 'bc19b85ea9a5'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("update algorithms set name='ResNet50, 9 classes, 0.89 accuracy', create_date='2019-01-12 01:01:01' where id=0")


def downgrade():
    pass
