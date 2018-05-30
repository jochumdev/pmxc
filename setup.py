import codecs
import os
from setuptools import setup, find_packages

# abspath here because setup.py may be __main__, in which case
# __file__ is not guaranteed to be absolute
here = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    """Open a related file and return its content."""
    with codecs.open(os.path.join(here, filename), encoding='utf-8') as f:
        content = f.read()
    return content


README = read_file('README.rst')
CHANGELOG = read_file('CHANGELOG.rst')
CONTRIBUTORS = read_file('CONTRIBUTORS.rst')

REQUIREMENTS = [
    'aiohttp',
    'texttable',
]

UVLOOP_REQUIRES = [
    'uvloop',
]

PERFORMANCE_REQUIRES = [
    'cchardet',
    'aiodns',
]

DEVELOPMENT_REQUIRES = [
    'pycodestyle==2.3.1', # version pin for flake8 and prospector
    'pylint',
    'autopep8',
    'flake8',
    'ipython',
    'prospector[with_pyroma]',
    'zest.releaser',
]

ENTRY_POINTS = {
    'console_scripts': [
        'pmxc = pmxc.__main__:main'
    ]
}

setup(name='pmxc',
      version='5.2.0.0.dev0',
      description='',
      long_description='{}\n\n{}\n\n{}'.format(
          README, CHANGELOG, CONTRIBUTORS),
      license='MIT',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='Console Proxmox PVE',
      author='René Jochum',
      author_email='rene@jochums.at',
      url='https://git.lxch.eu/pcdummy/pmxc-py',
      packages=find_packages(),
      package_data={'': ['*.rst', '*.py', '*.yaml']},
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      extras_require={
          'development': DEVELOPMENT_REQUIRES,
          'performance': PERFORMANCE_REQUIRES,
          'uvloop': UVLOOP_REQUIRES,
      },
      entry_points=ENTRY_POINTS)
