-- Migration 003: Align Database Tables with CSV Structure
-- Created: 2025-10-22
-- Purpose: Drop and recreate tables to match actual CSV column names

-- Drop all existing tables
DROP TABLE IF EXISTS permanent_placement_invoices CASCADE;
DROP TABLE IF EXISTS temporary_worker_invoices CASCADE;
DROP TABLE IF EXISTS training_service_invoices CASCADE;
DROP TABLE IF EXISTS wellbeing_service_invoices CASCADE;
DROP TABLE IF EXISTS assessment_service_invoices CASCADE;
DROP TABLE IF EXISTS contact_centre_consultancy_invoices CASCADE;
DROP TABLE IF EXISTS staff_salaries CASCADE;
DROP TABLE IF EXISTS temp_worker_payroll CASCADE;
DROP TABLE IF EXISTS office_rent_facilities CASCADE;
DROP TABLE IF EXISTS technology_subscriptions CASCADE;
DROP TABLE IF EXISTS job_board_advertising CASCADE;
DROP TABLE IF EXISTS insurance_premiums CASCADE;
DROP TABLE IF EXISTS compliance_costs CASCADE;
DROP TABLE IF EXISTS marketing_costs CASCADE;
DROP TABLE IF EXISTS professional_services CASCADE;
DROP TABLE IF EXISTS utilities_expenses CASCADE;
DROP TABLE IF EXISTS bank_finance_charges CASCADE;
DROP TABLE IF EXISTS travel_expenses CASCADE;
DROP TABLE IF EXISTS vat_payments CASCADE;
DROP TABLE IF EXISTS corporation_tax CASCADE;

-- ====================================
-- REVENUE TABLES (6 tables)
-- ====================================

