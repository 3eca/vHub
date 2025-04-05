from flask import Flask, render_template, request, flash, redirect, send_from_directory, url_for, abort
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from secrets import token_hex
from utils import *
from admin.admin import administrator
from api.api import api
from swagger.swagger import swagger
from os import path


LOGER = get_logger(path.basename(__file__))
create_db()
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
app.config["SQLALCHEMY_DATABASE_URI"] = ENGINE
app.config['SESSION_COOKIE_NAME'] = 'vhub'
app.config['SECRET_KEY'] = token_hex()

app.register_blueprint(administrator, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(swagger, url_prefix='/swagger')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db.init_app(app)
with app.app_context():
    db.create_all()
    defaults()


@app.template_filter('truncate_name')
def truncate_name(name):
    """
    Jinja2 template
    """
    if len(name) > 27:
        return ''.join(name[:27]) + '...'
    return name


@app.template_filter('valid_frame')
def valid_frame(frame):
    """
    Jinja2 template
    """
    if frame:
        return temporary_link_s3(frame)
    return f'static/frames/empty_frame.jpg'


@app.errorhandler(404)
def page_404(e):
    return render_template(
        '40X.html',
        data={'code': 404, 'message': 'Not Found.'}
        ), 404


@app.errorhandler(403)
def page_403(e):
    return render_template(
        '40X.html',
        data={'code': 403, 'message': 'Access Denied.'}
        ), 403


@app.route('/', methods=['GET'])
@login_required
async def index():
    """
    Root page
    """
    return render_template(
        'index.html',
        data=user_data(current_user.id),
        admin=current_user.admin,
        owner=True
        )


@app.route('/my-video', methods=['POST', 'GET'])
@login_required
async def my_video():
    """
    Page with uploaded user videos
    """
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_video_user(
            user_id=current_user.id,
            search=request.form['search'],
            page=page
            )
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_video_user(
            user_id=current_user.id,
            search=request.args['search'],
            page=page
            )
        search = request.args['search']
    else:
        results = get_video_user(user_id=current_user.id, page=page)
    return render_template(
        'videos.html',
        data=results,
        admin=current_user.admin,
        search=search,
        my_video=True
        )


@app.route('/login', methods=['POST', 'GET'])
async def login():
    """
    Login page
    """
    if request.method == 'POST':
        if not request.form['email-name'] or not request.form['password']:
            flash('Empty input fields.')
            LOGER.info(
                f'{login.__name__}(): Empty fields form <Email or name>: "{request.form["email-name"]}" or password: *****. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return render_template('login.html')
        user = exists_user(request.form['email-name'])
        if not user:
            flash('Invalid user.')
            LOGER.info(
                f'{login.__name__}(): user "{request.form["email-name"]}" not found. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}.'
                )
            return render_template('login.html')
        if not user.check_password(request.form['password']):
            flash('Invalid password.')
            LOGER.info(
                f'{login.__name__}(): invalid password for user "{request.form["email-name"]}". '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return render_template('login.html')
        if user.blocked:
            flash('User <{0}> blocked.'.format(user.name))
            LOGER.info(
                f'{login.__name__}(): try to log in a blocked user "{request.form["email-name"]}". '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return render_template('login.html')
        login_user(user)
        LOGER.info(
            f'{login.__name__}(): user "{request.form["email-name"]}" is logged on. '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
@login_required
async def logout():
    LOGER.info(
        f'{logout.__name__}(): user "{current_user.name}" logout. '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}.'
        )
    logout_user()
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(user_id: int):
    return get_short_user(user_id)


@app.route('/group/<int:_id>', methods=['GET'])
@login_required
async def group_info(_id: int):
    """
    Group details
    """
    try:
        data = get_gp(Groups, GroupsUser, GroupsVideo, _id)
        return render_template(
            'gp.html',
            data=sorting(data),
            admin=current_user.admin,
            groups=True
            )
    except db.exc.NoResultFound:
        abort(404)


@app.route('/playlist/<int:_id>', methods=['GET'])
@login_required
async def playlist_info(_id):
    """
    Playlist details
    """
    try:
        data = get_gp(Playlists, PlaylistsUser, PlaylistsVideo, _id)
        return render_template(
            'gp.html',
            data=sorting(data),
            admin=current_user.admin,
            playlists=True
            )
    except db.exc.NoResultFound:
        abort(404)


@app.route('/group/<int:_id>/video', methods=['POST', 'GET'])
@login_required
async def group_video(_id: int):
    """
    All the videos in group
    """
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_gp_video(
            Groups,
            GroupsVideo,
            _id,
            search=request.form['search'],
            page=page
        )
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_gp_video(
            Groups,
            GroupsVideo,
            _id,
            search=request.args['search'],
            page=page
        )
        search = request.args['search']
    else:
        results = get_gp_video(
            Groups,
            GroupsVideo,
            _id,
            page=page
        )
    return render_template(
            'videos.html',
            data=results,
            admin=current_user.admin,
            search=search,
            groups=True,
            _id=_id
            )


@app.route('/playlist/<int:_id>/video', methods=['POST', 'GET'])
@login_required
async def playlist_video(_id: int):
    """
    All the videos in playlist
    """
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_gp_video(
            Playlists,
            PlaylistsVideo,
            _id,
            search=request.form['search'],
            page=page
        )
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_gp_video(
            Playlists,
            PlaylistsVideo,
            _id,
            search=request.args['search'],
            page=page
        )
        search = request.args['search']
    else:
        results = get_gp_video(
            Playlists,
            PlaylistsVideo,
            _id,
            page=page
        )
    return render_template(
            'videos.html',
            data=results,
            admin=current_user.admin,
            search=search,
            playlists=True,
            _id=_id
            )


@app.route('/available-video', methods=['POST', 'GET'])
@login_required
async def available_video():
    """
    All videos available to user
    """
    page = request.args.get('page', 1, type=int)
    search = None
    if request.form.get('search', None):
        results = get_available_video(
            user_id=current_user.id,
            search=request.form['search'],
            page=page
        )
        search = request.form['search']
    elif request.args.get('search', None) and not request.form.get('search', None):
        results = get_available_video(
            user_id=current_user.id,
            search=request.args['search'],
            page=page
        )
        search = request.args['search']
    else:
        results = get_available_video(user_id=current_user.id, page=page)
    return render_template(
        'videos.html',
        data=results,
        admin=current_user.admin,
        search=search,
        available=True
        )


@app.route('/video/<link>', methods=['GET'])
async def play_video(link):
    """404:
        when not found in the database;
        when not found in the minio;
       403:
        when a user does not have access to the group/playlist in which the video was added;
        when the time to access the shared video expired;
        when the video is not shared
    """
    data = video_data(link)
    if not data:
        LOGER.info(f'{play_video.__name__}(): "{link}" not found.')
        abort(404)
    try:
        get_file_s3(data["link"])
    except S3Error:
        LOGER.info(f'{play_video.__name__}(): "{data["name"]}" is missing.')
        abort(404)
    if isinstance(current_user, AnonymousUserMixin):
        if not data['expiry_share']:
            LOGER.info(f'{play_video.__name__}(): "{data["name"]}" not available for anonymous.')
            abort(403)
        elif data['expiry_share'] and data['expiry_share'] < datetime.datetime.now():
            LOGER.info(f'{play_video.__name__}(): "{data["name"]}" has expired for sharing.')
            abort(403)
        LOGER.info(f'{play_video.__name__}(): "{data["name"]}" not available for anonymous.')
        return render_template(
            'video.html',
            video=temporary_link_s3(data["link"]),
            data=data,
            anonymous=True
            )
    else:
        access = any(_ in data['video_groups'] for _ in user_data(current_user.id)['user_groups'])
        owner = current_user.id == data['owner_id']
        if not current_user.admin and not access and current_user.id != data['owner_id'] and not data['expiry_share']:
            LOGER.info(f'{login.__name__}(): user "{current_user.name}" not have access for video "{data["name"]}".')
            abort(403)
        if data['expiry_share'] and data['expiry_share'] < datetime.datetime.now():
            data['expiry_share'] = False
        return render_template(
            'video.html',
            video=temporary_link_s3(data["link"]),
            data=data,
            admin=current_user.admin,
            owner=owner
            )


if __name__ == '__main__':
    pass
