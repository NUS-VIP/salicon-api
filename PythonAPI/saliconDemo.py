
# coding: utf-8

# In[1]:

#get_ipython().magic(u'reload_ext autoreload')
#get_ipython().magic(u'autoreload 2')
#get_ipython().magic(u'matplotlib inline')
from salicon.salicon import SALICON
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt


# In[2]:

dataDir='..'
dataType='train2014examples'
annFile='%s/annotations/fixations_%s.json'%(dataDir,dataType)


# In[3]:

# initialize COCO api for instance annotations
salicon=SALICON(annFile)


# In[4]:

# get all images 
imgIds = salicon.getImgIds();
img = salicon.loadImgs(imgIds[np.random.randint(0,len(imgIds))])[0]


# In[6]:

# load and display image
I = io.imread('%s/images/%s/%s'%(dataDir,dataType,img['file_name']))
plt.figure()
plt.imshow(I)
plt.show()


# In[7]:

# load and display instance annotations
#plt.imshow(I)
annIds = salicon.getAnnIds(imgIds=img['id'])
anns = salicon.loadAnns(annIds)
salicon.showAnns(anns)
plt.show()


# In[ ]:



