# flask_ext.pyi
from sqlite3 import Connection
from flask.ctx import _AppCtxGlobals

class AppCtxGlobals(_AppCtxGlobals):
    db: Connection

def __getattr__(name: str) -> AppCtxGlobals: ...