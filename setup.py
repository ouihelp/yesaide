import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as r_file:
    readme = r_file.read()


setup(
    name="yesaide",
    version="1.6.2dev",
    license="MIT",
    author="Ouihelp Tech",
    author_email="tech@ouihelp.fr",
    long_description=readme,
    packages=find_packages(),
    test_suite="tests",
    install_requires=[
        "SQLAlchemy>=1.3,<2.1",
        "voluptuous>=0.10.5,<0.12",
        "jwcrypto>=0.6,<0.7",
        "python-dateutil>=2,<3",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
