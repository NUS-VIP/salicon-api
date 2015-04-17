
# coding: utf-8

# In[21]:

#get_ipython().magic(u'reload_ext autoreload')
#get_ipython().magic(u'autoreload 2')
#get_ipython().magic(u'matplotlib inline')
from salicon.salicon import SALICON
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt


# In[12]:

dataDir='.'
dataType='val2014'
annFile='%s/annotations/fixations_%s_examples.json'%(dataDir,dataType)


# In[13]:

# initialize COCO api for instance annotations
salicon=SALICON(annFile)


# In[16]:

# get all images 
imgIds = salicon.getImgIds();
img = salicon.loadImgs(imgIds[np.random.randint(0,len(imgIds))])[0]


# In[18]:

# load and display image
I = io.imread('%s/images/examples/%s'%(dataDir,img['file_name']))
plt.figure()
plt.imshow(I)
plt.show()


# In[30]:

# load and display instance annotations
#plt.imshow(I)
annIds = salicon.getAnnIds(imgIds=img['id'])
anns = salicon.loadAnns(annIds)
salicon.showAnns(anns)
plt.show()


# In[ ]:



