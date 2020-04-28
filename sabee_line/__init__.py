from . import app


export = app.export

def reload_child():
    global export
    from core.helpers import reload_modules
    reload_modules([app])
    export = app.export

def setup():
    from core.helpers import interval
    interval(300, app.save)

