from core.events import app
from core.loader import manager
from core.helpers import interval
from core.config import conf
from sabee_line.app import save

if __name__ == '__main__':
    #conf.set("storage", "total_handle", 0)
    print(manager.load_modules())
    interval(300, save)
    app.run()
    conf.save()
