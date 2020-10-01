## imports
import os
from skimage import io #library for python to help access pictures
import numpy as np #help do math in python
import matplotlib.pyplot as plt
import random
import imageio
from PIL import Image

from skimage.util.shape import view_as_windows, view_as_blocks
import imutils

import os
import cv2

import glob
import shutil
import re
import pandas as pd
import time


## Clear out old shit

shutil.rmtree('/home/diego/Desktop/Output')
os.mkdir('/home/diego/Desktop/Output')

shutil.rmtree('/home/diego/MPFI/gold_particles/PIX2PIX/datasets/Output_Appended/test')
os.mkdir('/home/diego/MPFI/gold_particles/PIX2PIX/datasets/Output_Appended/test')

shutil.rmtree('/home/diego/MPFI/gold_particles/PIX2PIX/results/Oct30pix2pix/test_latest/images')
os.mkdir('/home/diego/MPFI/gold_particles/PIX2PIX/results/Oct30pix2pix/test_latest/images')

shutil.rmtree('/home/diego/Desktop/Output_ToStich')
os.mkdir('/home/diego/Desktop/Output_ToStich')
## look in INPUT folder, crop photo and save crop to OUTPUT folder
def load_data_make_jpeg(folder):
    list = glob.glob(folder)
    for entry in list:
        img_size=(256,256, 3)
        img_new  = io.imread(entry)
        #img_new = (img_new/256).astype('uint8')
        shape = img_new.shape
        height = shape[0]//256
        height256 = height*256
        width = shape[1]//256
        width256 = width*256
        #CROPPING
        img_new = img_new[:height256,:width256,:3]
        img_new_w = view_as_blocks(img_new, img_size)
        img_new_w = np.uint8(img_new_w)
        imageio.imwrite('/home/diego/Desktop/Output_Final/' + 'CroppedVersion' + '.png', img_new)
        #saving the blocks as images
        r = 0
        for i in range(img_new_w.shape[0]):
            for j in range(img_new_w.shape[1]):
                A = np.zeros((img_size[0], img_size[1], 3))
                A[:,:,:] = img_new_w[i,j,:,:]
                A = np.uint8(A)
                imageio.imwrite('/home/diego/Desktop/Output/'+ str(r) + '.png', A)
                r += 1
    return width, height




## Cut up in order, append white images
width, height = load_data_make_jpeg('/home/diego/Desktop/Input/*.*')

def combine_white(folderA):
    os.chdir(folderA)
    for file in os.listdir(folderA):
        imA = io.imread(file)
        newimage = np.concatenate((imA,white), axis=1)
        imageio.imwrite('/home/diego/MPFI/gold_particles/PIX2PIX/datasets/Output_Appended/test/' + file, newimage)

white = io.imread('/home/diego/Desktop/White/white.png')

combine_white('/home/diego/Desktop/Output/')

## Save that dataset to PIX2PIX/datasets/___

## Run PIX2PIX network
os.system('python3 /home/diego/MPFI/gold_particles/PIX2PIX/test.py --dataroot /home/diego/MPFI/gold_particles/PIX2PIX/datasets/Output_Appended/ --name Oct30pix2pix --model pix2pix --direction AtoB --num_test 1000000 --checkpoints_dir /home/diego/MPFI/gold_particles/PIX2PIX/checkpoints/ --results_dir /home/diego/MPFI/gold_particles/PIX2PIX/results/')
## Take only the Fake_B photos and stich together
list = glob.glob('/home/diego/MPFI/gold_particles/PIX2PIX/results/Oct30pix2pix/test_latest/images/*_fake_B.png')
## Save to OUTPUT folder
for entry in list:
    split_name = entry.split('/')
    dirA = '/home/diego/MPFI/gold_particles/PIX2PIX/results/Oct30pix2pix/test_latest/images/'
    pathA = os.path.join(dirA,split_name[10])
    dirB = '/home/diego/Desktop/Output_ToStich/'
    pathB = os.path.join(dirB,split_name[10])
    shutil.move(pathA, pathB)

## STICH TOGETHER

widthdiv256 = width
heighttimeswidth =  width * height

folderstart = '/home/diego/Desktop/Output_ToStich/'
def stitch_row(n):
    file1 = np.array(Image.open(folderstart  + master[n]))
    file2 = np.array(Image.open(folderstart + master[n+1]))
    full_row = np.concatenate((file1, file2), axis=1)
    for i in range(n + 2, n + widthdiv256):
        file_next = np.array(Image.open(folderstart + master[i]))
        full_row = np.concatenate((full_row, file_next), axis = 1)
    return full_row

files = os.listdir(folderstart)
list = []
for file in files:
    split_name = re.split('\D', file)

    list.append(split_name[0])

list.sort(key = float)
master = []
for file in list:
    name = file + '_fake_B.png'
    master.append(name)


picture = stitch_row(0)
for n in range(widthdiv256,heighttimeswidth,widthdiv256):
    next_row = stitch_row(n)
    picture = np.concatenate((picture,next_row), axis=0)

imageio.imwrite('/home/diego/Desktop/Output_Final/OutputStitched.png', picture)



## Count All Green Dots
img = cv2.imread('/home/diego/Desktop/Output_Final/OutputStitched.png')


lower_green = np.array([0,245,0])
upper_green = np.array([40,255,40])


mask = cv2.inRange(img, lower_green, upper_green)
kernel = np.ones((5,5), np.uint8)
e = cv2.erode(mask, kernel, iterations=1)
d = cv2.dilate(e, kernel, iterations = 1)


cnts = cv2.findContours(d,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
results = pd.DataFrame(columns = ['X','Y'])

for c in cnts:
    M = cv2.moments(c)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        M["m00"] = 1
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

    if (cX != 0 or cY != 0):
        results = results.append({'X':cX , 'Y': cY}, ignore_index=True)
        # cv2.circle(newlabeled, (cX, cY), 2,(255,255,255), -1)
    cv2.putText(d, "center", (cX - 4, cY - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),2)

export_csv = results.to_csv(r'/home/diego/Desktop/Output_Final/Results.csv', index = None, header= True)

shutil.rmtree('/home/diego/Desktop/Input')
os.mkdir('/home/diego/Desktop/Input')
