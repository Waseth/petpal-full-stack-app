"""Add adopter_id to pet

Revision ID: 7618e2a2122a
Revises: c9b3672c56bc
Create Date: 2025-04-11 14:38:19.181004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7618e2a2122a'
down_revision = 'c9b3672c56bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pet', schema=None) as batch_op:
        batch_op.add_column(sa.Column('adopter_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_pet_adopter_id', 'adopter', ['adopter_id'], ['id'])


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pet', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('adopter_id')

    # ### end Alembic commands ###
