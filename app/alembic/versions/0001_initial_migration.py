"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('last_updated_date', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('handle', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('handle')
    )
    
    # Create chatrooms table
    op.create_table('chatrooms',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('last_updated_date', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('last_updated_date', sa.DateTime(), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('chatroom_id', sa.String(length=36), nullable=False),
        sa.Column('is_reply', sa.Boolean(), nullable=False),
        sa.Column('parent_message_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['chatroom_id'], ['chatrooms.id'], ),
        sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create chatroom_participants table
    op.create_table('chatroom_participants',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('last_updated_date', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('chatroom_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['chatroom_id'], ['chatrooms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('chatroom_participants')
    op.drop_table('messages')
    op.drop_table('chatrooms')
    op.drop_table('users')
