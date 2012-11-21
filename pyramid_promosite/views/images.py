import os
import glob
import time

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.config.views import StaticURLInfo


def get_static_dir(request):
    registrations = set(StaticURLInfo()._get_registrations(request.registry))
    registrations = registrations - set([(None, 'pyramid_debugtoolbar:static/',
        '___debug_toolbar/static/'),
        (None, 'pyramid_promosite:static/', '__static/')])
    static_dir = list(registrations)
    if static_dir:
        static_dir = static_dir[0][2][2:]
    else:
        static_dir = 'static/'

    return static_dir


@view_config(route_name='admin_object',
             match_param=("object=image", "action=upload"),
             renderer='json', permission="image_create")
def upload_image(request):
    path = request.registry.settings.get('redactor_images')

    filename = str(time.time()) + request.POST['file'].filename
    input_file = request.POST['file'].file

    # Using the filename like this without cleaning it is very
    # insecure so please keep that in mind when writing your own
    # file handling.
    file_path = os.path.join(path, filename)
    output_file = open(file_path, 'wb')

    # Finally write the data to the output file
    input_file.seek(0)
    while 1:
        data = input_file.read(2 << 16)
        if not data:
            break
        output_file.write(data)
    output_file.close()

    static_dir = get_static_dir(request)
    return {"filelink": "/" + static_dir + "uploaded/images/" + filename}


@view_config(route_name='admin_object',
             match_param=("object=image", "action=GetJson"),
             renderer='json', permission="image_read")
def imageGetJson(request):
    path = request.registry.settings.get('redactor_images')
    types = ('*.jpg', '*.jpeg', '*.gif')  # the tuple of file types

    static_dir = get_static_dir(request)
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(path + "/" + files))
    images = []
    for file in files_grabbed:
        file = file.replace(path, "")
        images.append({"thumb": "/" + static_dir + "uploaded/images/" + file,
             "image": "/" + static_dir + "uploaded/images/" + file,
             "title": file, "folder": "images"})

    return images


@view_config(route_name='admin_object',
             match_param=("object=image", "action=view"),
             renderer='admin/view_image.jinja2',
             permission="image_read")
def view_image(request):
    path = request.registry.settings.get('redactor_images')
    types = ('*.jpg', '*.jpeg', '*.gif')  # the tuple of file types

    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(path + "/" + files))

    images = []
    for file in files_grabbed:
        file = file.replace(path, "")[1:]
        images.append(file)

    return dict(images=images, static_dir=get_static_dir(request))


@view_config(route_name='admin_object_target',
             match_param=("object=image", "action=delete"),
             permission="image_delete")
def del_image(request):
    image = request.matchdict['target']
    path = request.registry.settings.get('redactor_images')
    os.unlink(path + "/" + image)

    return HTTPFound(location=request.route_url('admin_object',
                     action='view', object='image'))
