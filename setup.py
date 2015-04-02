# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


def read_relative_file(filename):
    """Returns contents of the given file, whose path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


if __name__ == '__main__':  # ``import setup`` doesn't trigger setup().
    setup(
        name='django-mail-factory',
        version=read_relative_file('VERSION').strip(),
        description="Django Mail Manager",
        long_description=read_relative_file('README.rst'),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
        ],
        keywords='django mail manager',
        author='Rémy Hubscher',
        author_email='hubscher.remy@gmail.com',
        url='https://github.com/novafloss/django-mail-factory',
        license='BSD Licence',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=['html2text']  # depends on Django
    )
