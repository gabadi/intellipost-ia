-- Initialize IntelliPost database for development
-- This script ensures the database and user are properly configured

-- Create extensions that might be needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE intellipost_dev TO intellipost_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO intellipost_user;

-- Set up basic schema structure (will be managed by Alembic migrations)
-- This is just to ensure the database is ready for migrations

COMMENT ON DATABASE intellipost_dev IS 'IntelliPost AI development database';
