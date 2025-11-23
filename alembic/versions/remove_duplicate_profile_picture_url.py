"""Remove duplicate profile_picture_url from customers and trainers

Revision ID: remove_duplicate_pic_url
Revises: add_password_reset_tokens
Create Date: 2025-10-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_duplicate_pic_url'
down_revision = 'add_password_reset_tokens'
branch_labels = None
depends_on = None


def upgrade():
    # Remove profile_picture_url from customers table
    op.drop_column('customers', 'profile_picture_url')

    # Remove profile_picture_url from trainers table
    op.drop_column('trainers', 'profile_picture_url')


def downgrade():
    # Add back profile_picture_url to trainers table
    op.add_column('trainers', sa.Column('profile_picture_url', sa.Text(), nullable=True))

    # Add back profile_picture_url to customers table
    op.add_column('customers', sa.Column('profile_picture_url', sa.Text(), nullable=True))
