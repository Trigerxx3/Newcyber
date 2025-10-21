from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your models
from models.user import User, SystemUser
from models.source import Source
from models.content import Content
from models.keyword import Keyword
from models.detection import Detection
from models.identifier import Identifier
from models.osint_result import OSINTResult
from models.case import Case
from models.user_case_link import UserCaseLink
from models.osint_identifier_link import OSINTIdentifierLink
from models.active_case import ActiveCase
from models.case_request import CaseRequest
from models.case_content_link import CaseContentLink

# this is the Alembic Config object
config = context.config

# Smart database selection for migrations:
# If USE_PRODUCTION_DB=true is set, use Railway PostgreSQL
# Otherwise, use local SQLite (even if DATABASE_URL exists in .env)
use_prod_db = os.getenv('USE_PRODUCTION_DB', '').lower() == 'true'

if use_prod_db:
    # Use Railway PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    print(f"🌐 Alembic: Using Railway PostgreSQL database")
else:
    # Use local SQLite
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cyber_intel.db')
    database_url = f'sqlite:///{db_path}'
    print(f"💾 Alembic: Using local SQLite database at {db_path}")

config.set_main_option('sqlalchemy.url', database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your Base
from extensions import db
target_metadata = db.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()