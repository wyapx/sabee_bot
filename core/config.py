import os
import json

conf_path = "config.json"

base_config = {
    "basic": {
        "host": "127.0.0.1",
        "port": 8080,
        "auth_key": "",
        "use_websocket": True,
        "bind_qq": 1145141919,
        "command_head": "+"
    },
    "permission": {
        "operator": [2190945952]
    },
    "active": {
        "group_id": []
    },
    "banner": {
        "qq_id": [],
        "group_id": []
    },
    "plugins": {
        "active": ["admin.app"],
    },
    "storage": {}
}


class JsonConfigParser:
    def __init__(self, config: dict):
        self.config = config

    def _dict_sync(self, source: dict, target: dict):
        for k, v in source.items():
            if isinstance(v, dict):
                self._dict_sync(v, target[k])
            else:
                target[k] = v

    def update(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError
        with open(path, "r") as raw:
            data = raw.read()
        try:
            self._dict_sync(
                json.loads(data),
                base_config
            )
        except json.decoder.JSONDecodeError as e:
            print("Error: ConfigFile is not load")
            print("reason:", e)
            exit(0)

    def get(self, segment: str, block=None):
        if segment in self.config:
            result = self.config[segment]
            if not block:
                return result
            elif block in result:
                return result[block]
            raise KeyError(f"block {block} is not exist")
        raise KeyError(f"segment {segment} is not exist")

    def sets(self, segment: str, data: dict):
        if segment not in self.config:
            raise KeyError(f"segment {segment} is not exist")
        for k, v in data.items():
            self.config[segment][k] = v

    def set(self, segment: str, block, data):
        if segment in self.config:
            self.config[segment][block] = data
        else:
            raise KeyError(f"block {block} is not exist")

    def save(self, path=conf_path):
        with open(path, "w") as f:
            f.write(
                json.dumps(self.config, indent=2)
            )


conf = JsonConfigParser(base_config)
if not os.path.exists(conf_path):
    print(f"Warning: {conf_path} not found, regenerating...")
    conf.save()
else:
    conf.update(conf_path)
