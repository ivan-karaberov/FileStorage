from .config import Config
from .db.db_helper import DatabaseHelper

settings = Config()
db_helper = DatabaseHelper(
    url=settings.db.db_url,
    echo=settings.db.echo
)
