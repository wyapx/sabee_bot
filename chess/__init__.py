from . import app
from . import core

export = app.export
def reload_child():
    global export
    from core.helpers import reload_modules
    reload_modules([app, core])
    export = app.export
