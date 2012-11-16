# coding=utf8
import pytils
import urllib

from sqlalchemy import (
    event,
    Column,
    Integer,
    Text,
    Unicode,
    Boolean,
    ForeignKey,
    DateTime,
    Table,
    ForeignKeyConstraint,
    )

from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref,
    relationship,
    scoped_session,
    sessionmaker,
    )

from pyramid.security import Allow
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


pagetag_table = Table('pps_pagetag', Base.metadata,
    Column('page_id', Integer, ForeignKey('pps_pages.id',
           onupdate="CASCADE", ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('pps_tag.id',
           onupdate="CASCADE", ondelete="CASCADE"))
    )


class Page(Base):
    __tablename__ = 'pps_pages'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    translite_name = Column(Text, unique=True)
    content = Column(Text)
    position = Column(Integer)
    visible = Column(Boolean)
    parent_id = Column(Integer, ForeignKey('pps_pages.id'), default=0)
    parent = relationship("Page",
                    primaryjoin=('pps_pages.c.id==pps_pages.c.parent_id'),
                    remote_side='Page.id',
                    backref=backref("children"))

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(Integer, ForeignKey('pps_users.id'), nullable=False)
    updated_by = Column(Integer, ForeignKey('pps_users.id'), nullable=False)
    # link to page of default language
    orign_page_id = Column(Integer, ForeignKey('pps_pages.id'), default=0)
    orign_page = relationship("Page",
                    primaryjoin=('pps_pages.c.orign_page_id==pps_pages.c.id'),
                    remote_side='Page.id',
                    backref=backref("orign"))
    language = Column(Text)

    tags = relationship("Tag", secondary=pagetag_table, order_by='Tag.name',
                        cascade="all")

    __table_args__ = (
            ForeignKeyConstraint(
                ["orign_page_id", "language"],
                ["pps_pages.orign_page_id", "pps_pages.language"],
                name="fk_language_page", use_alter=True
        ),
    )

    @property
    def __acl__(self):
        return [
            (Allow, self.created_by, 'page_create'),
            (Allow, self.created_by, 'page_update'),
            (Allow, self.created_by, 'page_delete'),
        ]

    def __init__(self, updated_by, name, content='', position=0,
                 visible=False, parent_id=0):
        self.name = name
        self.content = content
        self.position = position
        self.visible = visible
        self.parent_id = parent_id
        self.updated_by = updated_by


def convert_name(name, lang):
    text = pytils.translit.translify(name)
    text = text.replace(" ", "_") + '_' + lang
    return urllib.quote(text.encode('utf-8'))


@event.listens_for(Page, "before_insert")
@event.listens_for(Page, "before_update")
def translite_name(mapper, connection, instance):
    instance.translite_name = convert_name(instance.name, instance.language)


class Tag(Base):
    __tablename__ = 'pps_tag'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class Settings(Base):
    __tablename__ = 'pps_settings'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Text)

    def __init__(self, name, value=''):
        self.name = name
        self.value = value


def initialize_sql(engine):
    import transaction
    from pyramid_promosite.models.auth import User
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    DBSession.flush()
    transaction.commit()

    if not DBSession.query(User).all():
        admin = User(login='admin', password='admin', groups='admin')
        DBSession.add(admin)
        transaction.commit()
