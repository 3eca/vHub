import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.query import Query


db = SQLAlchemy()


class Groups(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('GroupsUser', backref='groups', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<Name %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.name
                    )


class GroupsUser(db.Model):
    __tablename__ = 'groups_user'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    link_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<UserID %r>, ' \
            '<GroupID %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.user_id,
                    self.link_id
                    )


class GroupsVideo(db.Model):
    __tablename__ = 'groups_video'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id', ondelete='CASCADE'))
    link_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<VideoID %r>, ' \
            '<GroupID %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.video_id,
                    self.link_id
                    )


class Playlists(db.Model):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('PlaylistsUser', backref='playlists', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<Name %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.name
                    )
   

class PlaylistsUser(db.Model):
    __tablename__ = 'playlists_user'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    link_id = db.Column(db.Integer, db.ForeignKey('playlists.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<UserID %r>, ' \
            '<PlaylistID %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.user_id,
                    self.link_id
                    )


class PlaylistsVideo(db.Model):
    __tablename__ = 'playlists_video'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id', ondelete='CASCADE'))
    link_id = db.Column(db.Integer, db.ForeignKey('playlists.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<VideoID %r>, ' \
            '<GroupID %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.video_id,
                    self.link_id
                    )


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    blocked = db.Column(db.Boolean, default=False, nullable=False)
    passwd = db.Column(db.String(255))
    admin = db.Column(db.Boolean, default=False, nullable=False)
    groups = db.relationship('GroupsUser', backref='users', cascade='all, delete-orphan')
    playlists = db.relationship('PlaylistsUser', backref='users', cascade='all, delete-orphan')
    videos = db.relationship('VideosUser', backref='users', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<Name %r>, ' \
            '<Email %r>, ' \
            '<Date %r>, ' \
            '<Blocked %r> ' \
            '<Admin %r> ' \
            '<Groups %r> ' 
                ) % (
                    self.__tablename__,
                    self.id,
                    self.name,
                    self.email,
                    self.date,
                    self.blocked,
                    self.admin,
                    self.groups
                    )

    @property
    def get_passwd(self) -> str:
        return self.passwd

    @staticmethod
    def gen_password(passwd: str):
        return generate_password_hash(passwd)

    def check_password(self, passwd: str) -> bool:
        return check_password_hash(self.get_passwd, passwd)


class Videos(db.Model):
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    frame = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False, unique=True)
    expiry_share = db.Column(db.DateTime, nullable=True)
    owner = db.relationship('VideosUser', backref='videos', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<Name %r>, ' \
            '<Date %r>, ' \
            '<Link %r>, ' \
            '<Expiry Share %r> '
                ) % (
                    self.__tablename__,
                    self.id,
                    self.name,
                    self.date,
                    self.link,
                    self.expiry_share
                    )


class VideosUser(db.Model):
    __tablename__ = 'videos_user'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    link_id = db.Column(db.Integer, db.ForeignKey('videos.id', ondelete='CASCADE'))

    def __repr__(self) -> str:
        return (
            '<Table %r>, ' \
            '<ID %r>, ' \
            '<UserID %r>, ' \
            '<VideoID %r>'
                ) % (
                    self.__tablename__,
                    self.id,
                    self.user_id,
                    self.link_id
                    )


if __name__ == '__main__':
    pass
