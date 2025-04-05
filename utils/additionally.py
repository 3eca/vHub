from io import BytesIO
from re import match
from moviepy.editor import VideoFileClip, ImageClip
import matplotlib.pyplot as plt
from utils.database import *
from secrets import choice
from string import ascii_letters, digits


ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'flv'}


def generate_passwd() -> str:
    """
    Password generation.
    """
    symbols = ascii_letters + digits
    return ''.join(choice(symbols) for _ in range(12))


def allowed_file(filename) -> bool:
    """
    Check file extension for presence in available extensions.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_file_bytes(path_file: str) -> BytesIO:
    """
    Returns the file in bits as an object.
    """
    with open (path_file, 'rb') as file:
        return BytesIO(file.read())


def get_frame(path_video: str, path_frame: str) -> bool:
    """
    Get frame preview.
    """
    video = VideoFileClip(path_video)
    frame = video.get_frame(1)
    correct_frame = ImageClip(frame).resize((150, 200))
    plt.imsave(path_frame, correct_frame.img)
    video.close()


def validate_email(email: str) -> bool:
    """
    Email validation.
    """
    try:
        return match(r"^\S+@\S+\.\S+$", email).group()
    except AttributeError:
        return False


def sorting_access_user(dict_a: dict) -> dict:
    """
    Word processing.
    """
    temp_dict = {
        'user': '',
        'on': {},
        'off': {},
    }
    temp_dict['user'] = dict_a['user']
    temp_dict['on']['GroupsUser'] = set(data.split('-')[-1] for data in dict_a['on'] if 'group' in data)
    temp_dict['on']['PlaylistsUser'] = set(data.split('-')[-1] for data in dict_a['on'] if 'playlist' in data)
    temp_dict['off']['GroupsUser'] = set(data.split('-')[-1] for data in dict_a['off'] if 'group' in data)
    temp_dict['off']['PlaylistsUser'] = set(data.split('-')[-1] for data in dict_a['off'] if 'playlist' in data)
    return temp_dict


def sorting(data: list) -> tuple:
    """
    Sort playlist|group data to an acceptable form.
    """
    return (
        data[0][0],
        data[0][1],
        {element[2]: element[3] for element in data},
        data[0][-2],
        data[0][-1]
        )


def user_data(user_id: int) -> dict:
    """
    User data aggregation.
    """
    data = {}
    user = get_full_user(user_id)
    groups = get_short_gp(Groups)
    playlists = get_short_gp(Playlists)
    user_groups = set(row[6:8] for row in user)
    user_playlists = set(row[8:10] for row in user)
    user_groups_sort = intersection(user_groups, groups)
    user_playlists_sort = intersection(user_playlists, playlists)
    if user:
        data['id'] = user[0][0]
        data['name'] = user[0][1]
        data['email'] = user[0][2]
        data['date'] = user[0][3]
        data['blocked'] = user[0][4]
        data['admin'] = user[0][5]
        data['user_groups'] = user_groups
        data['user_playlists'] = user_playlists
        data['groups'] = juxtaposition(groups, user_groups_sort)
        data['playlists'] = juxtaposition(playlists, user_playlists_sort)
        data['count_videos'] = 0 if user[0][-1] is None else len(set(row[10:] for row in user))
    return data


def intersection(list_a: list, list_b: list) -> dict:
    """
    Filtering set and available playlist groups\playlists.
    """
    temp_dict = {v: k for k, v in list_b if k}
    enabled = set(temp_dict[seq_a[-1]] for seq_a in list_a if seq_a[-1] in temp_dict.keys())
    all = set(v for v in temp_dict.values())
    result = {
        'enabled': enabled,
        'disabled': all - enabled
        }
    return result


def juxtaposition(list_a: list, dict_a: dict) -> tuple:
    """
    Matches occurrences of the set in the dictionary.
    => new dictionary of the form {'enabled': ((set_a[0], set_a[1]),), 'disabled': ((set_a[0], set_a[1]),),}
    """
    enabled = tuple((_id, name) for _id, name in list_a for v in dict_a['enabled'] if _id==v)
    disabled = tuple((_id, name) for _id, name in list_a for v in dict_a['disabled'] if _id==v)
    result = {
        'enabled': enabled,
        'disabled': disabled,
        }
    return result


def video_data(link: str) -> dict:
    """
    Vidoe data aggregation.
    """
    data = {}
    video = get_video(link=link)
    video_groups = get_video_gp(Groups, GroupsVideo, link=link)
    video_playlists = get_video_gp(Playlists, PlaylistsVideo, link=link)
    groups = get_short_gp(Groups)
    playlists = get_short_gp(Playlists)
    video_groups_sort = intersection(video_groups, groups)
    video_playlists_sort = intersection(video_playlists, playlists)
    if video:
        data['id'] = video[0]
        data['name'] = video[1]
        data['date'] = video[2]
        data['link'] = video[3]
        data['expiry_share'] = video[4]
        data['owner_id'] = video[5]
        data['owner'] = video[6]
        data['video_groups'] = video_groups
        data['video_playlists'] = video_playlists
        data['groups'] = juxtaposition(groups, video_groups_sort)
        data['playlists'] = juxtaposition(playlists, video_playlists_sort)
    return data


def sorting_access(data: dict, table_m: str, table_s: str) -> dict:
    """
    Word processing.
    """
    temp_dict = {
        'link': '',
        'on': {},
        'off': {},
    }
    temp_dict['link'] = data['link']
    temp_dict['on'][table_m] = set(row.split('-')[-1] for row in data['on'] if 'group' in row)
    temp_dict['on'][table_s] = set(row.split('-')[-1] for row in data['on'] if 'playlist' in row)
    temp_dict['off'][table_m] = set(row.split('-')[-1] for row in data['off'] if 'group' in row)
    temp_dict['off'][table_s] = set(row.split('-')[-1] for row in data['off'] if 'playlist' in row)
    return temp_dict


def check_keys(keys: tuple, data: dict)-> bool:
    """
    Check if the required keys are present in json.
    """
    return tuple(True if req_key in data.keys() else False for req_key in keys)


if __name__ == '__main__':
    pass
