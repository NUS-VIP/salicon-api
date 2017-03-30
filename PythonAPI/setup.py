from distutils.core import setup
import os
import urllib2

setup(name='salicon',
      packages=['salicon'],
      package_dir={'salicon': 'salicon'},
      version='1.0',
      )


# download data for Microsoft coco dataset
def download(url, dst):
    '''
    command line progress bar tool
    :param url: url link for the file to download
    :param dst: dst file name
    :return:
    '''
    if os.path.exists(dst):
        print 'File downloaded'
        return 1

    u = urllib2.urlopen(url)
    f = open(dst, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s " % (dst, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%] " % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,
    f.close()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).
    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print question + prompt
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print  "Please respond with 'yes' or 'no' (or 'y' or 'n')."


def build_fixmaps(in_ann_wo_fixmap, out_ann_w_fixmap):
    """
    build a full self-contained annoation json file with fixations maps inside.
    :param in_ann_wo_fixmap: the original annotation without fixation maps
    :param out_ann_w_fixmap: the path to the output annotation with fixation maps
    """
    # TODO
    pass


# create directory folder
if not os.path.exists('../images'):
    print 'creating ../images to host images in SALICON (Microsoft COCO) dataset...'
    os.mkdir('../images')
    print 'done'
if not os.path.exists('../annotations'):
    print 'creating ../annotations to host annotations in SALICON dataset'
    os.mkdir('../annotations')
    print 'done'

print "The following steps help you download images and annotations."
print "Given the size of zipped image files, manual download is recommended at http://mscoco.org/download"
# download train images
if query_yes_no("Do you want to download zipped training images [1.5GB] under ./images?", default='no'):
    url = 'https://www.dropbox.com/s/cy96zvud8fdpwde/train.zip?dl=1'
    download(url, '../images/train2015r1.zip')

# download val images
if query_yes_no("Do you want to download zipped validation images [0.8GB] under ./images?", default='no'):
    url = 'https://www.dropbox.com/s/9jzzwsaxnwnbdmg/val.zip?dl=1'
    download(url, '../images/val2015r1.zip')

if query_yes_no("Do you want to download zipped test images [0.8GB] under ./images?", default='no'):
    url = 'https://www.dropbox.com/s/4gzn0hs1tw4ydlu/test.zip?dl=1'
    download(url, '../images/test2015r1.zip')

# download annotations
for split in ['train', 'val']:
    for anno in ['fixations']:
        # download annotations
        if split == 'train' and anno == 'fixations':
            size = '818'
            if query_yes_no("Do you want to download %s split for %s annotations [%sMB] under ./annotations?" % (
                    split, anno, size), default='yes'):
                fname = '../annotations/%s_%s2015r1.json' % (anno, split)
                url = 'https://www.dropbox.com/s/7t2sc4m92hhtzm2/fixations_train2014.json.zip?dl=1'
                download(url, fname)

        elif split == 'val' and anno == 'fixations':
            size = '459'
            if query_yes_no("Do you want to download %s split for %s annotations [%sMB] under ./annotations?" % (
                    split, anno, size), default='yes'):
                fname = '../annotations/%s_%s2015r1.json' % (anno, split)
                url = 'https://www.dropbox.com/s/bgo91bnoqk3m5ja/fixations_val2014.json.zip?dl=1'
                download(url, fname)

    if query_yes_no("Do you want to download %s split for %s annotations [%sMB] under ./annotations?" % (
            split, anno, size), default='yes'):
        fname = '../annotations/%s_%s2015r1.json' % (anno, split)
        url = 'https://dl.dropboxusercontent.com/u/3777195/salicon-dataset/2015r1/%s_%s2014.json' % (anno, split)
        download(url, fname)

    if query_yes_no(
            "The downloaded annotation files has only fixations but no fixation maps. Do you want to build annotation file with fixations maps under ./annotations?",
            default='yes'):
        input_fname = '../annotations/%s_%s2015r1.json' % (anno, split)
        output_fname = './annotations/%s_%s2015r1.json' % ('fixationmaps', split)
        build_fixmaps(input_fname, output_fname)
