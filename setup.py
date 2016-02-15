from setuptools import setup

setup(name='portfolio.io.js.py',
      version='0.1',
      description='Portfolio generator',
      url='https://github.com/Dvergar/portfolio.io.js.py',
      author='caribou',
      # author_email='flyingcircus@example.com',
      license='MIT',
      # packages=['funniest'],
      install_requires=[
          'markdown',
          'PyYAML',
          'docopt',
          'spectra',
          'jinja2'
      ],
      zip_safe=False)