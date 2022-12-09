from dataclasses import dataclass

from environs import Env


@dataclass
class KAFKAConfig:
    server: str
    data_proccessing_topic: str


@dataclass
class DBConfig:
    name: str
    user: str
    password: str
    host: str
    port: str


@dataclass
class Config:
    kafka: KAFKAConfig
    db: DBConfig


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        kafka=KAFKAConfig(
            server=env.str('KAFKA_HOST'),
            data_proccessing_topic=env.str('DATA_PROCCESSING_TOPIC'),
        ),
        db=DBConfig(
            name=env.str('POSTGRES_DB'),
            user=env.str('POSTGRES_USER'),
            password=env.str('POSTGRES_PASSWORD'),
            host=env.str('POSTGRES_SERVER'),
            port=env.str('POSTGRES_PORT')
        )
    )


settings = load_config('.env')
