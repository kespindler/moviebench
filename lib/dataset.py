
from os.path import join
import wave

DATA_DIR = './data'


def load_set(fpath):
    print 'Loading', fpath
    lines = open(fpath).readlines()
    result = []
    for line in lines:
        code, text = line.split(',', 1)
        wav = wave.open(join(DATA_DIR, 'audio', code + '.wav'))
        data = wav.readframes(wav.getnframes())
        result.append((data, text))
    return result


def load_data():
    train_fpath = join(DATA_DIR, 'train.txt')
    test_fpath = join(DATA_DIR, 'test.txt')

    train = load_set(train_fpath)
    test = load_set(test_fpath)

    return train, test
