"""重新生成迁移

Revision ID: ffa9c991fc5e
Revises: c8b057f983c2
Create Date: 2025-05-15 21:29:56.738899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffa9c991fc5e'
down_revision: Union[str, None] = 'c8b057f983c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admins')
    op.drop_table('patients')
    op.drop_table('doctors')
    op.alter_column('cases', 'id_number',
               existing_type=sa.VARCHAR(length=32),
               comment='患者身份证号',
               existing_nullable=False)
    op.drop_constraint('cases_patient_id_fkey', 'cases', type_='foreignkey')
    op.drop_column('cases', 'patient_id')
    op.add_column('users', sa.Column('department', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('title', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('license_number', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'license_number')
    op.drop_column('users', 'title')
    op.drop_column('users', 'department')
    op.add_column('cases', sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('cases_patient_id_fkey', 'cases', 'users', ['patient_id'], ['id'])
    op.alter_column('cases', 'id_number',
               existing_type=sa.VARCHAR(length=32),
               comment=None,
               existing_comment='患者身份证号',
               existing_nullable=False)
    op.create_table('doctors',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('department', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('license_number', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='doctors_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='doctors_pkey')
    )
    op.create_table('patients',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('gender', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='patients_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='patients_pkey')
    )
    op.create_table('admins',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], name='admins_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='admins_pkey')
    )
    # ### end Alembic commands ###
