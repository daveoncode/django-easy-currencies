import os

from setuptools import setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-easy-currencies',
    version='0.2.0',
    packages=['django_easy_currencies'],
    install_requires=['django', 'Babel>=1.3'],
    include_package_data=True,
    license='MIT License',
    description='Simple app to manage currencies conversion in Django using openexchangerates.org service.',
    url='https://github.com/daveoncode/django-easy-currencies',
    author='Davide Zanotti',
    author_email='davidezanotti@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
