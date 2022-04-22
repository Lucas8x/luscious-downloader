from setuptools import setup, find_packages

from luscious_dl import __author__, __version__, __email__

with open('requirements.txt') as r:
  requirements = r.readlines()

with open('README.md', encoding='utf-8') as ld:
  long_description = ld.read()

setup(
  name='luscious-downloader',
  version=__version__,
  packages=find_packages(),
  keywords='luscious, album, downloader',
  url='https://github.com/Lucas8x/luscious-downloader',
  license='MIT',
  author=__author__,
  author_email=__email__,
  description='CLI tool for downloading albums from Luscious',
  long_description=long_description,
  long_description_content_type="text/markdown",
  install_requires=requirements,
  extras_require={
    'pdf': ['Pillow>=8.2.0']
  },
  include_package_data=True,
  zip_safe=False,
  python_requires='>=3.9',
  entry_points={
    'console_scripts': [
      'lsd = luscious_dl.start:start'
    ]
  },
  classifiers=[
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Topic :: Terminals',
    'Topic :: Utilities',
  ],
  project_urls={
    'Source': 'https://github.com/Lucas8x/luscious-downloader',
    'Tracker': 'https://github.com/Lucas8x/luscious-downloader/issues'
  }
)
