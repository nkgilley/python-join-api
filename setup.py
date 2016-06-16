from setuptools import setup

setup(name='python-join-api',
      version='0.0.1',
      description='Python API for viewing Plex activity',
      url='https://github.com/nkgilley/python-join-api',
      author='Nolan Gilley',
      license='MIT',
      install_requires=['requests>=2.0'],
      packages=['pyjoin'],
      zip_safe=True)
