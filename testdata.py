#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
originally from https://scikit-image.org/docs/dev/api/skimage.color.html#skimage.color.label2rgb

@author: jev
"""



from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb
import numpy as np

class TestData:
    """ some example testdata for the viewer """

    def __init__(self):

        image = data.coins()[50:-50, 50:-50]

        # apply threshold
        thresh = threshold_otsu(image)
        bw = closing(image > thresh, square(3))

        # remove artifacts connected to image border
        cleared = clear_border(bw)

        # set properties
        self.image = image
        self.labels = label(cleared)
        
    @property 
    def overlay(self):
        """ overlay with transparancy """
        
        
        rgb = label2rgb(self.labels, bg_label=0)
        
        alpha = np.ones(self.image.shape)
        alpha[self.labels==0] = 0
            
        return np.dstack((rgb,alpha))


