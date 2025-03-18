from dataclasses import dataclass
import yaml


@dataclass
class MainConfig:
    # mqtt
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    mqtt_topic: str

    # ptz
    ptz_id_function: int

    def __init__(self):
        with open('resources/config/main_config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        self.mqtt_broker = config['mqtt_broker']
        self.mqtt_port = config['mqtt_port']
        self.mqtt_username = config['mqtt_username']
        self.mqtt_password = config['mqtt_password']
        self.mqtt_topic = config['mqtt_topic']
        self.ptz_id_function = config['ptz_id_function']


mainConfig = MainConfig()
