"""create case table

Revision ID: c8b057f983c2
Revises: 
Create Date: 2025-04-24 16:50:52.979638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8b057f983c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_number', sa.String(length=32), nullable=False, comment='患者身份证号'),
    sa.Column('patient_name', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cases_id'), 'cases', ['id'], unique=False)
    op.create_index(op.f('ix_cases_id_number'), 'cases', ['id_number'], unique=True)
    op.create_table('diagnoses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('case_id', sa.Integer(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnoses_id'), 'diagnoses', ['id'], unique=False)
    op.create_table('images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('case_id', sa.Integer(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_images_id'), 'images', ['id'], unique=False)
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.drop_constraint('users_username_key', 'users', type_='unique')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    op.create_unique_constraint('users_email_key', 'users', ['email'])
    op.drop_index(op.f('ix_images_id'), table_name='images')
    op.drop_table('images')
    op.drop_index(op.f('ix_diagnoses_id'), table_name='diagnoses')
    op.drop_table('diagnoses')
    op.drop_index(op.f('ix_cases_id_number'), table_name='cases')
    op.drop_index(op.f('ix_cases_id'), table_name='cases')
    op.drop_table('cases')
    # ### end Alembic commands ###
