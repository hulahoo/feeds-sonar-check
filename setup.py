import os
from setuptools import setup, find_packages

install_requires = [
    ('flake8', '5.0.4'),
    ('python-dotenv', '0.21.0'),
    ('psycopg2-binary', '2.9.5'),
    ('sqlalchemy', '1.4.44'),
    ('Flask', '1.0.1'),
    ('flask-restplus', '0.13.0'),
    ('Flask-WTF', '1.0.1'),
    ('alembic', '1.8.1'),
    ('prometheus-client', '0.15.0'),
    ('environs', '9.5.0'),
    ('dagster', '1.1.6'),
    ('dagit', '1.1.6'),
    ('jsonpath-ng', '1.5.3'),
]

CI_PROJECT_NAME = os.environ.get("CI_PROJECT_NAME", "feeds-importing-worker")
ARTIFACT_VERSION = os.environ.get("ARTIFACT_VERSION", "0.1")
CI_PROJECT_TITLE = os.environ.get("CI_PROJECT_TITLE", "Воркер импорта фидов")
CI_PROJECT_URL = os.environ.get("CI_PROJECT_URL", "https://gitlab.in.axept.com/rshb/feeds-importing-worker")

setup(
    name=CI_PROJECT_NAME,
    version=ARTIFACT_VERSION,
    description=CI_PROJECT_TITLE,
    url=CI_PROJECT_URL,
    install_requires=[">=".join(req) for req in install_requires],
    python_requires=">=3.10.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            CI_PROJECT_NAME + " = " + "feeds_importing_worker.main:execute",
        ]
    },
    include_package_data=True,
    package_data={
        "feeds_importing_worker.config": ["dagster.yaml"],
    },
)
