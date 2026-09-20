-- Initialize database schema for loan collection system
-- Run on postgres container startup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'collector',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    id_card VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    employment_status VARCHAR(30),
    monthly_income DECIMAL(15,2),
    credit_score INTEGER,
    customer_segment VARCHAR(20),
    registration_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create cases table
CREATE TABLE IF NOT EXISTS cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    loan_id VARCHAR(50) NOT NULL,
    loan_product VARCHAR(50),
    principal_amount DECIMAL(15,2),
    overdue_amount DECIMAL(15,2),
    overdue_days INTEGER,
    overdue_date DATE,
    status VARCHAR(30) DEFAULT 'new',
    priority INTEGER DEFAULT 5,
    assigned_to UUID REFERENCES users(id),
    contact_count INTEGER DEFAULT 0,
    last_contact_date TIMESTAMP,
    payment_promise JSONB,
    dispute_flag BOOLEAN DEFAULT FALSE,
    legal_status VARCHAR(30),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- Create contact_history table
CREATE TABLE IF NOT EXISTS contact_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contact_id VARCHAR(50) UNIQUE NOT NULL,
    case_id UUID NOT NULL,
    contact_type VARCHAR(20) NOT NULL,
    contact_time TIMESTAMP NOT NULL,
    duration_seconds INTEGER,
    transcript TEXT,
    sentiment VARCHAR(20),
    intent VARCHAR(50),
    outcome VARCHAR(50),
    created_by UUID REFERENCES users(id),
    genai_processed BOOLEAN DEFAULT FALSE,
    compliance_checked BOOLEAN DEFAULT FALSE,
    compliance_violations TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_case FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
);

-- Create rules table
CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type VARCHAR(30) NOT NULL,
    drl_content TEXT,
    decision_table_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 5,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create genai_audit table
CREATE TABLE IF NOT EXISTS genai_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID,
    service_type VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    confidence FLOAT,
    trust_gate_decision VARCHAR(20),
    human_review_result VARCHAR(20),
    reviewed_by UUID REFERENCES users(id),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_case_audit FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE SET NULL
);

-- Create script_templates table
CREATE TABLE IF NOT EXISTS script_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    scenario VARCHAR(50),
    content TEXT NOT NULL,
    compliance_validated BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    effectiveness_score FLOAT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create compliance_violations table
CREATE TABLE IF NOT EXISTS compliance_violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID,
    contact_id UUID,
    violation_type VARCHAR(50) NOT NULL,
    description TEXT,
    severity VARCHAR(20),
    detected_by VARCHAR(20),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by UUID REFERENCES users(id),
    CONSTRAINT fk_case_violation FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE SET NULL,
    CONSTRAINT fk_contact_violation FOREIGN KEY (contact_id) REFERENCES contact_history(id) ON DELETE SET NULL
);

-- Create task_queue table (for async jobs)
CREATE TABLE IF NOT EXISTS task_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(50) UNIQUE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    payload JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB,
    error TEXT,
    priority INTEGER DEFAULT 5,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_cases_customer_id ON cases(customer_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_assigned_to ON cases(assigned_to);
CREATE INDEX idx_cases_overdue_days ON cases(overdue_days);
CREATE INDEX idx_cases_created_at ON cases(created_at);

CREATE INDEX idx_contact_history_case_id ON contact_history(case_id);
CREATE INDEX idx_contact_history_contact_time ON contact_history(contact_time);
CREATE INDEX idx_contact_history_created_by ON contact_history(created_by);

CREATE INDEX idx_rules_rule_type ON rules(rule_type);
CREATE INDEX idx_rules_is_active ON rules(is_active);

CREATE INDEX idx_genai_audit_case_id ON genai_audit(case_id);
CREATE INDEX idx_genai_audit_service_type ON genai_audit(service_type);
CREATE INDEX idx_genai_audit_created_at ON genai_audit(created_at);

CREATE INDEX idx_compliance_violations_case_id ON compliance_violations(case_id);
CREATE INDEX idx_compliance_violations_detected_at ON compliance_violations(detected_at);
CREATE INDEX idx_compliance_violations_resolved ON compliance_violations(resolved);

CREATE INDEX idx_task_queue_status ON task_queue(status);
CREATE INDEX idx_task_queue_task_type ON task_queue(task_type);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES (
    'admin',
    'admin@loan-agent.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5RA0Z0lKsGuFS', -- hashed "admin123"
    'System Administrator',
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- Insert demo collector users
INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES
    ('collector1', 'collector1@loan-agent.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5RA0Z0lKsGuFS', '李明', 'collector'),
    ('collector2', 'collector2@loan-agent.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5RA0Z0lKsGuFS', '王娟', 'collector'),
    ('supervisor1', 'supervisor1@loan-agent.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5RA0Z0lKsGuFS', '張偉', 'supervisor')
ON CONFLICT (username) DO NOTHING;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_script_templates_updated_at BEFORE UPDATE ON script_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
