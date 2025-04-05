from os import environ, path

import argparse
from minio import Minio
from minio.error import S3Error
import pymysql
import logs


LOGER = logs.get_logger(path.basename(__file__))
parser = argparse.ArgumentParser(
    description='Video deletion script',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='''Examples.\n
    \tSingle video: python3 utils/remove_video.py --id 2ec9932-6a9e-476d-8208-017dbf0185a4.mp4 --type single\n
    \tGroups|Playlist|User video: python3 utils/remove_video.py --file videos.txt\n
    \t\tor python3 utils/remove_video.py --type <group|playlist|user> --name <group_name|playlist_name|user_name>.'''
)


class RMVideo():
    """
    Сlass for deleting videos.
    """
    def __init__(
            self, _id: str | None,
            file: str | None,
            type: str | None,
            type_name: str | None
            ):
        self._id = _id
        self.file = file
        self.type = type
        self.type_name = type_name
        self.connect = self.__connect_to_db()
        self.db_cursor = self.__get_db_cursor()
        self.s3 = self.__connect_to_s3()
        
        if self.file:
            with open(self.file, 'r', encoding='utf-8') as f:
                self.data_file = f.readlines()

        if self.type == 'single':
            self.__rm_single_video()
        elif self.type and self.type != 'single':
            self.__rm_gpu_video()
        else:
            self.__rm_file_video()

    def __connect_to_db(self) -> pymysql.Connect:
        return pymysql.connect(
            host=environ['VHUB_MYSQL_SRV'],
            port=int(environ['VHUB_MYSQL_PORT']),
            user=environ['VHUB_MYSQL_USER'],
            passwd=environ['VHUB_MYSQL_PWD'],
            database=environ['VHUB_MYSQL_DB'],
            autocommit=True
        )

    def __get_db_cursor(self) -> pymysql.Connect.cursor:
        return self.connect.cursor()

    def __connect_to_s3(self) -> Minio:
        return Minio(
            endpoint=f"{environ['VHUB_MINIO_SRV']}:{environ['VHUB_MINIO_PORT']}",
            access_key=environ['VHUB_MINIO_USER'],
            secret_key=environ['VHUB_MINIO_PWD'],
            secure=False
        )

    def __rm_single_video(self) -> None:
        """
        Delete video by the passed --id key.
        """
        self.db_cursor.execute(
            '''
            SELECT v.name
                ,v.frame
                ,v.link
            FROM videos v 
            WHERE v.link=%s
            ''', (self._id,)
            )
        vname, vframe, vlink = self.db_cursor.fetchone()
        self.db_cursor.execute(
            '''
            DELETE FROM videos v
            WHERE v.link=%s
            ''', (self._id,)
        )
        for s3_file in (vframe, vlink):
            self.s3.remove_object(environ['VHUB_MINIO_BUCKET'], s3_file)
            self.s3.remove_object(environ['VHUB_MINIO_BUCKET'], s3_file)
        LOGER.info(
            f'{self.__rm_single_video.__name__}(): Video ID "{self._id}" as "{vname}" has been removed by administrator.'
            )

    def __rm_file_video(self) -> None:
        """
        Delete video from file.
        """
        for video in self.data_file:
            self._id = video.rstrip()
            self.__rm_single_video()
        LOGER.info(
            f'{self.__rm_file_video.__name__}(): Videos from {self.file} file were removed by administrator for ID: {self.data_file}.'
            )

    def __rm_gpu_video(self) -> None:
        """
        Delete all video any user|group|playlist
        """
        if self.type == 'group':
            self.db_cursor.execute(
            '''
            SELECT v.name
                ,v.frame
                ,v.link
            FROM videos v
            JOIN groups_video gv ON v.id=gv.video_id
            JOIN `groups` g ON gv.link_id=g.id
            WHERE g.name=%s
            ''', (self.type_name,)
            )
            rows = self.db_cursor.fetchall()
            id_rows = [row[-1] for row in rows]
            for row in rows:
                self._id = row[-1]
                self.__rm_single_video()
            LOGER.info(
                f'{self.__rm_gpu_video.__name__}(): All video in group "{self.type_name}" has been removed by administrator. ID: {id_rows}'
                )
        elif self.type == 'playlist':
            self.db_cursor.execute(
            '''
            SELECT v.name
                ,v.frame
                ,v.link
            FROM videos v
            JOIN playlists_video pv ON v.id=pv.video_id
            JOIN `playlists` p ON pv.link_id=p.id
            WHERE p.name=%s
            ''', (self.type_name,)
            )
            rows = self.db_cursor.fetchall()
            id_rows = [row[-1] for row in rows]
            for row in rows:
                self._id = row[-1]
                self.__rm_single_video()
            LOGER.info(
                f'{self.__rm_gpu_video.__name__}(): All video in playlist "{self.type_name}" has been removed by administrator. ID: {id_rows}'
                )
        elif self.type == 'user':
            self.db_cursor.execute(
            '''
            SELECT v.name
                ,v.frame
                ,v.link
            FROM videos v
            JOIN videos_user vu ON v.id=vu.link_id
            JOIN users u ON vu.user_id=u.id
            WHERE u.name=%s
            ''', (self.type_name,)
            )
            rows = self.db_cursor.fetchall()
            id_rows = [row[-1] for row in rows]
            for row in rows:
                self._id = row[-1]
                self.__rm_single_video()
            LOGER.info(
                f'{self.__rm_gpu_video.__name__}(): All video user "{self.type_name}" has been removed by administrator. ID: {id_rows}'
                )


parser.add_argument(
    '-id', '--id', type=str,
    help='Video id from browser address bar.\n'
    'Like http://192.168.0.2/video/92ec9932-6a9e-476d-8208-017dbf0185a4.mp4\n'
    'where 92ec9932-6a9e-476d-8208-017dbf0185a4.mp4 video id.',
    required=False
)
parser.add_argument(
    '-f', '--file', type=str,
    help="Path to the file in the container. Which lists the video id's, one on each line",
    required=False
)
parser.add_argument(
    '-t', '--type', type=str,
    help="To delete a single video, specify single.\n",
    required=False
)
parser.add_argument(
    '-tn', '--type-name', type=str,
    help="To delete all video in a group or playlist, specify the name groups or playlists.\n"
    "To delete all user's video, specify the user name",
    required=False
)


if __name__ == '__main__':
    args = parser.parse_args()
    rm_video = RMVideo(args.id, args.file, args.type, args.type_name)
