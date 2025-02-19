import sqlite3
from flask import g


DATABASE = './app/database/bakery.db'


def get_db():
    """Opens a connection to the database.
    
    Raises:
        sqlite3.Error: if the database connection cannot be established

    Returns:
        sqlite3.Connection: the database connection
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_db():
    """Closes the connection to the database.

    Raises:
        sqlite3.Error: if the operation fails
    """
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

