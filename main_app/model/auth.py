from dataclasses import dataclass


@dataclass(init=False)
class Auth:
    access_token: str
    refresh_token: str
    fullName: str
    username: str
    userId: int
    comId: int

    def from_json(self, json_data: dict):
        for key, value in json_data.items():
            setattr(self, key, value)
