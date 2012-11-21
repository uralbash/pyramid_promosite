import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'pyramid_jinja2',
    'Babel',
    'lingua',
    'pytils',
    'PyRSS2Gen',
    ]

setup(name='pyramid_promosite',
      version='0.0',
      description='pyramid_promosite',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Svintsov Dmitry',
      author_email='spam@19216801.ru',
      url='http://github.com/uralbash/pyramid_promosite',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyramid_promosite',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pyramid_promosite:main
      [console_scripts]
      initialize_pyramid_promosite_db = pyramid_promosite.scripts.initializedb:main
      """,
      )
