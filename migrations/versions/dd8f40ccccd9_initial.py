"""Initial

Revision ID: dd8f40ccccd9
Revises: 851b1721f583
Create Date: 2025-07-10 00:32:53.151001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd8f40ccccd9'
down_revision = '851b1721f583'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roadmap_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('roadmap_key', sa.String(length=64), nullable=False),
    sa.Column('goal_posts', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roadmap_items')
    # ### end Alembic commands ###
