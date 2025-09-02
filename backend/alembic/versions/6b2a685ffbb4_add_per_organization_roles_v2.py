"""add_per_organization_roles_v2

Revision ID: 6b2a685ffbb4
Revises: 933103c015c6
Create Date: 2025-09-02 02:28:56.758225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '6b2a685ffbb4'
down_revision: Union[str, None] = '933103c015c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type for user organization roles
    userorg_role_enum = postgresql.ENUM('ADMIN', 'MEMBER', name='userorganizationrole', create_type=False)
    userorg_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Add role column to user_organizations table (nullable first)
    op.add_column('user_organizations', 
                  sa.Column('role', userorg_role_enum, nullable=True))
    
    # Migrate existing data: Set user_organizations.role based on users.role
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE user_organizations 
        SET role = users.role::text::userorganizationrole
        FROM users 
        WHERE user_organizations.user_id = users.id
    """))
    
    # Make the role column NOT NULL
    op.alter_column('user_organizations', 'role', nullable=False)
    
    # Remove the global role column from users table
    op.drop_column('users', 'role')


def downgrade() -> None:
    # Add back the global role column to users (nullable first)
    op.add_column('users', 
                  sa.Column('role', postgresql.ENUM('ADMIN', 'MEMBER', name='role'), nullable=True))
    
    # Migrate data back: Set users.role based on their role in any organization
    # (prioritize ADMIN role if user is admin in any org, otherwise MEMBER)
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users 
        SET role = CASE 
            WHEN EXISTS (
                SELECT 1 FROM user_organizations 
                WHERE user_organizations.user_id = users.id 
                AND user_organizations.role = 'ADMIN'
            ) THEN 'ADMIN'::role
            ELSE 'MEMBER'::role
        END
    """))
    
    # Make the users.role column NOT NULL
    op.alter_column('users', 'role', nullable=False)
    
    # Drop the per-organization role column
    op.drop_column('user_organizations', 'role')
    
    # Drop the enum type
    userorg_role_enum = postgresql.ENUM(name='userorganizationrole')
    userorg_role_enum.drop(op.get_bind(), checkfirst=True)
