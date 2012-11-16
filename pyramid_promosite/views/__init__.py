from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
    )

from pyramid_promosite.models import (
    DBSession,
    Page,
    )
from pyramid_promosite.views.pages import get_settings

from pyramid.events import subscriber
from pyramid.events import BeforeRender
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_registry
from pyramid.i18n import get_locale_name

from sqlalchemy import or_


@subscriber(BeforeRender)
def add_global(event):
    settings = get_current_registry().settings
    event['settings'] = get_settings()
    event['languages'] = settings['available_languages'].split()
    locale = get_locale_name(event['request'])
    event['partition'] = DBSession.query(Page).\
                         filter(Page.visible == True).\
                         filter(Page.parent_id == 0).\
                         filter(Page.language == locale).\
                         filter(or_(Page.orign_page.has(Page.parent_id == 0),
                                    Page.orign_page_id == 0)).\
                         order_by(Page.position).all()

    event['logged_in'] = authenticated_userid(event['request'])


@view_config(route_name='home', renderer='index.jinja2')
def index(request):
    return {}


@view_config(route_name='lang')
def lang(request):
    lang_name = request.matchdict['name']
    response = HTTPFound(location=request.environ['HTTP_REFERER'])
    response.set_cookie('_LOCALE_', value=lang_name,
                        max_age=31536000)  # max_age = year
    return response


@view_config(context=HTTPNotFound, renderer='error/404.jinja2')
def not_found(self, request):
    request.response.status = 404
    return {}


@view_config(context=Exception,
             renderer='error/500.jinja2')
def server_error(self, request):
    request.response.status = 500
    return {'context': self}
