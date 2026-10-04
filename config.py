import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///healthcare.db")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
