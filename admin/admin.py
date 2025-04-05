from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from utils.database import *
from utils.models import *
from utils.additionally import *


administrator = Blueprint(
    'admin',
    __name__,
    template_folder='templates'
    )


@administrator.route('/', methods=['GET'])
@login_required
async def root():
    """
    Admin page
    """
    if not current_user.admin:
        abort(403)
    return render_template('admin/admin.html', data=current_user.id)


@administrator.route('/groups', methods=['POST', 'GET'])
@login_required
async def groups():
    """
    Complete information about all groups with number of users and videos
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_full_gp(
            Groups,
            GroupsUser,
            GroupsVideo,
            search=request.form['search'],
            page=page
            )
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_full_gp(
            Groups,
            GroupsUser,
            GroupsVideo,
            search=request.args['search'],
            page=page
            )
        search = request.args['search']
    else:
        results = get_full_gp(Groups, GroupsUser, GroupsVideo, page=page)
    return render_template(
        'admin/tables.html',
        data=results,
        search=search,
        groups=True
        )


@administrator.route('/playlists', methods=['POST', 'GET'])
@login_required
async def playlists():
    """
    Complete information about all playlists with number of users and videos
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_full_gp(
            Playlists,
            PlaylistsUser,
            PlaylistsVideo,
            search=request.form['search'],
            page=page)
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_full_gp(
            Playlists,
            PlaylistsUser,
            PlaylistsVideo,
            search=request.args['search'],
            page=page)
        search = request.args['search']
    else:
        results = get_full_gp(Playlists, PlaylistsUser, PlaylistsVideo, page=page)
    return render_template(
        'admin/tables.html',
        data=results,
        search=search,
        playlists=True
        )


@administrator.route('/users', methods=['POST', 'GET'])
@login_required
async def users():
    """
    All users information
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_users(search=request.form['search'], page=page)
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_users(search=request.args['search'], page=page)
        search = request.args['search']
    else:
        results = get_users(page=page)
    return render_template(
        'admin/tables.html',
        data=results,
        search=search,
        users=True
        )


@administrator.route('/user/<int:_id>', methods=['GET'])
@login_required
async def user(_id: int):
    """
    Advanced user information
    """
    if not current_user.admin:
        abort(403)
    data = user_data(_id)
    if not data:
        abort(404)
    return render_template(
        'index.html',
        data=data,
        admin=current_user.admin
        )


@administrator.route('/user/<int:_id>/video', methods=['POST', 'GET'])
@login_required
async def user_video(_id: int):
    """
    User's videos
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_video_user(user_id=_id, search=request.form['search'], page=page)
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_video_user(user_id=_id, search=request.args['search'], page=page)
        search = request.args['search']
    else:
        results = get_video_user(user_id=_id, page=page)
    return render_template(
        'admin/user-video.html',
        data=results,
        search=search,
        _id=_id
        )


@administrator.route('/shared-video', methods=['POST', 'GET'])
@login_required
async def shared_video():
    """
    Get all the shared videos
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_shared_video(search=request.form['search'], page=page)
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_shared_video(search=request.args['search'], page=page)
        search = request.args['search']
    else:
        results = get_shared_video(page=page)
    return render_template(
            'admin/tables.html',
            data=results,
            search=search,
            shared_video=True
            )


@administrator.route('/blocked-users', methods=['POST', 'GET'])
@login_required
async def blocked_users():
    """
    get all blocked users
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_blocked_users(search=request.form['search'], page=page)
        search = search=request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_blocked_users(search=request.args['search'], page=page)
        search = request.args['search']
    else:
        results = get_blocked_users(page=page)
    return render_template(
        'admin/tables.html',
        data=results,
        search=search,
        blocked_user=True
        )


@administrator.route('/all-video', methods=['POST', 'GET'])
@login_required
async def all_video():
    """
    Get all videos
    """
    if not current_user.admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_all_video(search=request.form['search'], page=page)
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_all_video(search=request.args['search'], page=page)
        search = request.args['search']
    else:
        results = get_all_video(page=page)
    return render_template(
        'admin/tables.html',
        data=results,
        search=search,
        all_video=True
    )


if __name__ == '__main__':
    pass
