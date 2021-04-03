"""
AWS Request Signature4
"""
import os
import re

from setuptools import setup, find_packages

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_version(package: str) -> str:
    """
    :param package:
    :return:
    """
    with open(os.path.join(BASE_DIR, f'{package}/__version__.py')) as version:
        version = version.readlines()[-1]
    match = re.search("__version__ = ['\"]([^'\"]+)['\"]", version)
    assert match is not None
    return match.group(1)


def get_log_description():
    """
    :return:
    """
    with open('README.md') as readme:
        with open('CHANGELOG.md') as changelog:
            return readme.read() + "\n\n" + changelog.read()


setup(
    name='AWSSignV4',
    version=get_version('AWSSignV4'),
    author='Vubon Roy',
    author_email='vubon.roy@gmail.com',
    description='This package will help to use AWS service without SDK',
    url='https://github.com/vubon/AWSSignV4',
    project_urls={
        "Documentation": "https://github.com/vubon/AWSSignV4/blob/master/docs/GUIDE.md"
    },
    packages=find_packages(),
    long_description=get_log_description(),
    long_description_content_type="text/markdown",
    license='MIT',
    platforms='Python',
    install_requires=[
        'requests'
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
