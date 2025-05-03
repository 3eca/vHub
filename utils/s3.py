from socket import gethostbyname, gethostname
from typing import BinaryIO
from .database import config, path
from minio import Minio
from minio.error import S3Error

import datetime
import utils.logs as logs


LOGER = logs.get_logger(path.basename(__file__))
s3 = Minio(
    endpoint=f"{config['Minio']['host']}:{config['Minio']['port']}",
    access_key=config['Minio']['user'],
    secret_key=config['Minio']['password'],
    secure=False
)


def upload_s3(
        object_name: str,
        data: BinaryIO,
        length: int,
        content_type: str
        ) -> None:
    """
    Upload file
    """
    s3.put_object(
                bucket_name=config['Minio']['bucket'],
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type
            )
    LOGER.info(f'{upload_s3.__name__}(): file "{object_name}" uploaded.')


def get_file_s3(object_name: str):
    """
    Check exist file
    """
    return s3.get_object(
        bucket_name=config['Minio']['bucket'],
        object_name=object_name
        )


def temporary_link_s3(object_name: str) -> str:
    """
    Generate link url for pasting into html
    """
    shared_file = s3.get_presigned_url(
        method='GET',
        bucket_name=config['Minio']['bucket'],
        object_name=object_name,
        expires=datetime.timedelta(
            hours=config['Video'].getint('time') if config['Video'].getint('time') else 0.1
            )
    )
    return f"/vhub/{shared_file.split('/')[-1]}"


if __name__ == '__main__':
    pass
