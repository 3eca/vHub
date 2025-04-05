from socket import gethostbyname, gethostname
from os import environ, path
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

import datetime
import utils.logs as logs


LOGER = logs.get_logger(path.basename(__file__))
s3 = Minio(
    endpoint=f"{environ['VHUB_MINIO_SRV']}:{environ['VHUB_MINIO_PORT']}",
    access_key=environ['VHUB_MINIO_USER'],
    secret_key=environ['VHUB_MINIO_PWD'],
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
                bucket_name=environ['VHUB_MINIO_BUCKET'],
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
        bucket_name=environ['VHUB_MINIO_BUCKET'],
        object_name=object_name
        )


def temporary_link_s3(object_name: str) -> str:
    """
    Generate link url for pasting into html
    """
    shared_file = s3.get_presigned_url(
        method='GET',
        bucket_name=environ['VHUB_MINIO_BUCKET'],
        object_name=object_name,
        expires=datetime.timedelta(hours=int(environ['VHUB_SHARED_VIDEO_TIME']))
    )
    return f"/vhub/{shared_file.split('/')[-1]}"


if __name__ == '__main__':
    pass
