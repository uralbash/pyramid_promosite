from pyramid_promosite.models import (
    Base,
    DBSession,
    Page,
    )

from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    ALL_PERMISSIONS,
    )


class User(Base):
    __tablename__ = 'pps_users'
    id = Column(Integer, primary_key=True)
    login = Column(Text, unique=True)
    password = Column(Text)
    groups = Column(Text)

    def __init__(self, login, password, groups=None):
        self.login = login
        self.password = password
        self.groups = groups or ""

    def check_password(self, passwd):
        return self.password == passwd


def get_user(login):
    user = DBSession.query(User).filter(User.login == login).all()
    if user:
        return user[0]
    else:
        return None


def get_page(key):
    page = DBSession.query(Page).filter(Page.id == key).all()
    if page:
        page = page[0]
    else:
        page = Page('', '', '', '', '')
    return page


class RootFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
        (Allow, 'g:admin', 'admin'),
        (Allow, 'g:moderator', 'page_create'),
        (Allow, 'g:moderator', 'page_read'),
        (Allow, 'g:moderator', 'page_update'),
        (Allow, 'g:moderator', 'page_delete'),
        (Allow, 'g:moderator', 'page_sort'),
        (Allow, 'g:moderator', 'image_create'),
        (Allow, 'g:moderator', 'image_read'),
        (Allow, 'g:moderator', 'image_update'),
        (Allow, 'g:moderator', 'image_delete'),
        (Allow, 'g:moderator', 'settings'),
        (Allow, 'g:editor', 'page_create'),
        (Allow, 'g:editor', 'page_read'),
        (Allow, 'g:editor', 'page_update'),
        (Allow, 'g:editor', 'page_delete'),
        (Allow, 'g:editor', 'page_sort'),
        (Allow, 'g:editor', 'image_create'),
        (Allow, Everyone, 'page_read'),
        (Allow, Authenticated, 'page_create'),
        (Allow, Authenticated, 'page_sort'),
        (Allow, Authenticated, 'authenticated'),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        page = get_page(key)
        page.__parent__ = self
        page.__name__ = key
        return page
