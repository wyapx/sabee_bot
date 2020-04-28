from . import app


def reload_child():
    from core.helpers import reload_modules
    reload_modules([app])

export = app.export