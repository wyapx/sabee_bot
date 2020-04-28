from . import app

export = app.export

def reload_child():
    global export
    from core.helpers import reload_modules
    reload_modules([app])
    export = app.export
