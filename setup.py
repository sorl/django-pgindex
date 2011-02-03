from os.path import abspath, dirname, join as pjoin
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


fn = abspath(pjoin(dirname(__file__), 'README.rst'))
fp = open(fn, 'r')
long_description = fp.read()
fp.close()

setup(
    name='django-pgindex',
    version='0.1',
    url='https://github.com/aino/django-pgindex',
    license='BSD',
    author='Mikko Hellsing',
    author_email='mikko@aino.se',
    description='Search for Django and PostgreSQL',
    long_description=long_description,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
    ],
    packages=[
        'pgindex',
    ],
    platforms='any',
    # we don't want eggs
    zip_safe=False,
)

