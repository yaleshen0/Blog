import sqlite3
from flask_sqlalchemy import SQLAlchemy
import click
from flask import current_app, g

def get_db():
    '''
    onnect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE_URL"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    '''
    If this request connected to the database, close the
    connection.
    '''
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    '''
    Clearing existing data and create new tables.
    '''
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    db.commit()
    
@click.command('init-db')
def init_db_command():
    '''
    Clear existing data and create new tables.
    '''
    init_db()
    click.echo("Database initialized")

def init_app(app):
    '''
    Register database functions with the Flask App. 
    This is called by the application factory.
    '''
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    