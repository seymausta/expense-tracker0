"""category table

Revision ID: 12fdf5274f82
Revises: c300855d141f
Create Date: 2024-04-26 12:44:49.513523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12fdf5274f82'
down_revision = 'c300855d141f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(length=64), nullable=False),
    sa.Column('lastname', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_firstname'), ['firstname'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_lastname'), ['lastname'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_email')
        batch_op.drop_index('ix_user_firstname')
        batch_op.drop_index('ix_user_lastname')

    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('firstname', sa.VARCHAR(length=64), nullable=False),
    sa.Column('lastname', sa.VARCHAR(length=64), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('ix_user_lastname', ['lastname'], unique=False)
        batch_op.create_index('ix_user_firstname', ['firstname'], unique=False)
        batch_op.create_index('ix_user_email', ['email'], unique=1)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_lastname'))
        batch_op.drop_index(batch_op.f('ix_users_firstname'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    op.drop_table('category')
    # ### end Alembic commands ###