from setuptools import setup, find_packages

setup(
    name="log-center",  # PyPI package name
    version="0.1.0",
    description="A logging API and client for collecting, querying, and managing log entries via FastAPI.",
    author="R. Kyle Norris",
    author_email="r.kyle.norris@gmail.com",
    url="https://github.com/rkylenorris/log-center",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.20.0",
        "sqlalchemy>=1.4",
        "pydantic>=1.10",
        "requests>=2.28",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
