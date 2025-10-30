-- Database initialization script for Chatty
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- But we can add any additional setup here

-- Set timezone
SET timezone = 'UTC';

-- Create a function to update the last_updated_date column
CREATE OR REPLACE FUNCTION update_last_updated_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated_date = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

