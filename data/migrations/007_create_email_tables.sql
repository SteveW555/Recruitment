-- Email Classification Tables Migration
-- ProActive People - Recruitment Automation System
-- Date: 2025-01-21

-- =====================================================
-- 1. Email Messages Table
-- =====================================================

CREATE TABLE IF NOT EXISTS email_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    thread_id VARCHAR(255),

    -- Sender/Recipients
    from_email VARCHAR(255) NOT NULL,
    from_name VARCHAR(255),
    to_emails JSONB NOT NULL DEFAULT '[]',
    cc_emails JSONB DEFAULT '[]',
    bcc_emails JSONB DEFAULT '[]',
    reply_to_email VARCHAR(255),
    reply_to_name VARCHAR(255),

    -- Content
    subject TEXT NOT NULL,
    body_text TEXT,
    body_html TEXT,
    attachments JSONB DEFAULT '[]',

    -- Metadata
    received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    source VARCHAR(50) NOT NULL CHECK (source IN ('sendgrid', 'ses', 'smtp', 'manual')),

    -- Processing Status
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    routed BOOLEAN NOT NULL DEFAULT FALSE,
    routed_to JSONB DEFAULT '[]',
    archived BOOLEAN NOT NULL DEFAULT FALSE,
    archived_at TIMESTAMP WITH TIME ZONE,

    -- Relationships
    candidate_id UUID REFERENCES candidates(id) ON DELETE SET NULL,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    placement_id UUID REFERENCES placements(id) ON DELETE SET NULL,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Indexes
    CONSTRAINT valid_direction CHECK (direction IN ('inbound', 'outbound')),
    CONSTRAINT valid_source CHECK (source IN ('sendgrid', 'ses', 'smtp', 'manual'))
);

-- Indexes for email_messages
CREATE INDEX idx_email_messages_message_id ON email_messages(message_id);
CREATE INDEX idx_email_messages_thread_id ON email_messages(thread_id);
CREATE INDEX idx_email_messages_from_email ON email_messages(from_email);
CREATE INDEX idx_email_messages_received_at ON email_messages(received_at DESC);
CREATE INDEX idx_email_messages_processed ON email_messages(processed, processed_at);
CREATE INDEX idx_email_messages_candidate_id ON email_messages(candidate_id);
CREATE INDEX idx_email_messages_client_id ON email_messages(client_id);
CREATE INDEX idx_email_messages_job_id ON email_messages(job_id);
CREATE INDEX idx_email_messages_direction ON email_messages(direction);
CREATE INDEX idx_email_messages_source ON email_messages(source);

-- Full-text search on subject and body
CREATE INDEX idx_email_messages_subject_fts ON email_messages USING gin(to_tsvector('english', subject));
CREATE INDEX idx_email_messages_body_text_fts ON email_messages USING gin(to_tsvector('english', body_text));

COMMENT ON TABLE email_messages IS 'Stores all inbound and outbound emails with full content';
COMMENT ON COLUMN email_messages.message_id IS 'Unique message ID from email provider';
COMMENT ON COLUMN email_messages.thread_id IS 'Conversation thread identifier';
COMMENT ON COLUMN email_messages.to_emails IS 'Array of recipient objects [{email, name}]';
COMMENT ON COLUMN email_messages.attachments IS 'Array of attachment objects [{filename, contentType, size, storageUrl, isCV}]';
COMMENT ON COLUMN email_messages.routed_to IS 'Array of service/user IDs that processed this email';

-- =====================================================
-- 2. Email Classifications Table
-- =====================================================

CREATE TABLE IF NOT EXISTS email_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL REFERENCES email_messages(id) ON DELETE CASCADE,

    -- Classification Results
    category VARCHAR(50) NOT NULL CHECK (category IN ('candidate', 'client', 'supplier', 'staff', 'other')),
    sub_category VARCHAR(100),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    -- Priority & Sentiment
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('urgent', 'high', 'normal', 'low')),
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('positive', 'neutral', 'negative', 'mixed')),

    -- Extracted Information
    keywords JSONB DEFAULT '[]',
    entities JSONB DEFAULT '{}', -- {candidates: [], clients: [], jobs: []}

    -- Action Requirements
    requires_action BOOLEAN NOT NULL DEFAULT FALSE,
    suggested_actions JSONB DEFAULT '[]',

    -- Classification Metadata
    classified_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    classified_by VARCHAR(20) NOT NULL CHECK (classified_by IN ('ai', 'manual', 'rule-based')),
    model_version VARCHAR(50),

    -- Manual Review
    needs_review BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    review_notes TEXT,

    -- Audit
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_category CHECK (category IN ('candidate', 'client', 'supplier', 'staff', 'other')),
    CONSTRAINT valid_priority CHECK (priority IN ('urgent', 'high', 'normal', 'low')),
    CONSTRAINT valid_sentiment CHECK (sentiment IN ('positive', 'neutral', 'negative', 'mixed')),
    CONSTRAINT valid_classified_by CHECK (classified_by IN ('ai', 'manual', 'rule-based'))
);

-- Indexes for email_classifications
CREATE UNIQUE INDEX idx_email_classifications_email_id ON email_classifications(email_id);
CREATE INDEX idx_email_classifications_category ON email_classifications(category);
CREATE INDEX idx_email_classifications_priority ON email_classifications(priority);
CREATE INDEX idx_email_classifications_confidence ON email_classifications(confidence);
CREATE INDEX idx_email_classifications_needs_review ON email_classifications(needs_review);
CREATE INDEX idx_email_classifications_classified_at ON email_classifications(classified_at DESC);
CREATE INDEX idx_email_classifications_requires_action ON email_classifications(requires_action);

COMMENT ON TABLE email_classifications IS 'AI-powered email classification results';
COMMENT ON COLUMN email_classifications.confidence IS 'Classification confidence score (0.0-1.0)';
COMMENT ON COLUMN email_classifications.keywords IS 'Array of extracted keywords';
COMMENT ON COLUMN email_classifications.entities IS 'Extracted entity IDs {candidates: [], clients: [], jobs: []}';
COMMENT ON COLUMN email_classifications.suggested_actions IS 'AI-suggested actions for this email';

-- =====================================================
-- 3. Email Templates Table
-- =====================================================

CREATE TABLE IF NOT EXISTS email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,

    -- Template Content
    subject VARCHAR(500) NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT NOT NULL,

    -- Template Metadata
    category VARCHAR(50) CHECK (category IN ('candidate', 'client', 'supplier', 'staff', 'other')),
    sub_category VARCHAR(100),
    variables JSONB NOT NULL DEFAULT '[]', -- Array of variable names

    -- Status
    active BOOLEAN NOT NULL DEFAULT TRUE,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_template_category CHECK (category IN ('candidate', 'client', 'supplier', 'staff', 'other', NULL))
);

-- Indexes for email_templates
CREATE INDEX idx_email_templates_name ON email_templates(name);
CREATE INDEX idx_email_templates_category ON email_templates(category);
CREATE INDEX idx_email_templates_active ON email_templates(active);

COMMENT ON TABLE email_templates IS 'Reusable email templates for automated and manual communication';
COMMENT ON COLUMN email_templates.variables IS 'Array of variable placeholders used in template (e.g., ["candidateName", "jobTitle"])';

-- =====================================================
-- 4. Email Classification Rules Table
-- =====================================================

CREATE TABLE IF NOT EXISTS email_classification_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    priority INTEGER NOT NULL DEFAULT 100, -- Lower = higher priority
    active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Conditions (JSONB for flexibility)
    conditions JSONB NOT NULL DEFAULT '{}',
    -- {
    --   fromDomain: ["example.com"],
    --   fromEmail: ["sender@example.com"],
    --   toDomain: ["proactivepeople.com"],
    --   subjectContains: ["urgent", "cv"],
    --   bodyContains: ["application"],
    --   hasAttachment: true,
    --   attachmentType: [".pdf", ".docx"]
    -- }

    -- Actions
    actions JSONB NOT NULL DEFAULT '{}',
    -- {
    --   setCategory: "candidate",
    --   setSubCategory: "application",
    --   setPriority: "high",
    --   routeTo: ["recruitment-team"],
    --   autoRespond: true,
    --   responseTemplateId: "uuid",
    --   flag: true
    -- }

    -- Statistics
    match_count INTEGER NOT NULL DEFAULT 0,
    last_matched_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for email_classification_rules
CREATE INDEX idx_email_rules_priority ON email_classification_rules(priority, active);
CREATE INDEX idx_email_rules_active ON email_classification_rules(active);

COMMENT ON TABLE email_classification_rules IS 'Rule-based email classification and routing rules';
COMMENT ON COLUMN email_classification_rules.priority IS 'Rule execution priority (lower number = higher priority)';
COMMENT ON COLUMN email_classification_rules.conditions IS 'JSON object defining matching conditions';
COMMENT ON COLUMN email_classification_rules.actions IS 'JSON object defining actions to take when rule matches';

-- =====================================================
-- 5. Email Statistics View
-- =====================================================

CREATE OR REPLACE VIEW email_classification_stats AS
SELECT
    ec.category,
    COUNT(*) as total_count,
    AVG(ec.confidence) as avg_confidence,
    COUNT(CASE WHEN ec.needs_review THEN 1 END) as needs_review_count,
    COUNT(CASE WHEN ec.requires_action THEN 1 END) as requires_action_count,
    COUNT(CASE WHEN ec.priority = 'urgent' THEN 1 END) as urgent_count,
    COUNT(CASE WHEN ec.priority = 'high' THEN 1 END) as high_priority_count,
    DATE_TRUNC('day', em.received_at) as date
FROM email_classifications ec
JOIN email_messages em ON ec.email_id = em.id
WHERE em.received_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ec.category, DATE_TRUNC('day', em.received_at)
ORDER BY date DESC, ec.category;

COMMENT ON VIEW email_classification_stats IS 'Daily email classification statistics for the last 30 days';

-- =====================================================
-- 6. Trigger: Update email_messages.updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_email_messages_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_email_messages_updated_at
    BEFORE UPDATE ON email_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_email_messages_updated_at();

-- =====================================================
-- 7. Trigger: Update email_classifications.updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_email_classifications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_email_classifications_updated_at
    BEFORE UPDATE ON email_classifications
    FOR EACH ROW
    EXECUTE FUNCTION update_email_classifications_updated_at();

-- =====================================================
-- 8. Trigger: Auto-link email to entities after classification
-- =====================================================

CREATE OR REPLACE FUNCTION auto_link_email_entities()
RETURNS TRIGGER AS $$
BEGIN
    -- Link to candidates if entity IDs are present
    IF NEW.entities ? 'candidates' AND jsonb_array_length(NEW.entities->'candidates') > 0 THEN
        UPDATE email_messages
        SET candidate_id = (NEW.entities->'candidates'->>0)::UUID
        WHERE id = NEW.email_id AND candidate_id IS NULL;
    END IF;

    -- Link to clients
    IF NEW.entities ? 'clients' AND jsonb_array_length(NEW.entities->'clients') > 0 THEN
        UPDATE email_messages
        SET client_id = (NEW.entities->'clients'->>0)::UUID
        WHERE id = NEW.email_id AND client_id IS NULL;
    END IF;

    -- Link to jobs
    IF NEW.entities ? 'jobs' AND jsonb_array_length(NEW.entities->'jobs') > 0 THEN
        UPDATE email_messages
        SET job_id = (NEW.entities->'jobs'->>0)::UUID
        WHERE id = NEW.email_id AND job_id IS NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_link_email_entities
    AFTER INSERT OR UPDATE ON email_classifications
    FOR EACH ROW
    EXECUTE FUNCTION auto_link_email_entities();

-- =====================================================
-- 9. Sample Data: Email Templates
-- =====================================================

INSERT INTO email_templates (name, subject, body_html, body_text, category, sub_category, variables, active)
VALUES
(
    'candidate_application_acknowledgement',
    'Application Received - {{jobTitle}}',
    '<p>Dear {{candidateName}},</p><p>Thank you for your application for the <strong>{{jobTitle}}</strong> position. We have received your CV and will review it shortly.</p><p>If your experience matches our requirements, we will contact you within 3-5 business days.</p><p>Best regards,<br>ProActive People Recruitment Team</p>',
    'Dear {{candidateName}},\n\nThank you for your application for the {{jobTitle}} position. We have received your CV and will review it shortly.\n\nIf your experience matches our requirements, we will contact you within 3-5 business days.\n\nBest regards,\nProActive People Recruitment Team',
    'candidate',
    'application',
    '["candidateName", "jobTitle"]',
    true
),
(
    'client_feedback_request',
    'Interview Feedback Request - {{candidateName}}',
    '<p>Hi {{clientContactName}},</p><p>I hope {{candidateName}}''s interview went well. Could you please provide your feedback on the candidate at your earliest convenience?</p><p>Your input is invaluable in helping us find the perfect match for your team.</p><p>Best regards,<br>{{recruiterName}}<br>ProActive People</p>',
    'Hi {{clientContactName}},\n\nI hope {{candidateName}}''s interview went well. Could you please provide your feedback on the candidate at your earliest convenience?\n\nYour input is invaluable in helping us find the perfect match for your team.\n\nBest regards,\n{{recruiterName}}\nProActive People',
    'client',
    'feedback',
    '["clientContactName", "candidateName", "recruiterName"]',
    true
),
(
    'internal_team_update',
    'Team Update - {{updateType}}',
    '<p>Hi Team,</p><p>{{updateMessage}}</p><p>Please review and let me know if you have any questions.</p><p>Thanks,<br>{{senderName}}</p>',
    'Hi Team,\n\n{{updateMessage}}\n\nPlease review and let me know if you have any questions.\n\nThanks,\n{{senderName}}',
    'staff',
    'team_update',
    '["updateType", "updateMessage", "senderName"]',
    true
);

-- =====================================================
-- 10. Sample Data: Classification Rules
-- =====================================================

INSERT INTO email_classification_rules (name, description, priority, conditions, actions, active)
VALUES
(
    'cv_attachments_are_candidates',
    'Emails with CV/resume attachments should be classified as candidate emails',
    10,
    '{"hasAttachment": true, "attachmentType": [".pdf", ".docx", ".doc"], "bodyContains": ["cv", "resume", "curriculum vitae", "application"]}',
    '{"setCategory": "candidate", "setSubCategory": "cv_submission", "setPriority": "high", "routeTo": ["candidate-service", "cv-parser"]}',
    true
),
(
    'bullhorn_emails_are_supplier',
    'All emails from Bullhorn are supplier emails',
    5,
    '{"fromDomain": ["bullhorn.com"]}',
    '{"setCategory": "supplier", "setSubCategory": "integration_issue", "routeTo": ["integration-hub", "bullhorn-sync"]}',
    true
),
(
    'internal_staff_emails',
    'Emails from @proactivepeople.com are internal staff communications',
    5,
    '{"fromDomain": ["proactivepeople.com", "proactive-people.co.uk"]}',
    '{"setCategory": "staff", "setPriority": "normal", "routeTo": ["internal-inbox"]}',
    true
),
(
    'urgent_keyword_flagging',
    'Flag emails with urgent keywords as high priority',
    20,
    '{"subjectContains": ["urgent", "asap", "emergency", "critical"]}',
    '{"setPriority": "urgent", "flag": true}',
    true
),
(
    'job_brief_from_clients',
    'Job briefs and vacancy emails from clients',
    15,
    '{"bodyContains": ["job brief", "vacancy", "looking to hire", "recruitment need"], "fromDomain": ["!proactivepeople.com", "!bullhorn.com", "!broadbean.com"]}',
    '{"setCategory": "client", "setSubCategory": "job_brief", "setPriority": "high", "routeTo": ["client-service", "job-service"]}',
    true
);

-- =====================================================
-- 11. Grant Permissions
-- =====================================================

-- Grant appropriate permissions (adjust role names as needed)
GRANT SELECT, INSERT, UPDATE ON email_messages TO authenticated;
GRANT SELECT, INSERT, UPDATE ON email_classifications TO authenticated;
GRANT SELECT ON email_templates TO authenticated;
GRANT SELECT ON email_classification_rules TO authenticated;
GRANT SELECT ON email_classification_stats TO authenticated;

-- Admin full access
GRANT ALL ON email_messages TO admin;
GRANT ALL ON email_classifications TO admin;
GRANT ALL ON email_templates TO admin;
GRANT ALL ON email_classification_rules TO admin;

COMMENT ON SCHEMA public IS 'Email classification system for ProActive People recruitment platform';
