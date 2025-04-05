from functools import wraps
import os
from uuid import uuid4
from werkzeug.wsgi import FileWrapper

from flask import Blueprint, request, jsonify
from flask_login import current_user

from utils import *
from utils.models import *


LOGER = get_logger(os.path.basename(__file__))
api = Blueprint(
    'api',
    __name__
    )


def check_cookie_decorator(func):
    """
    Checks if a cookie is present in the request and if it matches the current user.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session_cookie = request.cookies.get('vhub')
        if not session_cookie:
            return jsonify(status=False, message="No session cookie provided."), 401

        if not current_user.is_authenticated:
            return jsonify(status=False, message="Session cookie is invalid or user is not authenticated."), 401

        return await func(*args, **kwargs)

    return wrapper


@api.route('/video/edit', methods=['POST'])
@check_cookie_decorator
async def video_edit():
    """
    Edit video data
    """
    data = request.json
    if 'videoName' in data.keys():
        old_name = set_video_name(data['link'], data['videoName'])
        LOGER.info(
            f'{video_edit.__name__}(): user "{current_user.name}" update video "{old_name}" with link "{data["link"].split(".")[0]}". '
            f'New name: "{data["videoName"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
    if {'on', 'off'} & data.keys():
        try:
            sorting_data = sorting_access(request.json, 'GroupsVideo', 'PlaylistsVideo')
            for table, value in sorting_data['on'].items():
                for _id in value:
                    set_access_video(True, table, sorting_data['link'], int(_id))
            for table, value in sorting_data['off'].items():
                for _id in value:
                    set_access_video(False, table, sorting_data['link'], int(_id))
            LOGER.info(
                f'{video_edit.__name__}(): user "{current_user.name}" edit video with link "{data["link"].split(".")[0]}". '
                f'New access: enable - "{sorting_data["on"]}" and disable - "{sorting_data["off"]}. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=True)
        except Exception as err:
            LOGER.error(
                f'{video_edit.__name__}(): unknown error with edit video "{data["videoName"]}"\n{err}. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=False, message='Unknown error.')
    return jsonify(status=True)


@api.route('/video/share', methods=['POST'])
@check_cookie_decorator
async def video_share():
    """
    Adding a property to access video without authorization
    """
    data = request.json
    if not os.environ['VHUB_SHARED_VIDEO'] and data['state']:
        LOGER.error(
            f'{video_share.__name__}(): user "{current_user.name}" can\'t share video "{data["videoName"]}" with link "{data["videoLink"].split(".")[0]}". Share is disabled. '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Share video disabled.')
    if not all(check_keys(('videoLink', 'state'), data)):
        LOGER.error(
            f'{video_share.__name__}(): user "{current_user.name}" can\'t share video "{data["videoName"]}". Missing data: '
            f'"video": "{data["videoName"]}", link "{data["videoLink"].split(".")[0]}", "state": "{data["state"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    if share_video(data['videoLink'], data['state']):
        LOGER.info(
            f'{video_share.__name__}(): user "{current_user.name}" sharred="{data["state"]}" video "{data["videoName"]}" with link "{data["videoLink"].split(".")[0]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=True)
    LOGER.error(
        f'{video_share.__name__}(): user "{current_user.name}" couldn\'t find video "{data["videoName"]}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=False, message='Not found video.')
    

@api.route('/group/add', methods=['POST'])
@check_cookie_decorator
async def group_add():
    """
    Adding a group
    """
    data = request.json
    if not check_keys(('name'), data):
        LOGER.error(
            f'{group_add.__name__}(): user "{current_user.name}" could not add a group, missing name: "{data["name"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    LOGER.info(
        f'{group_add.__name__}(): user "{current_user.name}" added a group "{data["name"]}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=new_gp(Groups, data['name'].lower()))


@api.route('/playlist/add', methods=['POST'])
@check_cookie_decorator
async def playlist_add():
    """
    Adding a playlist
    """
    data = request.json
    if not check_keys(('name'), data):
        LOGER.error(
            f'{playlist_add.__name__}(): user "{current_user.name}" could not add a laylist, missing name: "{data["name"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    LOGER.info(
        f'{playlist_add.__name__}(): user "{current_user.name}" added a playlist"{data["name"]}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=new_gp(Playlists, data['name'].lower()))


@api.route('/user/add', methods=['POST'])
@check_cookie_decorator
async def user_add():
    """
    Adding a user
    """
    data = request.json
    if not all(check_keys(('name', 'email'), data)):
        LOGER.error(
            f'{user_add.__name__}(): user "{current_user.name}" can\'t added a user "{data["name"]}". Missing data: "name": '
            f'"{data["name"]}", "email": "{data["email"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    if not validate_email(data['email']):
        LOGER.error(
            f'{user_add.__name__}(): user "{current_user.name}" can\'t added a user "{data["name"]}". Invalid email: "{data["email"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status =False, message='Invalid email.')
    if 'pwd' in data.keys():
        state = new_user(data['name'].lower(), data['email'].lower(), data['pwd'])
    else:
        if not os.environ['VHUB_EMAIL']:
            LOGER.error(
                f'{user_add.__name__}(): user "{current_user.name}" can\'t send email to user "{data["name"]}". Email is disabled. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=False, message='Fail send email. Email is disabled.')
        password = generate_passwd()
        state = new_user(data['name'].lower(), data['email'].lower(), password)
        if not send_email(data['email'], password):
            LOGER.error(
                f'{user_add.__name__}(): user "{current_user.name}" can\'t send email to user "{data["name"]}". Check email property. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=False, message='Fail send email. Email is disabled.')
    LOGER.info(
        f'{user_add.__name__}(): user "{current_user.name}" added a user "{data["name"]}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=state, message='Duplicate name or email.')


@api.route('/user/access', methods=['POST'])
@check_cookie_decorator
async def user_access():
    """
    Set|revoke user access
    """    
    try:
        data = request.json
        sorting_data = sorting_access_user(data)
        for table, value in sorting_data['on'].items():
            for _id in value:
                set_access_user('on', table, sorting_data['user'], int(_id))
        for table, value in sorting_data['off'].items():
            for _id in value:
                set_access_user('off', table, sorting_data['user'], int(_id))
        LOGER.info(
            f'{user_access.__name__}(): user "{current_user.name}" edit a user "{data["user"]}". New access: enable - '
            f'"{sorting_data["on"]}" and disable - "{sorting_data["off"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=True)
    except Exception as err:
        LOGER.error(
            f'{user_access.__name__}(): unknown error with edit user "{data["user"]}"\n{err}. '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Unknown error.')


@api.route('/user/state', methods=['POST'])
@check_cookie_decorator
async def user_state():
    """
    Ban|unban user
    """
    data = request.json
    if not all(check_keys(('userID', 'userName', 'state'), data)):
        LOGER.error(
            f'{user_state.__name__}(): user "{current_user.name}" can\'t change state a user "{data["userName"]}". Missing data: '
            f'"ID": "{data["userID"]}", "name": "{data["userName"]}", "state": "{data["state"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'   
            )
        return jsonify(status=False, message='Missing data.')
    if set_user_state(data['userID'], data['state']):
        LOGER.info(
            f'{user_state.__name__}(): user "{current_user.name}" change state a user "{data["userName"]}". Blocked: "{data["state"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=True)
    LOGER.error(
        f'{user_state.__name__}(): user "{current_user.name}" fail set state a user "{data["userName"]}" . "{data}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=False, message='Fail set state.')


@api.route('/user/admin', methods=['POST'])
@check_cookie_decorator
async def user_admin():
    """
    Set|revoke administrator access for a user
    """
    data = request.json
    if not all(check_keys(('userID', 'userName', 'state'), data)):
        LOGER.error(
            f'{user_admin.__name__}(): user "{current_user.name}" can\'t change role a user "{data["userName"]}". Missing data: "ID": '
            f'"{data["userID"]}", "name": "{data["userName"]}", "state": "{data["state"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    if set_user_admin(data['userID'], data['state']):
        LOGER.info(
            f'{user_admin.__name__}(): user "{current_user.name}" change role a user "{data["userName"]}". Admin: "{data["state"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=True)
    LOGER.error(
        f'{user_admin.__name__}(): user "{current_user.name}" fail change role a user "{data["userName"]}". "{data}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=False, message='Fail change role.')


@api.route('/user/set-password', methods=['POST'])
@check_cookie_decorator
async def user_set_password():
    """
    Set a user password
    """
    data = request.json
    if not all(check_keys(('userID', 'userPwd', 'userName'), data)):
        LOGER.error(
            f'{user_set_password.__name__}(): user "{current_user.name}" can\'t change password user "{data["userName"]}". Missing data: "name" or "state". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    if set_user_pwd(data['userID'], data['userName'], data['userPwd']):
        LOGER.info(
            f'{user_set_password.__name__}(): user "{current_user.name}" change password user "{data["userName"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=True)
    LOGER.error(
        f'{user_set_password.__name__}(): user "{current_user.name}"user. "{data["userName"]}" not found or length password < 6. '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=False, message='Not found user or length password < 6.')


@api.route('/user/reset-password', methods=['POST'])
@check_cookie_decorator
async def user_reset_password():
    """
    Reset user password
    """
    data = request.json
    if not all(check_keys(('userID', 'userEmail', 'userName', 'state'), data)):
        LOGER.error(
            f'{user_reset_password.__name__}(): user "{current_user.name}" can\'t reset password a user "{data["userName"]}". Missing data: '
            '"ID" or "name" or "email" or "state". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Missing data.')
    password = generate_passwd()
    if not os.environ['VHUB_EMAIL'] == 'true':
            LOGER.error(
                f'{user_reset_password.__name__}(): user "{current_user.name}" can\'t send email a user "{data["userName"]}". Email is disabled. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=False, message='Fail send email. Email is disabled.')
    elif set_user_pwd(data['userID'], data['userName'], password, data['userEmail']):
        if not send_email(data['userEmail'], password):
            LOGER.error(
                f'{user_reset_password.__name__}(): user "{current_user.name}" can\'t send email a user "{data["userName"]}". Check email property. '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=False, message='Fail send email. Check email property or logs.')
        LOGER.info(
            f'{user_reset_password.__name__}(): user "{current_user.name}" send email with new password to user "{data["userName"]}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=True)
    LOGER.error(
        f'{user_reset_password.__name__}(): user "{current_user.name}" was unable to reset a password  user "{data["userName"]}". '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=False, message='Fail to reset password.')


@api.route('/upload', methods=['POST'])
@check_cookie_decorator
async def upload():
    """
    Upload video
    """
    print(request.files)
    if not request.files:
        LOGER.error(
            f'{upload.__name__}(): user "{current_user.name}" can\'t upload video. Missing data: {request.files}. '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(status=False, message='Empty file name or file.')
    name = tuple(name for name in request.files.keys())[0]
    if not name:
        LOGER.error(
            f'{upload.__name__}(): user "{current_user.name}" can\'t upload video. Empty file name: "{request.files}". '
            f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
            )
        return jsonify(staus=False, message='Empty file name.')
    file = request.files[name]
    
    if allowed_file(file.filename):
        file.filename = f'{str(uuid4())}.{file.content_type.split("/")[-1]}' 
        upload_video = save_video(secure_filename(name), file.filename, user_id=current_user.id)
        
        if upload_video:

            if not os.path.exists('./temp'):
                os.mkdir('./temp')

            file.save(os.path.join('./temp', f'{file.filename}'))
            frame_name = f'{str(uuid4())}.jpg'
            get_frame(
                path_video=f'temp/{file.filename}',
                path_frame=f'temp/{frame_name}'
                )
            save_frame(name=secure_filename(name), frame=frame_name)

            get_size_file = os.path.getsize(f'temp/{file.filename}')
            get_size_frame = os.path.getsize(f'temp/{frame_name}')

            upload_s3(
                object_name=file.filename,
                data=convert_file_bytes(f'temp/{file.filename}'),
                length=get_size_file,
                content_type=file.content_type
            )
            upload_s3(
                object_name=frame_name,
                data=convert_file_bytes(f'temp/{frame_name}'),
                length=get_size_frame,
                content_type='image/jpg'
            )
            os.remove(f'temp/{file.filename}')
            os.remove(f'temp/{frame_name}')

            try:
                get_file_s3(object_name=file.filename)
                LOGER.info(
                    f'{upload.__name__}(): user "{current_user.name}" upload video "{name}" with link "{file.filename.split(".")[0]}". '
                    f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                    )
                return jsonify(status=True)
            except S3Error as err:
                LOGER.error(
                    f'{upload.__name__}(): user "{current_user.name}" fail upload video "{name}". '
                    f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                    )
                LOGER.error(f'{upload.__name__}(): {err}')
                return jsonify(status=False, message='Upload failed.')
        else:
            LOGER.error(
                f'{upload.__name__}(): user "{current_user.name}" tried to upload a video with a duplicate name "{name}". '
                f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
                )
            return jsonify(status=False, message='Duplicate name.')
    LOGER.error(
        f'{upload.__name__}(): user "{current_user.name}" fail upload video "{name}". Unknow error. '
        f'Remote addr: "{request.headers["X-Forwarded-For"]}".'
        )
    return jsonify(status=False)


if __name__ == '__main__':
    pass
