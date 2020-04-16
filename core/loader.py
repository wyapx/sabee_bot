from mirai import logger
from importlib import import_module, reload
from typing import List
from .config import conf

"""
struct:
{
   "active": [af]，
   "inactive": [iaf],
   "command": {"cm": "cmd"}
   "help": {"mod_name": {"cm": "info"}}
}
"""


class PluginsManager:
    def __init__(self, mods_path: list):
        self.mp = mods_path
        self.active = []
        self.inactive = []
        self.command = {}
        self.help = {}

    def _flush(self):
        self.active.clear()
        self.inactive.clear()
        self.command.clear()
        self.help.clear()

    def _parse_export(self, export: dict):
        for k, v in export.items():
            if k == "active":
                self.active.extend(v)
            elif k == "inactive":
                self.inactive.extend(v)
            elif k == "command":
                self.command.update(v)
            elif k == "help":
                self.help.update(v)

    def load_modules(self, reload_module=False) -> List[Exception]:
        self._flush()
        error = []
        for path in self.mp:
            try:
                mod = import_module(path)
                if reload_module:
                    reload(mod)
                self._parse_export(mod.export)
            except Exception as e:
                logger.Session.exception(f"reload error in module {path}:")
                error.append(e)
                continue
        return error

    def reload_modules(self) -> List[Exception]:
        return self.load_modules(reload_module=True)


manager = PluginsManager(conf.get("plugins", "active"))
