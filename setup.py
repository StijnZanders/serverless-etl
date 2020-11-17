from setuptools import setup

with open ("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="limber",
    version="0.0.1",
    scripts=[],
    author="Stijn Zanders",
    author_email="zandersstijn@gmail.com",
    description="Serverless DAGs orchestrated via Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StijnZanders/limber",
    packages=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ?"
        "Operating System :: OS Independent"
    ]
)
