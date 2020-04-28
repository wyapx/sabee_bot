from . import app
from . import compoments
from . import spider

export = app.export

def reload_child():
    global export
    from core.helpers import reload_modules
    reload_modules([app, compoments, spider])
    export = app.export
