from setuptools import setup, find_packages

version = '0.1'

long_description = open('README.rst').read() \
    + '\n\n' \
    + open('CHANGES.rst').read()

setup(name='khufu_javascript',
      version=version,
      description=('Khufu/Pyramid component for managing javascript '
                   'resources'),
      long_description=long_description,
      classifiers=[],
      keywords='khufu pyramid pylons',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points='',
      )
