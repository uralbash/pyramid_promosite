pyramid_promosite README
=

pyramid_promosite - is not CMS, this is a module that helps you quickly create a website. Pyramid_promosite is similar to django flatpages, but written in pyramid and more features.

Getting Started
-

- cd <directory containing this file>

- $venv/bin/python setup.py develop or pip install pyramid_promosite

- $venv/bin/populate_pyramid_promosite development.ini

- $venv/bin/pserve development.ini


Features
-

- admin page
- admin, moderator, editor, author role
- create and sort pages
- create translations of pages
- create subpages
- WYSIWYG editor with upload images
- tags for page if you want to create blog
- multilanguages support
- template for mobile phone ready
- flexibility

Sites
-

- http://platonaps.ru (https://github.com/uralbash/platonaps.ru/)
- your site there...

TODO
-

- RRS
- logs of users activity
- versioning pages
- autosave page
- REST

Help
-

if you have the opportunity to help the project, I would be happy to finalize:

- tests
- docs for https://readthedocs.org
- translate on other languges
- security with crypt(bcrypt or sha) and group table
- scaffolds for pcreate
- rewrite templates for true CSS, HTML design
- anything from TODO
- or anything else...

Permission
-

CRUD - create, read, update, delete

- Admin can CRUD ALL
- Moderator can CRUD all pages and images
- Editor can CRUD all pages
- Authon can CRUD only own pages

Screenshots
-

![ScreenShot](https://raw.github.com/uralbash/pyramid_promosite/master/pyramid_promosite/static/img/img1.png)

![ScreenShot](https://raw.github.com/uralbash/pyramid_promosite/master/pyramid_promosite/static/img/img2.png)

![ScreenShot](https://raw.github.com/uralbash/pyramid_promosite/master/pyramid_promosite/static/img/img3.png)

![ScreenShot](https://raw.github.com/uralbash/pyramid_promosite/master/pyramid_promosite/static/img/img4.png)
