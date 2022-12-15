import os
from setuptools import setup, find_packages

install_requires = [
    ("alembic", "1.8.1"),
    ("aniso8601", "9.0.1"),
    ("anyio", "3.6.2"),
    ("backoff", "2.2.1"),
    ("certifi", "2022.12.7"),
    ("charset-normalizer", "2.1.1"),
    ("click", "8.1.3"),
    ("coloredlogs", "14.0"),
    ("croniter", "1.3.8"),
    ("dagit", "1.1.6"),
    ("dagster", "1.1.6"),
    ("dagster-graphql", "1.1.6"),
    ("docstring-parser", "0.15"),
    ("environs", "9.5.0"),
    ("fsspec", "2022.11.0"),
    ("gql", "3.4.0"),
    ("graphene", "3.2.1"),
    ("graphql-core", "3.2.3"),
    ("graphql-relay", "3.2.0"),
    ("greenlet", "2.0.1"),
    ("grpcio", "1.47.2"),
    ("grpcio-health-checking", "1.43.0"),
    ("h11", "0.14.0"),
    ("httptools", "0.5.0"),
    ("humanfriendly", "10.0"),
    ("idna", "3.4"),
    ("Jinja2", "3.1.2"),
    ("Mako", "1.2.4"),
    ("MarkupSafe", "2.1.1"),
    ("marshmallow", "3.19.0"),
    ("multidict", "6.0.3"),
    ("packaging", "21.3"),
    ("pendulum", "2.1.2"),
    ("protobuf", "3.20.3"),
    ("psycopg2", "2.9.5"),
    ("pyparsing", "3.0.9"),
    ("python-dateutil", "2.8.2"),
    ("python-dotenv", "0.21.0"),
    ("pytz", "2022.6"),
    ("pytzdata", "2020.1"),
    ("PyYAML", "6.0"),
    ("requests", "2.28.1"),
    ("requests-toolbelt", "0.10.1"),
    ("six", "1.16.0"),
    ("sniffio", "1.3.0"),
    ("SQLAlchemy", "1.4.45"),
    ("starlette", "0.23.1"),
    ("tabulate", "0.9.0"),
    ("tomli", "2.0.1"),
    ("toposort", "1.7"),
    ("tqdm", "4.64.1"),
    ("typing_extensions", "4.4.0"),
    ("universal_pathlib", "0.0.21"),
    ("urllib3", "1.26.13"),
    ("uvicorn", "0.20.0"),
    ("uvloop", "0.17.0"),
    ("watchdog", "2.2.0"),
    ("watchfiles", "0.18.1"),
    ("websockets", "10.4"),
    ("yarl", "1.8.2"),
    ('Flask', '1.1.2'),
    ('Flask-WTF', '1.0.1'),
    ('prometheus-client', '0.15.0')
]

CI_PROJECT_NAME = os.environ.get("CI_PROJECT_NAME", "feeds-importing-worker")
ARTIFACT_VERSION = os.environ.get("ARTIFACT_VERSION", "local")
CI_PROJECT_TITLE = os.environ.get("CI_PROJECT_TITLE", "Воркер импорта фидов")
CI_PROJECT_URL = os.environ.get("CI_PROJECT_URL", "https://gitlab.in.axept.com/rshb/feeds-importing-worker")


setup(
    name=CI_PROJECT_NAME,
    version=ARTIFACT_VERSION,
    description=CI_PROJECT_TITLE,
    url=CI_PROJECT_URL,
    install_requires=[">=".join(req) for req in install_requires],
    python_requires=">=3.9.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            CI_PROJECT_NAME + " = " + "feeds_importing_worker.main:execute",
        ]
    }
)
