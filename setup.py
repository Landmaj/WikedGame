from setuptools import (
    setup,
    find_packages,
)

requirements = [
    "py2neo==4.1.0",
    "psutil==5.4.7",
]

setup(
    name="WikedGame",
    version="0.0.1",
    packages=find_packages(),
    install_requires=requirements,
    license="GPL",
    author="Michał Wieluński",
    author_email="michal@landmaj.pl",
    description="Find the shortest path between two articles on Wikipedia.",
)
