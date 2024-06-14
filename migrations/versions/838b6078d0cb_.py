"""empty message

Revision ID: 838b6078d0cb
Revises: 973e1e71c1c2
Create Date: 2024-05-20 14:59:56.618032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '838b6078d0cb'
down_revision = '973e1e71c1c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_expenses')
    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payment_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_expenses_payment_id'), ['payment_id'], unique=False)
        batch_op.create_foreign_key('fk_expense_payment', 'payment', ['payment_id'], ['id'])

    with op.batch_alter_table('income', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.Date(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('income', schema=None) as batch_op:
        batch_op.drop_column('date')

    with op.batch_alter_table('expenses', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_expenses_payment_id'))
        batch_op.drop_column('payment_id')

    op.create_table('_alembic_tmp_expenses',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=140), nullable=False),
    sa.Column('amount', sa.NUMERIC(precision=10, scale=2), nullable=False),
    sa.Column('category_id', sa.INTEGER(), nullable=False),
    sa.Column('date', sa.DATE(), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('payment_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['payment_id'], ['payment.id'], name='fk_expense_payment'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
