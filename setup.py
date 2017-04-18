import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as r_file:
    readme = r_file.read()


setup(
    name='yesaide',
    version='1.1.1',
    license='MIT',
    author='Bastien Gandouet',
    author_email='bastien@ouihelp.fr',
    long_description=readme,
    packages=find_packages(),
    test_suite='tests',
    install_requires=[
        'SQLAlchemy>=1.0',
        'voluptuous>=0.8',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
