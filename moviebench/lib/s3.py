from botocore import session
from moviebench.lib import config
import os.path as op


def fetch_tracks(name):
    bucket_name = config.get('s3.buckets.tracks')
    sess = session.get_session()
    s3 = sess.create_client('s3')
    key = op.join(name, name + '.flac')
    response1 = s3.get_object(
        Bucket=bucket_name,
        Key=key,
    )

    key = op.join(name, name + '.srt')
    response2 = s3.get_object(
        Bucket=bucket_name,
        Key=key,
    )

    return response1, response2
