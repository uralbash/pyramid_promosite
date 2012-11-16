import re
import json
from sqlalchemy import func

from pyramid.httpexceptions import HTTPFound
from pyramid_promosite.models import (
    DBSession,
    Page,
    Tag,
    Settings,
    )
from pyramid.view import view_config

from pyramid.security import authenticated_userid
from pyramid.threadlocal import get_current_registry
from pyramid.i18n import get_locale_name


def get_lang(page):
    exist_translations = DBSession.query(Page).\
            filter_by(orign_page_id=page.id).all()
    exist_languages = [lang.language for lang in exist_translations]
    exist_languages.append(page.language)
    settings = get_current_registry().settings
    languages = settings['available_languages'].split()
    lang_list = list(set(languages) - set(exist_languages))
    return lang_list


@view_config(route_name='admin_object',
             match_param=("object=page", "action=add"),
             renderer='admin/edit.jinja2',
             permission="page_create")
def add_page(request):
    user = authenticated_userid(request)
    if 'form.submitted' in request.params:
        name = request.params['name']
        content = request.params['content']
        if 'visible' in request.params:
            visible = True
        else:
            visible = False
        max_id = DBSession.query(func.max(Page.id)).all()
        if max_id[0][0]:
            position = max_id[0][0] + 1
        else:
            position = 1
        page = Page(user, name, content, position, visible)
        if 'parent_id' in request.params:
            page.parent_id = request.params['parent_id']
        else:
            page.parent_id = 0
        if 'lang' in request.params:
            page.language = request.params['lang']
        if 'translated_page' in request.params:
            page.orign_page_id = request.params['translated_page']
        page.created_by = user

        page.tags = []
        tags = re.split(r'[,;]+', request.params['tags'])
        tags = filter(lambda x: x not in (None, '', ' '), tags)
        tags = map(lambda x: x.strip(), tags)
        tags = list(set(tags))
        for tag in tags:
            exist_tag = DBSession.query(Tag).filter_by(name=tag).all()
            if exist_tag:
                tag = exist_tag[0]
            else:
                tag = Tag(tag)
            page.tags.append(tag)
        DBSession.add(page)
        return HTTPFound(location=request.route_url('admin'))
    # if it child page
    if 'parent_id' in request.params:
        parent_id = request.params['parent_id']
    else:
        parent_id = ''
    LOCALE = get_locale_name(request)
    # if it translated page
    if 'add_translate' in request.params:
        translated_page_id = request.params['translated_page']
        translated_page = DBSession.query(Page).\
                               filter_by(id=translated_page_id).one()
        lang_list = get_lang(translated_page)
    else:
        lang_list = translated_page = None

    page = Page(user, '', '', '', '')
    return dict(page=page, parent_id=parent_id, translate_lang=lang_list,
                translated=translated_page, LOCALE=LOCALE)


@view_config(route_name='admin_object_target',
             match_param=("object=page", "action=edit"),
             renderer='admin/edit.jinja2',
             permission="page_update")
def edit_page(request):
    user = authenticated_userid(request)
    page_id = request.matchdict['target']
    page = DBSession.query(Page).filter_by(id=page_id).one()
    if 'form.submitted' in request.params:
        page.name = request.params['name']
        page.content = request.params['content']
        page.updated_by = user
        if 'visible' in request.params:
            page.visible = True
        else:
            page.visible = False

        page.tags = []
        tags = re.split(r'[,;]+', request.params['tags'])
        tags = filter(lambda x: x not in (None, '', ' '), tags)
        tags = map(lambda x: x.strip(), tags)
        tags = list(set(tags))
        for tag in tags:
            exist_tag = DBSession.query(Tag).filter_by(name=tag).all()
            if exist_tag:
                tag = exist_tag[0]
            else:
                tag = Tag(tag)
            page.tags.append(tag)
        DBSession.add(page)
        return HTTPFound(location=request.environ['HTTP_REFERER'])
    # if it translated page
    LOCALE = get_locale_name(request)
    translated_page = DBSession.query(Page).\
                                filter_by(id=page.orign_page_id).all()
    translated_page = translated_page[0] if translated_page else None
    if translated_page:
        exist_translations = DBSession.query(Page).\
                filter_by(orign_page_id=translated_page.id).all()
        lang_list = get_lang(translated_page)
    else:
        exist_translations = DBSession.query(Page).\
                filter_by(orign_page_id=page.id).all()
        lang_list = None
    return dict(page=page, translated=translated_page, LOCALE=LOCALE,
                exist_translations=exist_translations,
                translate_lang=lang_list)


@view_config(route_name='admin_object_target',
             match_param=("object=page", "action=delete"),
             permission="page_delete")
def del_page(request):
    page_id = request.matchdict['target']
    page = DBSession.query(Page).filter_by(id=page_id).one()
    parent_id = page.parent_id
    childs = DBSession.query(Page).filter(Page.parent_id == page_id).all()
    for child in childs:
        child.parent_id = parent_id
        DBSession.add(child)
    translations = DBSession.query(Page).\
                filter_by(orign_page_id=page_id).all()
    page = DBSession.query(Page).filter_by(id=page_id).one()
    DBSession.delete(page)
    DBSession.flush()
    for trans in translations:
        DBSession.delete(trans)
        DBSession.flush()
    return HTTPFound(location=request.route_url('admin'))


@view_config(route_name='admin_object_target',
             match_param=("object=page", "action=sort"),
             permission="page_sort")
def sort_page(request):
    page_list = request.params['page_list']
    parent_id = request.matchdict['target']
    if not page_list:
        return HTTPFound(location=request.environ['HTTP_REFERER'])
    else:
        page_list = json.loads("[" + page_list + "]")

    def sort_child(children, parent):
        for i, child in enumerate(children):
            page_id = child['id']
            ch = DBSession.query(Page).filter_by(id=page_id).one()
            ch.parent_id = parent
            ch.position = i
            DBSession.add(ch)
            if 'children' in child:
                sort_child(child['children'], ch.id)

    for i, page in enumerate(page_list):
        page_id = page['id']
        p = DBSession.query(Page).filter_by(id=page_id).one()
        if not page_id:
            p.parent_id = 0
        else:
            p.parent_id = parent_id
        p.position = i
        DBSession.add(p)
        children = page['children']
        if children:
            sort_child(children, p.id)

    return HTTPFound(location=request.environ['HTTP_REFERER'])


@view_config(route_name='view_page', renderer='view.jinja2',
             permission='page_read')
def view_page(request):
    page_name = request.matchdict['page_name']
    page_locale = get_locale_name(request)

    page = DBSession.query(Page).filter_by(translite_name=page_name).\
                                 filter_by(visible=True).one()
    # clause for choised locale
    if not page.language == page_locale:
        page_on_lang = False
        if page.orign_page_id == 0:
            page_id = page.id
        else:
            page_id = page.orign_page_id

        page_on_lang = DBSession.query(Page).\
                            filter_by(orign_page_id=page_id).\
                            filter_by(language=page_locale).all()
        if page_on_lang:
            page = page_on_lang[0]

    childs = DBSession.query(Page).filter_by(parent_id=page.id).\
                                   filter_by(visible=True).all()

    def get_breadcrumbs_chain(page):
        chain = []
        chain.append(page)
        while page.parent_id:
            page = DBSession.query(Page).filter_by(id=page.parent_id).one()
            chain.append(page)
        if len(chain) == 1:
            chain = []
        return reversed(chain)
    breadcrumbs = get_breadcrumbs_chain(page)
    return dict(page=page, childs=childs, breadcrumbs=breadcrumbs)


def get_settings():
    settings = {}
    list_of_settings = ['sitename', 'signature', 'author', 'copyright',
                        'description', 'keywords']
    for key in list_of_settings:
        setting = DBSession.query(Settings).\
                                  filter_by(name=key).all()
        if setting:
            settings[key] = setting[0]
        else:
            settings[key] = Settings(key, '')
    return settings


@view_config(route_name='admin_object',
             match_param=("object=page", "action=settings"),
             renderer='admin/settings.jinja2',
             permission="settings")
def settings(request):
    settings = get_settings()

    if 'form.submitted' in request.params:
        for key, value in settings.items():
            key_form = request.params[key]
            if not settings[key]:
                settings[key] = Settings(key, key_form)
            else:
                settings[key].value = key_form
            DBSession.add(settings[key])
        return HTTPFound(location=request.route_url('admin'))
    return dict(settings=settings)


class TreeObject(object):
    def __init__(self, id, text, state):
        self.id = str(id)
        self.text = text
        self.state = state

    def __json__(self, request):
        return {'id': self.id, 'text': self.text, 'state': self.state}


@view_config(route_name='admin_object_target',
             match_param=('object=page', 'action=get_tree'),
             renderer="json", permission="page_read")
def get_tree(request):
    '''Return child pages on demand.
    '''
    json_tree_nodes = []

    if 'id' in request.params:
        id = request.params['id']
    elif 'target' in request.matchdict:
        id = int(request.matchdict['target'])
    else:
        id = 0

    nodes = DBSession.query(Page).filter_by(parent_id=id).\
            filter_by(orign_page_id=0).\
            order_by(Page.position).all()
    for node in nodes:
        childs = DBSession.query(Page).filter_by(parent_id=node.id).\
                                       filter_by(orign_page_id=0).\
                                       order_by(Page.position).all()
        state = 'open' if not len(childs) else 'closed'
        node = TreeObject(node.id, node.name, state)
        json_tree_nodes.append(node)

    return json_tree_nodes

'''import datetime
import PyRSS2Gen


# TODO: add items
def rrs_gen(request):
    settings = get_settings()
    title = settings['sitename']
    link = request.host_url + "/static/rss/index.xml"
    description = settings['description']
    lastBuildDate = datetime.datetime.now()
    items = []
    pages = DBSession.query(Page).all()
    for page in pages:
        PyRSS2Gen.RSSItem()

    rss = PyRSS2Gen.RSS2(
        title=title,
        link=link,
        description=description,
        lastBuildDate=lastBuildDate,
        items=items)
    rss.write_xml(open("static/rss/index.xml", "w"))
'''
