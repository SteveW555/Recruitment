-- Migration: 001_create_routing_logs
-- Purpose: Create tables for AI Router logging with 90-day retention and 30-day anonymization
-- Created: 2025-10-22
-- Feature: Chat Routing AI (002-chat-routing-ai)

-- ====================================================================
-- Table 1: routing_logs (Full logs, 0-30 days)
-- ====================================================================
CREATE TABLE IF NOT EXISTS routing_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- User & Session (anonymized after 30 days)
    user_id VARCHAR(255) NOT NULL,
    session_id UUID NOT NULL,

    -- Query Details
    query_text TEXT NOT NULL,
    query_length_words INT NOT NULL,
    query_truncated BOOLEAN NOT NULL DEFAULT FALSE,

    -- Classification Results
    primary_category VARCHAR(50) NOT NULL CHECK (primary_category IN (
        'INFORMATION_RETRIEVAL',
        'PROBLEM_SOLVING',
        'REPORT_GENERATION',
        'AUTOMATION',
        'INDUSTRY_KNOWLEDGE',
        'GENERAL_CHAT'
    )),
    primary_confidence DECIMAL(5,4) NOT NULL CHECK (primary_confidence >= 0 AND primary_confidence <= 1),
    secondary_category VARCHAR(50) CHECK (secondary_category IN (
        'INFORMATION_RETRIEVAL',
        'PROBLEM_SOLVING',
        'REPORT_GENERATION',
        'AUTOMATION',
        'INDUSTRY_KNOWLEDGE',
        'GENERAL_CHAT'
    )),
    secondary_confidence DECIMAL(5,4) CHECK (secondary_confidence >= 0 AND secondary_confidence <= 1),

    -- Performance Metrics
    classification_latency_ms INT NOT NULL,
    agent_execution_latency_ms INT,

    -- Outcome
    agent_success BOOLEAN NOT NULL,
    fallback_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    user_override BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_routing_logs_timestamp ON routing_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_routing_logs_user_id ON routing_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_routing_logs_category ON routing_logs(primary_category);
CREATE INDEX IF NOT EXISTS idx_routing_logs_session ON routing_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_routing_logs_created_at ON routing_logs(created_at);

-- ====================================================================
-- Table 2: routing_logs_anonymized (Anonymized logs, 30-90 days)
-- ====================================================================
CREATE TABLE IF NOT EXISTS routing_logs_anonymized (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,

    -- Hashed Identifiers
    session_hash VARCHAR(64) NOT NULL,  -- SHA-256(session_id + salt)
    query_hash VARCHAR(64) NOT NULL,    -- SHA-256(query_text + salt)

    -- Preserved Analytics Data
    query_length_words INT NOT NULL,
    query_truncated BOOLEAN NOT NULL,
    primary_category VARCHAR(50) NOT NULL CHECK (primary_category IN (
        'INFORMATION_RETRIEVAL',
        'PROBLEM_SOLVING',
        'REPORT_GENERATION',
        'AUTOMATION',
        'INDUSTRY_KNOWLEDGE',
        'GENERAL_CHAT'
    )),
    primary_confidence DECIMAL(5,4) NOT NULL CHECK (primary_confidence >= 0 AND primary_confidence <= 1),
    secondary_category VARCHAR(50) CHECK (secondary_category IN (
        'INFORMATION_RETRIEVAL',
        'PROBLEM_SOLVING',
        'REPORT_GENERATION',
        'AUTOMATION',
        'INDUSTRY_KNOWLEDGE',
        'GENERAL_CHAT'
    )),
    secondary_confidence DECIMAL(5,4) CHECK (secondary_confidence >= 0 AND secondary_confidence <= 1),
    classification_latency_ms INT NOT NULL,
    agent_execution_latency_ms INT,
    agent_success BOOLEAN NOT NULL,
    fallback_triggered BOOLEAN NOT NULL,
    user_override BOOLEAN NOT NULL,

    -- Audit
    anonymized_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for anonymized table
CREATE INDEX IF NOT EXISTS idx_routing_logs_anonymized_timestamp ON routing_logs_anonymized(timestamp);
CREATE INDEX IF NOT EXISTS idx_routing_logs_anonymized_category ON routing_logs_anonymized(primary_category);
CREATE INDEX IF NOT EXISTS idx_routing_logs_anonymized_session_hash ON routing_logs_anonymized(session_hash);

-- ====================================================================
-- Comments for documentation
-- ====================================================================
COMMENT ON TABLE routing_logs IS 'Full routing decision logs with user data (0-30 days). Moved to routing_logs_anonymized after 30 days via cron job.';
COMMENT ON TABLE routing_logs_anonymized IS 'Anonymized routing logs (30-90 days). Deleted after 90 days via cron job.';

COMMENT ON COLUMN routing_logs.user_id IS 'User identifier - removed after 30 days during anonymization';
COMMENT ON COLUMN routing_logs.query_text IS 'Full query text - hashed after 30 days during anonymization';
COMMENT ON COLUMN routing_logs_anonymized.session_hash IS 'SHA-256 hash of session_id with salt';
COMMENT ON COLUMN routing_logs_anonymized.query_hash IS 'SHA-256 hash of query_text with salt';
