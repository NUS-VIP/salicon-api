__author__ = 'shane-huang'
__version__ = '1.0'
# Interface for accessing the SALICON dataset - saliency annotations for Microsoft COCO dataset.

import copy
import json
from pycocotools.coco import COCO
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import datetime
import numpy as np
from scipy import ndimage
import base64
import cStringIO
import skimage
import skimage.io as io

class SALICON (COCO):
    def __init__(self, annotation_file=None):
        """
        Constructor of SALICON helper class for reading and visualizing annotations.
        :param annotation_file (str): location of annotation file
        :return:
        """
        COCO.__init__(self,annotation_file=annotation_file)


    def createIndex(self):
        """
        Didn't change the original method, just call super
        """
        return COCO.createIndex(self)

    def info(self):
        """
        Didn't change the original method, just call super
        """
        return COCO.info(self)

    def getAnnIds(self, imgIds=[]):
        return self.getAnnIds(imgIds)

    def getAnnIds(self, imgIds=[], catIds=[], areaRng=[], iscrowd=None):
        """
        Get ann ids that satisfy given filter conditions. default skips that filter
        :param imgIds  (int array)     : get anns for given imgs
               catIds  (int array)     : get anns for given cats (must be empty)
               areaRng (float array)   : get anns for given area range (e.g. [0 inf]) (must be empty)
               iscrowd (boolean)       : get anns for given crowd label (False or True)
        :return: ids (int array)       : integer array of ann ids
        """
        imgIds = imgIds if type(imgIds) == list else [imgIds]
        catIds = catIds if type(catIds) == list else [catIds]

        if len(catIds) != 0 or len(areaRng) != 0:
            print "Error: does not support category or area range filtering in saliency annoations!"
            return []

        if len(imgIds) == 0:
            anns = self.dataset['annotations']
        else:
            anns = sum([self.imgToAnns[imgId] for imgId in imgIds if imgId in self.imgToAnns],[])

        if self.dataset['type'] == 'fixations' or self.dataset['type'] == 'saliency_map':
            ids = [ann['id'] for ann in anns]
        else:
            print "Unknown dataset type"
            ids = []
        return ids

    def getImgIds(self, imgIds=[], catIds=[]):
        """
        Didn't change the original method, just call supe
        """
        #not support category filtering
        if len(catIds) !=0 :
            return []
        return COCO.getImgIds(self,imgIds,catIds)

    def loadAnns(self, ids=[]):
        """
        Didn't change the default behavior, just call super
        """
        return COCO.loadAnns(self,ids)

    def loadImgs(self, ids=[]):
        """
        Didn't change the original function, just call super
        """
        return COCO.loadImgs(self,ids)

    def showAnns(self, anns):
        """
        TODO: Display the specified annotations.
        :param anns (array of object): annotations to display
        :return: None
        """
        if len(anns) == 0:
            return 0

        assert(len(set([ann['image_id'] for ann in anns])) == 1)
        image_id = list(set([ann['image_id'] for ann in anns]))[0]
        imginfo = self.imgs[image_id]
        #if datatype is fixations, build saliency map
        sal_map = np.zeros((imginfo['height'],imginfo['width']))
        if self.dataset['type'] == 'fixations':
            #TODO# depend on self.buildSaliencyMap
            sal_map = self.buildFixMap(anns)
        elif self.dataset['type'] == 'saliency_map':
            assert(len(anns) == 1)
            sal_map = self.decodeImage(anns[0]['saliency_map'])
        # TODO # show saliency map now
        # to change to heatmap
        plt.imshow(sal_map, cmap = cm.Greys_r,vmin=0,vmax=1)

    def buildFixMap(self,anns,doBlur=True,sigma=19):
        """
        TODO: Build a fixation map based on fixation annotations
        refer to format spec to see the format of fixations
        """
        if len(anns) == 0:
            return 0

        #build saliency map based on annotations
        #check whether all annotations are for the same image
        assert(len(set([ann['image_id'] for ann in anns])) == 1)
        image_id = list(set([ann['image_id'] for ann in anns]))[0]

        fixations = [ann['fixations'] for ann in anns] # fixations from several workers
        merged_fixations = [item for sublist in fixations for item in sublist] #merge
        #create saliency map
        imginfo = self.imgs[image_id]
        sal_map = np.zeros((imginfo['height'],imginfo['width']))

        for y,x in merged_fixations:
            sal_map[y-1][x-1] = 1
        if doBlur:
            sal_map = ndimage.filters.gaussian_filter(sal_map, sigma)
            sal_map -= np.min(sal_map)
            sal_map /= np.max(sal_map)
        return sal_map

    def loadRes(self, resFile):
        """
        Load result file and return a result api object.
        :param   resFile (str)     : file name of result file
        :return: res (obj)         : result api object
        result annotation has different format from the ground truth annotation (fixations vs. saliency map)
        """
        res = SALICON()
        res.dataset['images'] = [img for img in self.dataset['images']]
        res.dataset['info'] = copy.deepcopy(self.dataset['info'])
        res.dataset['type'] = 'saliency_map'
        res.dataset['licenses'] = copy.deepcopy(self.dataset['licenses'])

        print 'Loading and preparing results...     '
        time_t = datetime.datetime.utcnow()
        anns    = json.load(open(resFile))
        assert type(anns) == list, 'results in not an array of objects'
        annsImgIds = [ann['image_id'] for ann in anns]
        assert set(annsImgIds) == (set(annsImgIds) & set(self.getImgIds())), \
               'Results do not correspond to current coco set'
        if 'saliency_map' in anns[0]:
            #only keep the intersection of result and original image set
            imgIds = set([img['id'] for img in res.dataset['images']]) & set([ann['image_id'] for ann in anns])
            res.dataset['images'] = [img for img in res.dataset['images'] if img['id'] in imgIds]
            for id, ann in enumerate(anns):
                ann['id'] = id
            ### TODO ###
            # make sure whether needs to copy other things into Result object

        print 'DONE (t=%0.2fs)'%((datetime.datetime.utcnow() - time_t).total_seconds())

        res.dataset['annotations'] = anns
        res.createIndex()
        return res

    @staticmethod
    def encodeImage(imageFile):
        """
        Encode image file into string using base64.
        :param   imageFile : str - (path of png or jpg file)
        :return: string     : encoded image as string
        """
        encoded_string = ''
        if not os.path.exist(imageFile):
            print "File does not exist",imageFile
        with open(imgFile, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        return encoded_string

    @staticmethod
    def decodeImage(imageStr):
        """
        Decode image string back into image data
        :param imageStr: image as encoded base64 string
        :return img : image as ndarray
        """
        salmapData = base64.b64decode(imageStr)
        salmapFilelike = cStringIO.StringIO(salmapData)
        img = skimage.img_as_float(io.imread(salmapFilelike))
        return img

if __name__ == "__main__":
    s = SALICON('../annotations/fixations_val2014_examples.json')
    s.info()
    print s.getImgIds()
    print s.imgs[102625]
    #print s.getAnnIds(imigIds=102625)
