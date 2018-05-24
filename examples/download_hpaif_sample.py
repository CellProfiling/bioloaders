#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 17 13:04:14 2018

@author: devinsullivan
"""

from bioloaders.dataset import Dataset
from bioloaders.data.hpa import if_images_v2
#from IPython.core.display import display
#import PIL.Image
import getpass
import matplotlib.pyplot as plt

#reload(if_images_v2)
pswd = getpass.getpass('Password:')
dataset = if_images_v2.hpaif('/Users/devinsullivan/bioloaders/',download=True,
                             buffer_images=False,username='devin',
                             password=pswd,acc_list=['672_E2_1_*'],
                             dest='./data/672')

print('number of data: '+str(len(dataset)))

for i in range(4):
    datum = dataset[i]
    print(datum['label'])
    #display(PIL.Image.fromarray(datum['image']))
    plt.imshow(datum['image'])
    plt.show()
    input('continue?')