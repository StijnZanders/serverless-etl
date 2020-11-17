from setuptools import setup

with open ("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name="serverless_etl",
    version="0.1",
    scripts=[],
    author="Stijn Zanders",
    author_email="zandersstijn@gmail.com",
    description="Serverless DAGs orchestrated via Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StijnZanders/serverless-etl",
    packages=[],
    classifiers=[
        "Programming Langauge :: Python :: 3",
        "License :: OSI Approved :: ?"
        "Operating System :: OS Independent"
    ]
)
