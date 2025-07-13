import os
from dotenv import load_dotenv
from pathlib import Path

basedir = Path(__file__).resolve().parent
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    if not os.getenv("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set. Application startup aborted.")
    
    SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///default.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


