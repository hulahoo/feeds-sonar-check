import os

from dataclasses import dataclass
from environs import Env


@dataclass
class DBConfig:
    name: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class APPConfig:
    dagster_home: str
    dagit_enabled: bool
    config_path: str


@dataclass
class Config:
    db: DBConfig
    app: APPConfig


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        db=DBConfig(
            name=env.str('APP_POSTGRESQL_NAME'),
            user=env.str('APP_POSTGRESQL_USER'),
            password=env.str('APP_POSTGRESQL_PASSWORD'),
            host=env.str('APP_POSTGRESQL_HOST'),
            port=env.str('APP_POSTGRESQL_PORT')
        ),
        app=APPConfig(
            dagster_home=os.path.expanduser(env.str('DAGSTER_HOME')),
            dagit_enabled=env.bool('DAGIT_ENABLED'),
            config_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dagster.yaml')
        )
    )


settings = load_config('.env')
