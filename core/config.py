import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:12345@localhost/crm"
)
JWT_SECRET = os.getenv("JWT_SECRET", "myjwtsecret")
JWT_ALGORITHM = "HS256"


