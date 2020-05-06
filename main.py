from core.events import app
from core.loader import manager
from core.config import conf

if __name__ == '__main__':
    conf.set("storage", "total_handle", 0)
    err = manager.load_modules()
    if not err:
        print("All module loaded")
    else:
        print("Catch some error:", err)
    try:
        app.run()
    except KeyboardInterrupt:
        print("Force Stopped")
    conf.save()
