"""Add missing tables: rules, script_templates, compliance_violations, ab_testing, review_queue, contact_history

Revision ID: add_missing_tables
Revises: previous_revision
Create Date: 2026-09-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_missing_tables'
down_revision = None  # Update with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Rules table
    op.create_table(
        'rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('rule_type', sa.String(30), nullable=False, index=True),
        sa.Column('drl_content', sa.Text()),
        sa.Column('decision_table_path', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50)),
        sa.Column('updated_by', sa.String(50)),
        sa.Column('execution_count', sa.Integer(), default=0),
        sa.Column('last_executed_at', sa.DateTime())
    )

    # Script templates table
    op.create_table(
        'script_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('scenario', sa.String(50), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('compliance_validated', sa.Boolean(), default=False),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('effectiveness_score', sa.Float()),
        sa.Column('success_rate', sa.Float()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50)),
        sa.Column('tags', postgresql.JSON())
    )

    # Compliance violations table
    op.create_table(
        'compliance_violations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), index=True),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), index=True),
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), index=True),
        sa.Column('violation_type', sa.String(50), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('detected_by', sa.String(20), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('evidence', postgresql.JSON()),
        sa.Column('resolved', sa.Boolean(), default=False, index=True),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('resolved_by', sa.String(50)),
        sa.Column('resolution_notes', sa.Text()),
        sa.Column('action_taken', sa.String(100))
    )

    # A/B test experiments table
    op.create_table(
        'ab_test_experiments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text()),
        sa.Column('control_description', sa.Text()),
        sa.Column('treatment_description', sa.Text()),
        sa.Column('hypothesis', sa.Text()),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime()),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('target_metric', sa.String(50)),
        sa.Column('target_sample_size', sa.Integer()),
        sa.Column('control_success_count', sa.Integer(), default=0),
        sa.Column('control_total_count', sa.Integer(), default=0),
        sa.Column('treatment_success_count', sa.Integer(), default=0),
        sa.Column('treatment_total_count', sa.Integer(), default=0),
        sa.Column('statistical_significance', sa.Float()),
        sa.Column('winner', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(50))
    )

    # A/B test assignments table
    op.create_table(
        'ab_test_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('experiment_name', sa.String(100), nullable=False, index=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('variant', sa.String(20), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('outcome_data', postgresql.JSON()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('success', sa.Boolean())
    )

    # GenAI review queue table
    op.create_table(
        'genai_review_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), index=True),
        sa.Column('service_type', sa.String(50), nullable=False),
        sa.Column('genai_output', postgresql.JSON(), nullable=False),
        sa.Column('trust_gate_evaluation', postgresql.JSON(), nullable=False),
        sa.Column('status', sa.String(20), default='pending', index=True),
        sa.Column('priority', sa.Integer(), default=5),
        sa.Column('assigned_reviewer', postgresql.UUID(as_uuid=True), index=True),
        sa.Column('assigned_at', sa.DateTime()),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.Column('reviewer_decision', postgresql.JSON()),
        sa.Column('reviewer_comments', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # Contact history table
    op.create_table(
        'contact_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('contact_type', sa.String(20), nullable=False),
        sa.Column('contact_time', sa.DateTime(), nullable=False),
        sa.Column('duration_seconds', sa.Integer()),
        sa.Column('transcript', sa.Text()),
        sa.Column('recording_url', sa.String(500)),
        sa.Column('sentiment', sa.String(20)),
        sa.Column('intent', sa.String(50)),
        sa.Column('key_phrases', postgresql.JSON()),
        sa.Column('outcome', sa.String(50)),
        sa.Column('compliance_checked', sa.Boolean(), default=False),
        sa.Column('compliance_violations', postgresql.JSON()),
        sa.Column('created_by', sa.String(50)),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )


def downgrade():
    op.drop_table('contact_history')
    op.drop_table('genai_review_queue')
    op.drop_table('ab_test_assignments')
    op.drop_table('ab_test_experiments')
    op.drop_table('compliance_violations')
    op.drop_table('script_templates')
    op.drop_table('rules')
