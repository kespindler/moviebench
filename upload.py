import boto
import boto.s3
import sys
from boto.s3.key import Key

AWS_ACCESS_KEY_ID = 'AKIAJXFCL5XGHYMRSVGA'
AWS_SECRET_ACCESS_KEY = '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'

bucket_name = AWS_ACCESS_KEY_ID.lower() + 'moviebench-testing'
conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)


bucket = conn.create_bucket(bucket_name, location=boto.s3.connection.Location.DEFAULT)

testfile = "1of2.The.Story.of.Energy.1080p.HDTV.x264.AAC.MVGroup.org.wav"


def upload_files():
    for i in os.listdir(os.getcwd()):
        if i.endswith(".wav") or i.endswith(".srt"):
            print('Uploading %s to Amazon S3 bucket %s') % (i, bucket_name)
            continue
        else:
            continue



def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


k = Key(bucket)
k.key = ''
k.set_contents_from_filename(testfile, cb=percent_cb, num_cb=10)
