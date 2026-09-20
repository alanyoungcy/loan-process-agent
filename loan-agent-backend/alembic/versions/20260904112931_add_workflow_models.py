"""add workflow models

Revision ID: add_workflow_models
Revises: ba5c2b63e16d
Create Date: 2026-09-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_workflow_models'
down_revision = 'ba5c2b63e16d'
branch_labels = None
depends_on = None


def upgrade():
    # Create workflow_instances table
    op.create_table(
        'workflow_instances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_key', sa.String(length=100), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_key', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_task_id', sa.String(length=100), nullable=True),
        sa.Column('current_task_name', sa.String(length=200), nullable=True),
        sa.Column('variables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('external_process_instance_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_instances_case_id', 'workflow_instances', ['case_id'])
    op.create_index('ix_workflow_instances_status', 'workflow_instances', ['status'])
    op.create_index('ix_workflow_instances_workflow_key', 'workflow_instances', ['workflow_key'])
    op.create_index('ix_workflow_instances_external_process_instance_id', 'workflow_instances', ['external_process_instance_id'])

    # Create workflow_tasks table
    op.create_table(
        'workflow_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_key', sa.String(length=100), nullable=False),
        sa.Column('task_name', sa.String(length=200), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=True),
        sa.Column('assignee', sa.String(length=50), nullable=True),
        sa.Column('candidate_group', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('variables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('outcome', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('external_task_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['workflow_instance_id'], ['workflow_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_tasks_workflow_instance_id', 'workflow_tasks', ['workflow_instance_id'])
    op.create_index('ix_workflow_tasks_status', 'workflow_tasks', ['status'])
    op.create_index('ix_workflow_tasks_assignee', 'workflow_tasks', ['assignee'])
    op.create_index('ix_workflow_tasks_external_task_id', 'workflow_tasks', ['external_task_id'])


def downgrade():
    op.drop_table('workflow_tasks')
    op.drop_table('workflow_instances')
