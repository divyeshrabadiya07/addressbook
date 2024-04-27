from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a sqlite engine instance which will store database in address_book.db file
sqlite_engine = create_engine("sqlite:///address_book.db")

# Create a SessionLocal class for session maker
SessionLocal = sessionmaker(bind=sqlite_engine, expire_on_commit=False)

# Create a Base class for all ORM classes
BaseClass = declarative_base()
