from botocore import session
from moviebench.lib import config
import os.path as op


def fetch_tracks(name):
    bucket_name = config.get('s3.buckets.tracks')
    sess = session.get_session()
    s3 = sess.create_client('s3')
    operation = s3.get_operation('GetObject')
    endpoint = s3.get_endpoint('us-east-1')
    key = op.join(name, name + '.flac')
    response, flac_data = operation.call(
        endpoint,
        bucket=bucket_name,
        key=key
    )

    key = op.join(name, name + '.srt')
    response, srt_data = operation.call(
        endpoint,
        bucket=bucket_name,
        key=key
    )

    return flac_data, srt_data
