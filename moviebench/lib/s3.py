from botocore import session
from moviebench.lib import config
import os.path as op
from uuid import uuid4
from tempfile import NamedTemporaryFile
import wave


def write_stream_to_temp_file(stream):
    temp_file = open('/tmp/%s' % uuid4(), 'w+b')
    while True:
        d = stream.read(1024 * 512)
        if not d:
            break
        temp_file.write(d)
    temp_file.flush()
    return temp_file


def fetch_tracks(name):
    bucket_name = config.get('s3.buckets.tracks')
    sess = session.get_session()
    sess.set_credentials(config.get('s3.access_key'), config.get('s3.access_secret'))
    s3 = sess.create_client('s3')
    key = op.join(name, name + '.flac')
    response = s3.get_object(
        Bucket=bucket_name,
        Key=key,
    )
    stream = response['Body']
    temp_flac = write_stream_to_temp_file(stream)

    key = op.join(name, name + '.srt')
    response = s3.get_object(
        Bucket=bucket_name,
        Key=key,
    )
    stream = response['Body']
    temp_srt = write_stream_to_temp_file(stream)

    return temp_flac, temp_srt


def upload_lines(name, lines, wav_data, wav_params):
    bucket_name = config.get('s3.buckets.data')
    sess = session.get_session()
    sess.set_credentials(config.get('s3.access_key'), config.get('s3.access_secret'))
    s3 = sess.create_client('s3')

    line_data = '\n'.join(lines)
    key = op.join(name, name + '.txt')
    s3.put_object(
        Body=line_data,
        Bucket=bucket_name,
        Key=key,
    )

    for i, data in enumerate(wav_data):
        key = op.join(name, '%s.%05d.wav' % (name, i))

        with NamedTemporaryFile('w+b') as f:
            outwav = wave.open(f.name, 'wb')
            outwav.setparams(wav_params)
            outwav.writeframes(data)
            f.flush()
            f.seek(0)
            s3.put_object(
                Body=f,
                Bucket=bucket_name,
                Key=key,
            )
