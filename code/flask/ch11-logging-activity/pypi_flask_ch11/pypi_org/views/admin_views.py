import flask
import logbook

from pypi_org.infrastructure import permissions
from pypi_org.infrastructure.view_modifiers import response
from pypi_org.services import cms_service
from pypi_org.viewmodels.admin.editpage_viewmodel import EditPageViewModel
from pypi_org.viewmodels.admin.editredirect_viewmodel import EditRedirectViewModel
from pypi_org.viewmodels.admin.pageslist_viewmodel import PagesListViewModel
from pypi_org.viewmodels.admin.redirectlist_viewmodel import RedirectListViewModel
from pypi_org.viewmodels.shared.viewmodelbase import ViewModelBase

blueprint = flask.Blueprint('admin', __name__, template_folder='templates')
log = logbook.Logger('cms_admin')


@blueprint.route('/admin')
@permissions.admin
@response(template_file='admin/index.html')
def index():
    vm = ViewModelBase()
    log.info(f"User viewing admin index: {vm.user.email}")
    return vm.to_dict()


@blueprint.route('/admin/redirects')
@permissions.admin
@response(template_file='admin/redirects.html')
def redirects():
    vm = RedirectListViewModel()
    log.info(f"User viewing redirects: {vm.user.email}")
    return vm.to_dict()


@blueprint.route('/admin/pages')
@permissions.admin
@response(template_file='admin/pages.html')
def pages():
    vm = PagesListViewModel()
    log.info(f"User viewing pages: {vm.user.email}")
    return vm.to_dict()


# ADD_REDIRECT VIEWS ####################################
#
#
@blueprint.route('/admin/add_redirect', methods=['GET'])
@permissions.admin
@response(template_file='admin/edit_redirect.html')
def add_redirect_get():
    vm = EditRedirectViewModel()
    return vm.to_dict()


@blueprint.route('/admin/add_redirect', methods=['POST'])
@permissions.admin
@response(template_file='admin/edit_redirect.html')
def add_redirect_post():
    vm = EditRedirectViewModel()
    vm.process_form()

    if not vm.validate():
        log.notice(f"User cannot add new redirect, error: {vm.user.email} - {vm.error}.")
        return vm.to_dict()

    cms_service.create_redirect(vm.name, vm.short_url, vm.url, vm.user.email)
    log.notice(f"User adding new redirect: {vm.user.email}, {vm.name} --> {vm.short_url}.")

    return flask.redirect('/admin/redirects')


# EDIT_REDIRECT VIEWS ####################################
#
#
@blueprint.route('/admin/edit_redirect/<int:redirect_id>', methods=['GET'])
@permissions.admin
@response(template_file='admin/edit_redirect.html')
def edit_redirect_get(redirect_id: int):
    vm = EditRedirectViewModel(redirect_id)
    if not vm.redirect:
        return flask.abort(404)

    return vm.to_dict()


@blueprint.route('/admin/edit_redirect/<int:redirect_id>', methods=['POST'])
@permissions.admin
@response(template_file='admin/edit_redirect.html')
def edit_redirect_post(redirect_id: int):
    vm = EditRedirectViewModel(redirect_id)
    vm.process_form()

    if not vm.validate():
        log.notice(f"User cannot edit redirect, error: {vm.user.email} - {vm.error}.")
        return vm.to_dict()

    cms_service.update_redirect(vm.redirect_id, vm.name, vm.short_url, vm.url)
    log.notice(f"User edited redirect: {vm.user.email}, {vm.name} --> /{vm.short_url}.")

    return flask.redirect('/admin/redirects')


# ADD_PAGE VIEWS ####################################
#
#
@blueprint.route('/admin/add_page', methods=['GET'])
@permissions.admin
@response(template_file='admin/edit_page.html')
def add_page_get():
    vm = EditPageViewModel()
    return vm.to_dict()


@blueprint.route('/admin/add_page', methods=['POST'])
@permissions.admin
@response(template_file='admin/edit_page.html')
def add_page_post():
    vm = EditPageViewModel()
    vm.process_form()

    if not vm.validate():
        log.notice(f"User cannot add new page: {vm.user.email}, {vm.error}.")
        return vm.to_dict()

    cms_service.create_page(vm.title, vm.url, vm.contents, vm.user.email, vm.is_shared)
    log.notice(f"User adding new page: {vm.user.email}, {vm.title} --> {vm.url}.")

    return flask.redirect('/admin/pages')


# EDIT_PAGE VIEWS ####################################
#
#
@blueprint.route('/admin/edit_page/<int:page_id>', methods=['GET'])
@permissions.admin
@response(template_file='admin/edit_page.html')
def edit_page_get(page_id):
    vm = EditPageViewModel(page_id)
    return vm.to_dict()


@blueprint.route('/admin/edit_page/<int:page_id>', methods=['POST'])
@permissions.admin
@response(template_file='admin/edit_page.html')
def edit_page_post(page_id: int):
    vm = EditPageViewModel(page_id)
    vm.process_form()

    if not vm.validate():
        log.notice(f"User cannot edit page: {vm.user.email}, {vm.error}.")
        return vm.to_dict()

    cms_service.update_page(vm.page_id, vm.title, vm.url, vm.contents, vm.is_shared)
    log.notice(f"User editing page: {vm.user.email}, {vm.title} --> {vm.url}.")

    return flask.redirect('/admin/pages')
