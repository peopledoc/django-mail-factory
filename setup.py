# -*- coding: utf-8 -*-
"""Python packaging."""
from os.path import abspath, dirname, join
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


name = 'django-mail-factory'
version = read_relative_file('VERSION').strip()
readme = read_relative_file('README')
requirements = ['setuptools']
entry_points = {}


if __name__ == '__main__':  # ``import setup`` doesn't trigger setup().
    setup(name=name,
          version=version,
          description="""Django Mail Manager""",
          long_description=readme,
          classifiers=[
              "Programming Language :: Python",
              'License :: OSI Approved :: BSD License',
              'Framework :: Django',
          ],
          keywords='django mail manager',
          author=u'Rémy Hubscher',
          author_email='hubscher.remy@gmail.com',
          url='https://github.com/novagile/django-mail-factory',
          license='BSD Licence',
          packages=['mail_factory'],
          include_package_data=True,
          zip_safe=False,
          install_requires=requirements,
          entry_points=entry_points,
          )
