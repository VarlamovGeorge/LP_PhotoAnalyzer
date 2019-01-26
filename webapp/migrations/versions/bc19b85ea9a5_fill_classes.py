"""Fill classes

Revision ID: bc19b85ea9a5
Revises: 0c6810b8e12a
Create Date: 2019-01-25 22:07:01.412504

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc19b85ea9a5'
down_revision = '0c6810b8e12a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('algorithms', sa.Column('create_date', sa.DateTime(), nullable=False))
    op.drop_column('algorithms', 'ver')
    op.alter_column('photos', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###

    op.execute("insert into classes (id, name) values (1, 'cats')")
    op.execute("insert into classes (id, name) values (2, 'dogs')")
    op.execute("insert into classes (id, name) values (3, 'cars')")
    op.execute("insert into classes (id, name) values (4, 'humans')")
    op.execute("insert into classes (id, name) values (5, 'landscapes')")
    op.execute("insert into classes (id, name) values (6, 'food')")
    op.execute("insert into classes (id, name) values (7, 'cities')")
    op.execute("insert into classes (id, name) values (8, 'documents')")
    op.execute("insert into classes (id, name) values (9, 'other')")
    
    op.execute("insert into algorithms (id, name, create_date) values(0, 'default', '2019-01-01 00:00:00')")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('photos', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.add_column('algorithms', sa.Column('ver', sa.VARCHAR(), nullable=False))
    op.drop_column('algorithms', 'create_date')
    # ### end Alembic commands ###

    op.execute('delete from classes where id in [1,2,3,4,5,6,7,8,9]')
    op.execute('delete from algorithms where id=0')
