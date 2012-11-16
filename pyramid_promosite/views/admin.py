from pyramid_promosite.models import (
    DBSession,
    Page,
    )
from pyramid.view import view_config


@view_config(route_name='admin',
             renderer='admin/index.jinja2',
             permission="authenticated")
def admin(request):
    pages = DBSession.query(Page).filter(Page.orign_page_id == 0).\
            order_by(Page.position).all()
    return dict(pages=pages)
