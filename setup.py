import os
from setuptools import setup

install_requires = [
    ('loguru', '0.6.0'),
    ('python-dotenv', '0.21.0'),
    ('environs', '9.5.0'),
    ('psycopg2-binary', '2.9.5'),
    ('requests', '2.27.1'),
    ('beautifulsoup4', '4.11.1'),
    ('stix2-elevator', '4.1.7'),
    ('stix2', '3.0.1'),
    ('flatdict', '4.0.1'),
    ('confluent-kafka', '1.9.2'),
    ('kafka-python', '2.0.2'),
    ('dagster', '1.0.17'),
    ('dagit', '1.0.17'),
    ('flask-restplus', '0.13.0'),
    ('Flask', '1.1.2'),
    ('Flask-WTF', '1.0.1')
]

CI_PROJECT_NAME = os.environ.get(
    "CI_PROJECT_NAME", "feeds-importing-worker").replace("-", "_")
ARTIFACT_VERSION = os.environ.get("ARTIFACT_VERSION", "local")
CI_PROJECT_TITLE = os.environ.get(
    "CI_PROJECT_TITLE", "Воркер Импорта и Дедубликации Фидов")
CI_PROJECT_URL = os.environ.get(
    "CI_PROJECT_URL", "https://gitlab.in.axept.com/rshb/feeds-importing-worker")


setup(
    name=CI_PROJECT_NAME,
    version=ARTIFACT_VERSION,
    description=CI_PROJECT_TITLE,
    url=CI_PROJECT_URL,
    install_requires=[">=".join(req) for req in install_requires],
    python_requires=">=3.9.1",
    entry_points={
        'console_scripts': [
            CI_PROJECT_NAME +
            " = " +
            CI_PROJECT_NAME +
            ":main"
        ]
    }
)
