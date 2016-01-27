# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

setup(
    name="TerminalHeader",
    version="0.31",
    description="Add File Header use Terminal",
    author="Alan Wang",
    author_email="wangchengchao115@gmail.com",
    license="GPL",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.tmpl', 'FileHeader.default']},
    entry_points={
        'console_scripts': [
            'theader = theader.__main__:main',
        ]
    },
)
