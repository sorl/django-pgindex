from setuptools import setup, find_packages
from setuptools.command.test import test


class TestCommand(test):
    def run(self):
        from tests.runtests import runtests
        runtests()


setup(
    name='django-pgindex',
    version='0.8.1',
    description='Search for Django and PostgreSQL',
    long_description=open('README.rst').read(),
    author='Mikko Hellsing',
    author_email='mikko@aino.se',
    license='BSD',
    url='https://github.com/aino/django-pgindex',
    platforms='any',
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    cmdclass={"test": TestCommand},
    install_requires=[
        'django-stringfield>=0.1.5',
        'django-cerial>=0.0.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
)

