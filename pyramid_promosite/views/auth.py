from pyramid.httpexceptions import HTTPFound
from pyramid_promosite.models.auth import get_user
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )
from pyramid_promosite.models import DBSession
from pyramid_promosite.models.auth import User


@view_config(route_name='login', renderer='admin/user/login.jinja2')
@forbidden_view_config(renderer='admin/user/login.jinja2')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''
    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        user = get_user(login)
        if user and user.check_password(password):
            headers = remember(request, login)
            return HTTPFound(location=came_from,
                             headers=headers)
        message = 'Failed login'

    return dict(
        message=message,
        url=request.application_url + '/login',
        came_from=came_from,
        login=login,
        password=password,
        )


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location=request.route_url('home'),
                     headers=headers)


@view_config(route_name='admin_object',
             match_param=("object=user", "action=view"),
             renderer='admin/user/index.jinja2',
             permission='admin')
def users_view(request):
    users = DBSession.query(User).all()
    return {'users': users}


@view_config(route_name='admin_object_target',
             match_param=("object=user", "action=view"),
             renderer='admin/user/view.jinja2',
             permission='admin')
def user_view(request):
    user_id = request.matchdict['target']
    user = DBSession.query(User).filter_by(id=user_id).one()
    return {'user': user}


@view_config(route_name='admin_object',
             match_param=("object=user", "action=add"),
             renderer='admin/user/edit.jinja2',
             permission='admin')
def add_user(request):
    if 'form.submitted' in request.params:
        login = request.params['user_login']
        groups = request.params['user_groups']
        password = request.params['user_password']
        user = User(login=login, password=password, groups=groups)
        DBSession.add(user)
        return HTTPFound(location=request.route_path('admin_object',
                         object="user", action="view"))
    user = User('', '', '')
    return dict(user=user)


@view_config(route_name='admin_object_target',
             match_param=("object=user", "action=edit"),
             renderer='admin/user/edit.jinja2',
             permission='admin')
def edit_user(request):
    user_id = request.matchdict['target']
    user = DBSession.query(User).filter_by(id=user_id).one()
    if 'form.submitted' in request.params:
        user.login = request.params['user_login']
        password = request.params['user_password']
        user.groups = request.params['user_groups']
        if password:
            user.password = password
        DBSession.add(user)
        return HTTPFound(location=request.route_path('admin_object',
                         object="user", action="view"))
    return dict(user=user)


@view_config(route_name='admin_object_target',
             match_param=("object=user", "action=delete"),
             permission='admin')
def del_user(request):
    user_id = request.matchdict['target']
    user = DBSession.query(User).filter_by(id=user_id).one()
    DBSession.delete(user)
    return HTTPFound(location=request.route_path('admin_object',
                     object="user", action="view"))
