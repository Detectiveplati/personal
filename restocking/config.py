import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # NeonDB connection string with user and password
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_hv7TBjEmnu8f@ep-soft-dream-a1hopzci-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_hv7TBjEmnu8f@ep-soft-dream-a1hopzci-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 1,
        "max_overflow": 0,
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 10,
        },
    }