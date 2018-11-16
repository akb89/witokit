#!/usr/bin/env python3
"""witokit setup.py.

This file details modalities for packaging the witokit application.
"""

from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='witokit',
    description='A python module to generate a tokenized dump of Wikipedia for NLP',
    author='Alexandre Kabbach',
    author_email='akb@3azouz.net',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.1.1',
    url='https://github.com/akb89/witokit',
    download_url='https://pypi.org/project/witokit/#files',
    license='MIT',
    keywords=['wikipedia', 'dump', 'tokenization', 'nlp'],
    platforms=['any'],
    packages=['witokit', 'witokit.utils', 'witokit.exceptions',
              'witokit.logging'],
    package_data={'witokit': ['logging/*.yml']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'witokit = witokit.main:main'
        ],
    },
    install_requires=['PyYAML==3.13', 'wikiextractor==3.0.3', 'spacy==2.0.12',
                      'en_core_web_sm==2.0.0', 'natsort==5.4.1',
                      'beautifulsoup4==4.6.3'],
    dependency_links=[
        'https://github.com/akb89/wikiextractor/tarball/master#egg=wikiextractor-3.0.3',
        'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.0.0/en_core_web_sm-2.0.0.tar.gz'],
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Intended Audience :: Education',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Text Processing :: Linguistic'],
    zip_safe=False,
)
