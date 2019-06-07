from setuptools import find_packages, setup

requirements = ["lxml==4.2.5", "sqlalchemy==1.3.4", "psycopg2==2.8.2"]
test_requirements = ["pytest==4.6.2"]

setup(
    name="WikedGame",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={"dev": test_requirements},
    license="GPL",
    author="Michał Wieluński",
    author_email="michal@w-ski.dev",
    description="Find the shortest path between two articles on Wikipedia.",
)
