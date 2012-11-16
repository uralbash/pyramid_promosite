# coding=utf-8
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

from .models import DBSession
from .security import groupfinder


def add_routes(config):
    config.add_route('home', '/')
    config.add_route('view_page', '/page/{page_name}')
    config.add_route('lang', '/lang/{name}')

    config.add_route('admin', '/admin')

    # example: /admin/page/edit/2
    #          /admin/image/GetJson
    config.add_route('admin_object_target',
                     '/admin/{object}/{action}/{target}',
                     traverse='/{target}')  # for RootFactory
    config.add_route('admin_object', '/admin/{object}/{action}')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')


def includeme(config):
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'pyramid_promosite:static')
    config.include(add_routes)
    config.scan()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    settings = dict(settings)
    settings.setdefault('jinja2.i18n.domain', 'pyramid_promosite')

    config = Configurator(settings=settings,
                  root_factory='pyramid_promosite.models.auth.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    includeme(config)

    config.add_translation_dirs("pyramid_promosite:locale/")
    config.add_jinja2_search_path("pyramid_promosite:templates")

    return config.make_wsgi_app()
