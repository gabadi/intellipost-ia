"""
Database seeding utilities for ensuring default data exists.

This module provides functions to seed the database with default data
that should exist for the application to function properly.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.config.settings import Settings
from infrastructure.database import AsyncSessionLocal
from infrastructure.config.logging import get_logger

logger = get_logger(__name__)


async def ensure_default_admin_user(
    settings: Settings,
    session: Optional[AsyncSession] = None
) -> bool:
    """
    Ensure the default admin user exists in the database.
    
    Args:
        settings: Application settings containing admin credentials
        session: Optional database session to use
        
    Returns:
        True if user was created, False if user already existed
    """
    if session is None:
        async with AsyncSessionLocal() as db_session:
            return await ensure_default_admin_user(settings, db_session)
    
    admin_email = settings.user_default_admin_email
    admin_password = settings.user_default_admin_password
    
    # Check if admin user already exists
    result = await session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {'email': admin_email}
    )
    existing_user = result.fetchone()
    
    if existing_user:
        logger.info(f"Default admin user already exists: {admin_email}")
        return False
    
    # Hash the password
    password_hash = bcrypt.hashpw(
        admin_password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Create the admin user
    admin_user_data = {
        'id': str(uuid.uuid4()),
        'email': admin_email,
        'password_hash': password_hash,
        'first_name': 'Admin',
        'last_name': 'User',
        'status': 'active',
        'is_active': True,
        'is_email_verified': True,
        'failed_login_attempts': 0,
        'last_failed_login_at': None,
        'password_reset_token': None,
        'password_reset_expires_at': None,
        'email_verification_token': None,
        'ml_user_id': None,
        'ml_access_token': None,
        'ml_refresh_token': None,
        'ml_token_expires_at': None,
        'default_ml_site': 'MLA',
        'auto_publish': False,
        'ai_confidence_threshold': 'medium',
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
        'last_login_at': None,
        'email_verified_at': datetime.now(timezone.utc),
    }
    
    # Insert admin user
    await session.execute(
        text("""
            INSERT INTO users (
                id, email, password_hash, first_name, last_name, status,
                is_active, is_email_verified, failed_login_attempts,
                last_failed_login_at, password_reset_token, password_reset_expires_at,
                email_verification_token, ml_user_id, ml_access_token, ml_refresh_token,
                ml_token_expires_at, default_ml_site, auto_publish, ai_confidence_threshold,
                created_at, updated_at, last_login_at, email_verified_at
            ) VALUES (
                :id, :email, :password_hash, :first_name, :last_name, :status,
                :is_active, :is_email_verified, :failed_login_attempts,
                :last_failed_login_at, :password_reset_token, :password_reset_expires_at,
                :email_verification_token, :ml_user_id, :ml_access_token, :ml_refresh_token,
                :ml_token_expires_at, :default_ml_site, :auto_publish, :ai_confidence_threshold,
                :created_at, :updated_at, :last_login_at, :email_verified_at
            )
        """),
        admin_user_data
    )
    
    await session.commit()
    logger.info(f"Created default admin user: {admin_email}")
    return True


async def seed_database(settings: Settings) -> None:
    """
    Seed the database with default data.
    
    Args:
        settings: Application settings
    """
    logger.info("Starting database seeding...")
    
    try:
        await ensure_default_admin_user(settings)
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise


if __name__ == "__main__":
    # Allow running this script directly for testing
    from infrastructure.config.settings import settings
    
    asyncio.run(seed_database(settings))