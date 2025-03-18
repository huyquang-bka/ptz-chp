from dataclasses import dataclass, field
import yaml


@dataclass
class ApiRoute:
    base_url: str = "https://crd.atin.vn"
    additional_route: str = "/Service/api"

    login_route: str = "/token/auth"
    login_payload: dict = field(default_factory=lambda: {
        "username": "string",
        "password": "string",
        "client_id": "EPS",
        "client_secret": "b0udcdl8k80cqiyt63uq",
        "grant_type": "password"
    })
    device_route: str = "/device?page=1&itemsPerPage=999"

    def __post_init__(self):
        with open("resources/config/api_route.yaml", "r") as f:
            config = yaml.safe_load(f)

        for key, value in config.items():
            setattr(self, key, value)
