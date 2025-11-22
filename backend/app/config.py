"""
Application configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Application
    APP_NAME: str = "ClickBank Affiliate SaaS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_VERSION: str = "v1"

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 300

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Anthropic (Claude AI)
    ANTHROPIC_API_KEY: str

    # ClickBank
    CLICKBANK_API_KEY: str = ""
    CLICKBANK_DEVELOPER_KEY: str = ""
    CLICKBANK_CLERK_KEY: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_STARTER: str = ""
    STRIPE_PRICE_PROFESSIONAL: str = ""
    STRIPE_PRICE_AGENCY: str = ""

    # Email - Postmark
    POSTMARK_API_KEY: str = ""
    POSTMARK_FROM_EMAIL: str = ""

    # Email - SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""

    # SMS - Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_CONTENT: str = ""
    AWS_S3_BUCKET_UPLOADS: str = ""
    AWS_S3_BUCKET_BACKUPS: str = ""

    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"

    # Logging
    LOG_LEVEL: str = "INFO"
    BETTER_STACK_SOURCE_TOKEN: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = '["http://localhost:5173", "http://localhost:3000"]'

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_STARTER: str = "100/hour"
    RATE_LIMIT_PROFESSIONAL: str = "500/hour"
    RATE_LIMIT_AGENCY: str = "2000/hour"

    # Feature Flags
    FEATURE_SMS_NOTIFICATIONS: bool = False
    FEATURE_WHITE_LABEL: bool = True
    FEATURE_API_ACCESS: bool = True

    # Tier Limits
    STARTER_CONTENT_LIMIT: int = 50
    STARTER_CAMPAIGNS_LIMIT: int = 1
    STARTER_STORAGE_GB: int = 5

    PROFESSIONAL_CONTENT_LIMIT: int = 200
    PROFESSIONAL_CAMPAIGNS_LIMIT: int = 10
    PROFESSIONAL_STORAGE_GB: int = 50

    AGENCY_CONTENT_LIMIT: int = 999999
    AGENCY_CAMPAIGNS_LIMIT: int = 999999
    AGENCY_STORAGE_GB: int = 500

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        import json
        return json.loads(self.CORS_ORIGINS)

    @property
    def tier_limits(self) -> dict:
        """Get tier limits as dictionary"""
        return {
            "starter": {
                "content": self.STARTER_CONTENT_LIMIT,
                "campaigns": self.STARTER_CAMPAIGNS_LIMIT,
                "storage_gb": self.STARTER_STORAGE_GB
            },
            "professional": {
                "content": self.PROFESSIONAL_CONTENT_LIMIT,
                "campaigns": self.PROFESSIONAL_CAMPAIGNS_LIMIT,
                "storage_gb": self.PROFESSIONAL_STORAGE_GB
            },
            "agency": {
                "content": self.AGENCY_CONTENT_LIMIT,
                "campaigns": self.AGENCY_CAMPAIGNS_LIMIT,
                "storage_gb": self.AGENCY_STORAGE_GB
            }
        }


# Create global settings instance
settings = Settings()
