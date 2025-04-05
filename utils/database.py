import pymysql
from utils.models import *
from typing import Type
from sys import modules
from werkzeug.utils import secure_filename
import datetime
from os import environ, path
import utils.logs as logs


LOGER = logs.get_logger(path.basename(__file__))


ENGINE = f"mysql+pymysql://{environ['VHUB_MYSQL_USER']}:{environ['VHUB_MYSQL_PWD']}@" \
         f"{environ['VHUB_MYSQL_SRV']}/{environ['VHUB_MYSQL_DB']}?charset=utf8mb4"


def create_db() -> None:
    """
    Init database.
    """
    connect = pymysql.connect(
        host=environ['VHUB_MYSQL_SRV'],
        port=int(environ['VHUB_MYSQL_PORT']),
        user=environ['VHUB_MYSQL_USER'],
        passwd=environ['VHUB_MYSQL_PWD']
    )
    cursor = connect.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {environ['VHUB_MYSQL_DB']}")
    connect.commit()
    connect.close()


def __check(table: Type[SQLAlchemy], name: str) -> bool:
    """
    Record existence check
    True if the record exists
    False if the record does not exist
    """
    return db.session.query(table.id).filter(table.name==name).first()


def defaults() -> None:
    """
    Create a default group and playlist
    """
    if not __check(Groups, 'default'):
        db.session.add(Groups(name='default'))
        db.session.commit()
        LOGER.info(f'{defaults.__name__}(): group "default" created.')
    if not __check(Playlists, 'default'):
        db.session.add(Playlists(name='default'))
        db.session.commit()
        LOGER.info(f'{defaults.__name__}(): playlist "default" created.')
    if not __check(Users, 'admin'):
        db.session.add_all([
            Users(
            name=environ['VHUB_ADMIN_NAME'],
            email=f"{environ['VHUB_ADMIN_NAME']}@localhost.vhub",
            admin=True,
            passwd=Users.gen_password(environ['VHUB_ADMIN_PWD'])
            ),
            GroupsUser(user_id=1, link_id=1),
            PlaylistsUser(user_id=1, link_id=1)])
        db.session.commit()
        LOGER.info(f'{defaults.__name__}(): user "{environ["VHUB_ADMIN_NAME"]}" with role admin create.')


def get_short_user(user_id: int):
    return db.session.query(Users).get(user_id)


def get_full_user(user_id: int):
        """
        Retrieving user information for display on the /admin/user/<id>
        """
        return db.session.query(
            Users.id,
            Users.name,
            Users.email,
            Users.date,
            Users.blocked,
            Users.admin,
            Groups.id.label('gid'),
            Groups.name.label('gn'),
            Playlists.id.label('pid'),
            Playlists.name.label('pn'),
            Videos.id.label('vid'),
        ).select_from(Users)\
            .join(GroupsUser, GroupsUser.user_id==Users.id)\
            .join(Groups, Groups.id==GroupsUser.link_id)\
            .join(PlaylistsUser, PlaylistsUser.user_id==Users.id)\
            .join(Playlists, Playlists.id==PlaylistsUser.link_id)\
            .join(VideosUser, VideosUser.user_id==Users.id, isouter=True)\
            .join(Videos, Videos.id==VideosUser.link_id, isouter=True)\
            .filter(Users.id==user_id).all()
        

def get_short_gp(table: Type[SQLAlchemy]):
    """
    Getting data of groups|playlists.
    """
    return db.session.query(table.id, table.name).all()


def exists_user(login: str):
    """
    Checking whether a user exists to log in
    """
    user_name = db.session.query(Users).filter(Users.name==login).first()
    user_email = db.session.query(Users).filter(Users.email==login).first()
    if user_name or user_email:
        LOGER.info(f'{exists_user.__name__}(): user "{user_name.name if user_name else user_email.email}" found.')
        return user_name if user_name else user_email
    return False


def get_users(search: str='', page: int=1) -> Query:
    """
    Get all user data to display on /admin/users
    """
    cte_v = (
        db.select(
            Users.id.distinct().label('id'),
            db.func.count(Videos.id).over(partition_by=VideosUser.user_id).label('counter_video')
        ).select_from(Users)\
            .join(VideosUser, VideosUser.user_id==Users.id, isouter=True)\
            .join(Videos, Videos.id==VideosUser.link_id, isouter=True).cte('cv')
    )
    cte_g = (
        db.select(
            Users.id.distinct().label('id'),
            db.func.count(Groups.id).over(partition_by=GroupsUser.user_id).label('counter_group')
        ).select_from(Users)\
            .join(GroupsUser, GroupsUser.user_id==Users.id, isouter=True)\
            .join(Groups, Groups.id==GroupsUser.link_id, isouter=True).cte('cg')
    )
    cte_p = (
        db.select(
            Users.id.distinct().label('id'),
            db.func.count(Playlists.id).over(partition_by=PlaylistsUser.user_id).label('counter_playlist')
        ).select_from(Users)\
            .join(PlaylistsUser, PlaylistsUser.user_id==Users.id, isouter=True)\
            .join(Playlists, Playlists.id==PlaylistsUser.link_id, isouter=True).cte('cp')
    )
    if search:
        return db.paginate_rows(
        db.session.query(
            Users.id.distinct().label('id'),
            Users.name,
            Users.email,
            Users.date,
            Users.blocked,
            Users.admin,
            cte_v.c.counter_video.label('cv'),
            cte_g.c.counter_group.label('cg'),
            cte_p.c.counter_playlist.label('cp')
            ).select_from(Users)\
                .join(cte_v, cte_v.c.id==Users.id)\
                .join(cte_g, cte_g.c.id==Users.id)\
                .join(cte_p, cte_p.c.id==Users.id).order_by(Users.id)\
                .filter(Users.name.icontains(search) | Users.email.icontains(search)),
        page=page,
        per_page=20
        )
    return db.paginate_rows(
        db.session.query(
            Users.id.distinct().label('id'),
            Users.name,
            Users.email,
            Users.date,
            Users.blocked,
            Users.admin,
            cte_v.c.counter_video.label('cv'),
            cte_g.c.counter_group.label('cg'),
            cte_p.c.counter_playlist.label('cp')
            ).select_from(Users)\
                .join(cte_v, cte_v.c.id==Users.id)\
                .join(cte_g, cte_g.c.id==Users.id)\
                .join(cte_p, cte_p.c.id==Users.id).order_by(Users.id),
        page=page,
        per_page=20
    )


def get_full_gp(
        table_m: Type[SQLAlchemy],
        table_s: Type[SQLAlchemy],
        table_t: Type[SQLAlchemy],
        search: str='',
        page: int=1,
        ) -> Query:
    """
    Get group id, playlist name, user count and video count
    """
    gu = (
        db.select(
            table_s.link_id.distinct().label('glink_id'),
            db.func.count(table_s.link_id).over(partition_by=table_s.link_id).label('cl')
            ).cte('gu')
        )
    gv = (
        db.select(
            table_t.link_id.distinct().label('vlink_id'),
            db.func.count(table_t.link_id).over(partition_by=table_t.link_id).label('vl')
            ).cte('gv')
        )
    if search:
        return db.paginate_rows(
            db.session.query(
                table_m.id.distinct().label('id'),
                table_m.name,
                db.func.coalesce(gu.c.cl, '0').label('cu'),
                db.func.coalesce(gv.c.vl, '0').label('cv')
            ).join(gu, gu.c.glink_id==table_m.id, isouter=True)\
                .join(gv, gv.c.vlink_id==table_m.id, isouter=True)\
                .filter(table_m.name.icontains(search))\
                .order_by(table_m.id),
        page=page,
        per_page=20
        )
    return db.paginate_rows(
        db.session.query(
            table_m.id.distinct().label('id'),
            table_m.name,
            db.func.coalesce(gu.c.cl, '0').label('cu'),
            db.func.coalesce(gv.c.vl, '0').label('cv')
            ).join(gu, gu.c.glink_id==table_m.id, isouter=True)\
                .join(gv, gv.c.vlink_id==table_m.id, isouter=True)\
                .order_by(table_m.id),
        page=page,
        per_page=20
        )


def get_gp(
        table_m: Type[SQLAlchemy],
        table_s: Type[SQLAlchemy],
        table_t: Type[SQLAlchemy],
        _id: int
        ) -> Query:
    """
    Getting a group|playlist with the number of users and videos
    """
    cv = (
        db.select(
            table_t.link_id.distinct().label('vlink_id'),
            db.func.count(table_t.video_id).over(partition_by=table_t.link_id).label('vl')
        ).cte('cv')
    )
    cu = (
        db.select(
            table_s.link_id.distinct().label('ulink_id'),
            db.func.count(table_s.user_id).over(partition_by=table_s.link_id).label('cl')
        ).cte('cu')
    )
    full_gp = db.session.query(
        table_m.id,
        table_m.name,
        Users.id.label('uid'),
        Users.name.label('uname'),
        db.func.coalesce(cv.c.vl, '0').label('cv'),
        db.func.coalesce(cu.c.cl, '0').label('cu')
        ).select_from(table_m)\
        .join(table_s, table_s.link_id==table_m.id, isouter=True)\
        .join(Users, Users.id==table_s.user_id, isouter=True)\
        .join(cv, cv.c.vlink_id==table_m.id, isouter=True)\
        .join(cu, cu.c.ulink_id==table_m.id, isouter=True)\
        .filter(table_m.id==_id).order_by(Users.id).all()
    short_gp = db.session.query(table_m.id, table_m.name).filter(table_m.id==_id).one()
    return full_gp if full_gp else short_gp


def get_gp_video(
        table_m: Type[SQLAlchemy],
        table_s: Type[SQLAlchemy],
        _id: int,
        search: str='',
        page: int=1
        ) -> Query:
    """
    Receive videos of participating groups/playlists
    """
    if search:
        return db.paginate(
        db.session.query(Videos).select_from(table_m)\
            .join(table_s, table_s.link_id==table_m.id)\
            .join(Videos, Videos.id==table_s.video_id)\
            .filter(table_m.id==_id)\
            .filter(Videos.name.icontains(search)),
        page=page,
        per_page=20
        )
    return db.paginate(
        db.session.query(Videos).select_from(table_m)\
            .join(table_s, table_s.link_id==table_m.id)\
            .join(Videos, Videos.id==table_s.video_id)\
            .filter(table_m.id==_id),
        page=page,
        per_page=20
        )


def new_user(name: str, email: str, pwd: str='') -> bool:
    """
    Create new user
    """
    if not __check(Users, name):
        if pwd:
            db.session.add(
                Users(name=name, email=email, passwd=Users.gen_password(passwd=pwd))
                )
        else:
            db.session.add(Users(name=name, email=email))
        db.session.commit()
        LOGER.info(f'{new_user.__name__}(): user "{name}" with email "{email}" create.')
        db.session.add_all([
            GroupsUser(user_id=__get_id(Users, name), link_id=1),
            PlaylistsUser(user_id=__get_id(Users, name), link_id=1)
            ])
        db.session.commit()
        LOGER.info(f'{new_user.__name__}(): user "{name}". New access: group "default", playlist "default".')
        return True
    LOGER.error(f'{new_user.__name__}(): user "{name}" alredy exists.')
    return False


def __get_id(table: Type[SQLAlchemy], name: str) -> int:
    """
    Return row from table
    """
    return db.session.query(table.id).filter(table.name==name).first()[0]


def new_gp(table: Type[SQLAlchemy], name: str) -> bool:
    """
    Add group|playlist
    """
    if not __check(table, name):
        db.session.add(table(name=name))
        db.session.commit()
        LOGER.info(f'{new_gp.__name__}(): group|playlist "{name}" add.')
        return True
    LOGER.error(f'{new_gp.__name__}(): group|playlist "{name}" alredy exists.')
    return False


def set_user_state(user_id: int, state: bool) -> bool | None:
    """
    Ban|Unban user
    """
    user = get_short_user(user_id)
    if user:
        user.blocked = state
        db.session.commit()
        LOGER.info(f'{set_user_state.__name__}(): user "{user.name}" {"blocked" if state else "unblocked"}.')
        return True


def set_access_user(flag: str, table: str, user_id: int, _id: int) -> None:
    """
    Setting|Deleting user accesses
    """
    def duplicate_check() -> bool:
        """
        True if there are duplicates
        False if there are no duplicates
        """
        for row in rows:
            if _id == row.link_id:
                return True
        return False
    
    obj = getattr(modules[__name__], table)
    rows = db.session.query(obj).filter(obj.user_id==user_id).filter(obj.link_id!=1).all()
    if flag == 'on':
        if not duplicate_check():
            db.session.add(obj(user_id=user_id, link_id=_id))
            LOGER.info(f'{set_access_user.__name__}(): user ID "{user_id}" enable new access. New access "{obj.__tablename__}": "{_id}".')
    else:
        for row in rows:
            if _id == row.link_id:
                db.session.delete(row)
                LOGER.info(f'{set_access_user.__name__}(): user ID "{row.user_id}" removed access. Removed access "{obj.__tablename__}": "{row.link_id}".')
    db.session.commit()


def save_frame(name: str, frame: str) -> bool:
    """
    Save frame into database
    """
    v = db.session.query(Videos).get(__get_id(Videos, name))
    if v:
        v.frame = frame
        db.session.add(v)
        db.session.commit()
        LOGER.info(f'{save_frame.__name__}(): video "{v.name}" with link "{v.link.split(".")[0]}" update. New frame "{frame}".')
        return True
    LOGER.info(f'{save_frame.__name__}(): not found video "{v.name}" to update frame')
    return False


def save_video(name: str, link: str, user_id: int=1) -> bool:
    """
    Save video into database
    """
    if not __check(Videos, name):
        db.session.add(Videos(name=name, frame='', link=link))
        db.session.commit()
        LOGER.info(f'{save_video.__name__}(): video "{name}" add with link "{link.split(".")[0]}".')
        db.session.add(VideosUser(user_id=user_id, link_id=__get_id(Videos, name)))
        db.session.commit()
        LOGER.info(f'{save_video.__name__}(): video "{name}" with link "{link.split(".")[0]}" attached to user ID "{user_id}".')
        return True
    LOGER.error(f'{save_video.__name__}(): video "{name}" not added')
    return False


def get_video(link: str):
    """
    Get video data for reviewing/redacting
    """
    return db.session.query(
        Videos.id,
        Videos.name,
        Videos.date,
        Videos.link,
        Videos.expiry_share,
        Users.id.label('uid'),
        Users.name.label('owner')
        ).select_from(Videos)\
            .join(VideosUser, VideosUser.link_id==Videos.id)\
            .join(Users, Users.id==VideosUser.user_id)\
            .filter(Videos.link==link).first()


def get_video_user(user_id: int, search: str='', page: int=1) -> Query:
    """
    Get user video
    """
    if search:
        return db.paginate(
            db.select(Videos).select_from(Videos)\
                .join(VideosUser, VideosUser.link_id==Videos.id)\
                .join(Users, Users.id==VideosUser.user_id)\
                .filter(Users.id==user_id)\
                .filter(Videos.name.icontains(search)),
            page=page,
            per_page=20
        )
    return db.paginate(
        db.select(Videos).select_from(Videos)\
            .join(VideosUser, VideosUser.link_id==Videos.id)\
            .join(Users, Users.id==VideosUser.user_id)\
            .filter(Users.id==user_id),
        page=page,
        per_page=20
    )


def set_video_name(_id: int, video_name: str) -> bool:
    """
    Update video name
    """
    video = db.session.query(Videos).filter_by(link=_id).first()
    if video:
        old_video_name = video.name
        video.name = secure_filename(video_name)
        db.session.add(video)
        db.session.commit()
        LOGER.info(f'{set_video_name.__name__}(): video "{old_video_name}" update with link "{_id.split(".")[0]}". New name: "{video.name}".')
        return old_video_name
    LOGER.error(f'{set_video_name.__name__}(): video with link "{_id.split(".")[0]}" no new name has been set.')
    return False


def get_video_gp(table_m: Type[SQLAlchemy], table_s: Type[SQLAlchemy], link: str) -> list:
    """
    Getting groups\playlists for video
    """
    return db.session.query(
        table_m.id,
        table_m.name
    ).select_from(Videos)\
    .join(table_s, table_s.video_id==Videos.id, isouter=True)\
    .join(table_m, table_m.id==table_s.link_id, isouter=True)\
    .filter(Videos.link==link).all()


def set_access_video(flag: bool, table: str, link: int, _id: int) -> bool:
    """
    Installing|Removing video access
    """
    def duplicate_check() -> bool:
        """
        True if there are duplicates
        False if there are no duplicates
        """
        for row in rows:
            if _id == row.link_id:
                return True
        return False
    
    obj = getattr(modules[__name__], table)
    video = get_video(link)
    rows = db.session.query(obj).filter(obj.video_id==video.id).all()
    if flag:    # True
        if not duplicate_check():
            new_access = obj(video_id=video.id, link_id=_id)
            db.session.add(new_access)
            LOGER.info(f'{set_access_video.__name__}(): video "{video.name}" add new access. New access group|playlist: "{obj.__tablename__.split("_")[0]}_id={new_access.link_id}".')
    else:
        for row in rows:
            if _id == row.link_id:
                db.session.delete(row)
                LOGER.info(f'{set_access_video.__name__}(): video "{video.name}" removed access. Removed access group|playlist: "{row.__tablename__.split("_")[0]}_id={row.link_id}".')
    db.session.commit()
    return True


def share_video(link: str, state: bool) -> bool:
    """
    Adding a property to access video without authorization
    """
    video = db.session.query(Videos).filter(Videos.link==link).first()
    if not video:
        LOGER.info(f'{share_video.__name__}(): video ID "{link}" not found.')
        return False
    if state:
        video.expiry_share = datetime.datetime.now() + datetime.timedelta(days=int(environ['VHUB_SHARED_VIDEO_TIME']))
        LOGER.info(f'{share_video.__name__}(): video "{video.name}" with link "{video.link.split(".")[0]}" sharring.')
    else:
        video.expiry_share = None
        LOGER.info(f'{share_video.__name__}(): video "{video.name}" with link "{video.link.split(".")[0]}" stop sharring.')
    db.session.add(video)
    db.session.commit()
    return True


def set_user_pwd(user_id: int, user_name: str, pwd: str, user_email: str='') -> bool:
    """
    Set user password
    """
    user = get_short_user(user_id)
    if user and len(pwd) > 6:
        user.passwd=Users.gen_password(passwd=pwd)
        db.session.commit()
        if not user_email:
            LOGER.info(f'{set_user_pwd.__name__}(): manual set password to user "{user.name}".')
            return True
        LOGER.info(f'{set_user_pwd.__name__}(): reset password to user "{user.name}" and send email "{user.email}".')
        return True
    LOGER.error(f'{set_user_pwd.__name__}(): user "{user_name}" not found or length password < 6.')
    return False


def set_user_admin(user_id: int, state: bool) -> bool:
    """
    Set|Unset admin for user
    """
    user = get_short_user(user_id)
    if user:
        user.admin = state
        db.session.commit()
        LOGER.info(f'{set_user_admin.__name__}(): {"set" if state else "unset"} role admin to user "{user.name}".')
        return True
    LOGER.error(f'{set_user_admin.__name__}(): user ID "{user_id}" not found.')
    return False


def get_shared_video(search: str='', page: int=1) -> Query:
    """
    Receive all videos available to unauthorized users
    """
    if search:
        return db.paginate(
            db.session.query(Videos).filter(Videos.expiry_share!=None)\
                .filter(Videos.expiry_share > datetime.datetime.now())\
                .filter(Videos.name.icontains(search)),
            page=page,
            per_page=20
        )
    return db.paginate(
            db.session.query(Videos).filter(Videos.expiry_share!=None)\
                .filter(Videos.expiry_share > datetime.datetime.now()),
            page=page,
            per_page=20
        )


def get_all_video(search: str='', page: int=1) -> Query:
    """
    Get all video
    """
    if search:
        return db.paginate_rows(
        db.session.query(
            Videos.id,
            Videos.name,
            Videos.date,
            Videos.link,
            db.func.coalesce(Groups.name, '-').label('gname'),
            db.func.coalesce(Playlists.name, '-').label('pname'),
            Users.name.label('uname')
        ).select_from(Videos)\
            .join(VideosUser, VideosUser.link_id==Videos.id)\
            .join(Users, Users.id==VideosUser.user_id)\
            .join(GroupsVideo, GroupsVideo.video_id==Videos.id, isouter=True)\
            .join(Groups, Groups.id==GroupsVideo.link_id, isouter=True)\
            .join(PlaylistsVideo, PlaylistsVideo.video_id==Videos.id, isouter=True)\
            .join(Playlists, Playlists.id==PlaylistsVideo.link_id, isouter=True).order_by(Users.id)\
            .filter(
                Users.name.icontains(search) | Videos.name.icontains(search) | Groups.name.icontains(search) | Playlists.name.icontains(search)
                ),
        page=page,
        per_page=20
    )
    return db.paginate_rows(
        db.session.query(
            Videos.id,
            Videos.name,
            Videos.date,
            Videos.link,
            db.func.coalesce(Groups.name, '-').label('gname'),
            db.func.coalesce(Playlists.name, '-').label('pname'),
            Users.name.label('uname')
        ).select_from(Videos)\
            .join(VideosUser, VideosUser.link_id==Videos.id)\
            .join(Users, Users.id==VideosUser.user_id)\
            .join(GroupsVideo, GroupsVideo.video_id==Videos.id, isouter=True)\
            .join(Groups, Groups.id==GroupsVideo.link_id, isouter=True)\
            .join(PlaylistsVideo, PlaylistsVideo.video_id==Videos.id, isouter=True)\
            .join(Playlists, Playlists.id==PlaylistsVideo.link_id, isouter=True).order_by(Users.id),
        page=page,
        per_page=20
    )


def get_blocked_users(search: str='', page: int=1) -> Query:
    """
    Get all baned users
    """
    if search:
        return db.paginate(
            db.session.query(Users).filter(Users.blocked==True)\
                .filter(Users.name.icontains(search) | Users.email.icontains(search)),
            page=page,
            per_page=20
        )
    return db.paginate(
            db.session.query(Users).filter(Users.blocked==True),
            page=page,
            per_page=20
        )


def get_available_video(user_id: int, search: str='', page: int=1) -> Query:
    """
    Selection of available videos for the user
    """
    if search:
        db.paginate_rows(
            db.session.query(Videos).select_from(Users)\
                .join(GroupsUser, GroupsUser.user_id==Users.id)\
                .join(GroupsVideo, GroupsVideo.link_id==GroupsUser.link_id)\
                .join(Videos, Videos.id==GroupsVideo.video_id)\
                .filter(Users.id==user_id)\
                .filter(Videos.name.icontains(search)).order_by(Videos.id)\
                .union(
                    db.session.query(Videos).filter(Videos.expiry_share>datetime.datetime.now())\
                        .filter(Videos.name.icontains(search)).order_by(Videos.id)
                ),
            page=page,
            per_page=20
        )
    return db.paginate_rows(
        db.session.query(Videos).select_from(Users)\
            .join(GroupsUser, GroupsUser.user_id==Users.id)\
            .join(GroupsVideo, GroupsVideo.link_id==GroupsUser.link_id)\
            .join(Videos, Videos.id==GroupsVideo.video_id)\
            .filter(Users.id==user_id).order_by(Videos.id)\
            .union(
                db.session.query(Videos).filter(Videos.expiry_share>datetime.datetime.now()).order_by(Videos.id)
            ),
        page=page,
        per_page=20
        )


if __name__ == '__main__':
    pass
