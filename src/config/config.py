from dataclasses import dataclass

from environs import Env


@dataclass
class KAFKAConfig:
    server: str
    data_proccessing_topic: str


@dataclass
class DBConfig:
    name: str
    engine: str
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
            name=env.str('SQL_DATABASE'),
            engine=env.str('SQL_ENGINE'),
            user=env.str('SQL_USER'),
            password=env.str('SQL_PASSWORD'),
            host=env.str('SQL_HOST'),
            port=env.str('SQL_PORT')
        )
    )


settings = load_config('.env')
