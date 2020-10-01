import os as os# helps navigate filesystem
from skimage import io #library for python to help access pictures
import numpy as np #help do math in python
import matplotlib.pyplot as plt
import random
import imageio
from PIL import Image
import glob
import sys

from skimage.util.shape import view_as_windows, view_as_blocks
from array import array
import argparse
import os
from math import log10
from os.path import join

import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
from torch.utils.data import DataLoader
import torch.backends.cudnn as cudnn

import torch
import torch.nn as nn
from torch.nn import init
import functools
from torch.optim import lr_scheduler
import argparse
import os
import torch
import torchvision.transforms as transforms

Image.MAX_IMAGE_PIXELS = None

#curetesy of William Hahn
def load_data_make_jpeg(folder):
    entrynumber = 0
    list = glob.glob(folder)
    for entry in list:
        entrynumber += 1
        img_size=(256,256, 3)
        img_new  = io.imread(entry)

        shape = img_new.shape
        height = shape[0]//256
        height = height*256
        width = shape[1]//256
        width = width*256

        img_new = img_new[:height,:width,:3]
        img_new_w = view_as_blocks(img_new, img_size)
        img_new_w = np.uint8(img_new_w)

        r = 0
        for i in range(img_new_w.shape[0]):
            for j in range(img_new_w.shape[1]):
                A = np.zeros((img_size[0], img_size[1], 3))
                A[:,:,:] = img_new_w[i,j,:,:]
                A = np.uint8(A)
                imageio.imwrite('/home/diego/Desktop/Output/'+ str(entrynumber) + '-' + str(r) + '.png', A)
                r += 1



load_data_make_jpeg('/home/diego/Desktop/Input/*.tif')

def combine_white(folderA):
    os.chdir(folderA)
    for file in os.listdir(folderA):
        imA = io.imread(file)
        newimage = np.concatenate((imA,white), axis=1)
        imageio.imwrite('/home/diego/MPFI/gold_particles/PIX2PIX/datasets/Output_Appended/test' + file, newimage)

white = io.imread('/home/diego/Desktop/White/white.png')

combine_white('/home/diego/Desktop/Output')

sys.argv = ['--dataroot ./datasets/GreyAppended', '--direction AtoB', '--model pix2pix', '--name finalpix2pix' ]
exec(open(test.py).read());
