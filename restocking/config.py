import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL="https://ogtqgkgueltgdhrudpil.supabase.co"
SECRET_KEY="78b634c1cceaee2cec0ecd1689a700e61e3da29814dbf9c898604e3981a2dde4"
# Basic config
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")