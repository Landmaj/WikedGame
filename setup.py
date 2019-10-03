from setuptools import find_packages, setup

requirements = ["lxml==4.2.5", "click==7.0"]
test_requirements = []

setup(
    name="WikedGame",
    version="0.0.1",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    extras_require={"dev": test_requirements},
    entry_points={"console_scripts": ["wiked_parser = wiked.dump.cli:main"]},
    license="GPL",
    author="Michał Wieluński",
    author_email="michal@w-ski.dev",
    description="Find the shortest path between two articles on Wikipedia.",
    url="https://github.com/landmaj/WikedGame",
)
