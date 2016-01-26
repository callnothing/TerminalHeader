# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

setup(
    name="TerminalHeader",
    version="0.10",
    description="Add File Header use Terminal",
    author="Alan Wang",
    author_email="wangchengchao115@gmail.com",
    license="GPL",
    packages=find_packages(),
    include_package_data=True,
    data_files=[
        ('theader/etc', ['theader/etc/FileHeader.default']),
        # ('theader/template', ['theader/template']),
    ],
    package_data={'': ['*.tmpl']},
    #   'theader/template/body': ['*.tmpl', 'theader/template/body/*.tmpl']},
    entry_points={
        'console_scripts': [
            'theader = theader.__main__:main',
        ]
    },
)
