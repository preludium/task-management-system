"""Create tasks table

Revision ID: 0001
Revises: 
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    task_status_enum = postgresql.ENUM('OPEN', 'IN_PROGRESS', 'DONE', name='TASK_STATUS')
    
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', task_status_enum, nullable=False, server_default='OPEN'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_tasks_id', 'tasks', ['id'])
    
    op.create_check_constraint(
        'tasks_status_check',
        'tasks',
        "status IN ('OPEN', 'IN_PROGRESS', 'DONE')"
    )


def downgrade() -> None:
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_index('idx_tasks_id', table_name='tasks')
    
    op.drop_table('tasks')
    
    task_status_enum = postgresql.ENUM('OPEN', 'IN_PROGRESS', 'DONE', name='TASK_STATUS')
    task_status_enum.drop(op.get_bind())