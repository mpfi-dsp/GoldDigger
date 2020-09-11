## imports
import os
from skimage import io  # library for python to help access pictures
import numpy as np  # help do math in python
import matplotlib.pyplot as plt
import random
import imageio
from PIL import Image
import sys

from skimage.util.shape import view_as_windows, view_as_blocks
import imutils

import os
import cv2

import glob
import shutil
import re
import pandas as pd
import pathlib

import time
import errno, os, stat, shutil


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


model = sys.argv[1]

# gets rid of the constant artifact in the up left corner
if model == '87kGoldDigger':
    Artifact = True
else:
    Artifact = False

## Clear out old stuff

shutil.rmtree('media/Output')
os.mkdir('media/Output')

shutil.rmtree('media/Output_Appended/test')
os.mkdir('media/Output_Appended/test')

shutil.rmtree('media/PIX2PIX/results/{0}/test_latest/images'.format(model))
os.mkdir('media/PIX2PIX/results/{0}/test_latest/images'.format(model))

shutil.rmtree('media/Output_ToStitch')
os.mkdir('media/Output_ToStitch')

shutil.rmtree('media/Output_Final')
os.mkdir('media/Output_Final')

try:
    os.remove('media/GD_Output.zip')
except:
    pass


## look in INPUT folder, crop photo and save crop to OUTPUT folder
def load_data_make_jpeg(folder):
    list = glob.glob(folder)
    print(list)
    for entry in list:

        img_size = (256, 256, 3)
        img_new = io.imread(entry)
        # img_new = (img_new/256).astype('uint8')
        shape = img_new.shape
        height = shape[0] // 256
        height256 = height * 256
        width = shape[1] // 256
        width256 = width * 256

        img_new = img_new[:height256, :width256, :3]
        img_new_w = view_as_blocks(img_new, img_size)
        img_new_w = np.uint8(img_new_w)
        imageio.imwrite('media/Output_Final/' + 'CroppedVersion' + '.png', img_new)
        r = 0
        for i in range(img_new_w.shape[0]):
            for j in range(img_new_w.shape[1]):
                A = np.zeros((img_size[0], img_size[1], 3))
                A[:, :, :] = img_new_w[i, j, :, :]
                # A = np.uint8(A)
                imageio.imwrite('media/Output/' + str(r) + '.png', A)
                r += 1
    return width, height


## Cut up in order, append white images

width, height = load_data_make_jpeg('media/Input/*.*')

print("BEFORE COMBINE_WHITE")


def combine_white(folderA):
    print(os.getcwd())
    os.chdir(folderA)
    for file in os.listdir('.'):
        imA = io.imread(file)
        newimage = np.concatenate((imA, white), axis=1)
        imageio.imwrite('../Output_Appended/test/' + file, newimage)

    os.chdir('../../')
    print(os.getcwd())


white = io.imread('media/White/white.png')

combine_white('media/Output')

## Save that dataset to PIX2PIX/datasets/___


print("BEFORE PIX2PIX")

## Run PIX2PIX network
os.system(
    'python3 media/PIX2PIX/test.py --dataroot media/Output_Appended/ --name {0} --model pix2pix --direction AtoB --num_test 1000000 --checkpoints_dir media/PIX2PIX/checkpoints/ --results_dir media/PIX2PIX/results/'.format(
        model))

print("RAN PIX2PIX")

## Take only the Fake_B photos and stich together
list = glob.glob('media/PIX2PIX/results/{0}/test_latest/images/*_fake_B.png'.format(model))
## Save to OUTPUT folder
for entry in list:
    split_name = entry.split('/')
    print(split_name)
    dirA = 'media/PIX2PIX/results/{0}/test_latest/images/'.format(model)
    pathA = os.path.join(dirA, split_name[-1])
    dirB = 'media/Output_ToStitch/'
    pathB = os.path.join(dirB, split_name[-1])
    shutil.move(pathA, pathB)

## STICH TOGETHER

print("---BEFORE STITCH---")

widthdiv256 = width
heighttimeswidth = width * height

folderstart = 'media/Output_ToStitch/'


def stitch_row(n):
    image1 = imageio.imread(folderstart + master[n])
    if (Artifact):
        image1[0:35, 220:256, :] = 0
    file1 = np.array(image1)

    image2 = imageio.imread(folderstart + master[n + 1])
    if (Artifact):
        image2[0:35, 220:256, :] = 0
    file2 = np.array(image2)

    full_row = np.concatenate((file1, file2), axis=1)
    for i in range(n + 2, n + widthdiv256):
        image3 = imageio.imread(folderstart + master[i])
        if (Artifact):
            image3[0:35, 220:256, :] = 0
        file_next = np.array(image3)
        full_row = np.concatenate((full_row, file_next), axis=1)
    return full_row


files = os.listdir(folderstart)
list = []
for file in files:
    split_name = re.split('\D', file)

    list.append(split_name[0])

list.sort(key=float)
master = []
for file in list:
    name = file + '_fake_B.png'
    master.append(name)

picture = stitch_row(0)
for n in range(widthdiv256, heighttimeswidth, widthdiv256):
    next_row = stitch_row(n)
    picture = np.concatenate((picture, next_row), axis=0)

imageio.imwrite('media/Output_Final/OutputStitched.png', picture)

print("--AFTER STITCH--")

## Count All Green Dots
img = cv2.imread('media/Output_Final/OutputStitched.png')
img_original = cv2.imread('media/Output_Final/CroppedVersion.png')
img_original = np.uint8(img_original)

h, w = img_original.shape[:2]
flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)

lower_green = np.array([0, 245, 0])
upper_green = np.array([40, 255, 40])

mask = cv2.inRange(img, lower_green, upper_green)
kernel = np.ones((5, 5), np.uint8)
e = cv2.erode(mask, kernel, iterations=1)
d = cv2.dilate(e, kernel, iterations=1)

cnts = cv2.findContours(d, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
seedlistx = []
seedlisty = []
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
        if img_original[cY, cX, 0] < 120:
            seedlistx.append(cX)
            seedlisty.append(cY)

listlen = len(seedlistx)
floodflags = 4
floodflags |= cv2.FLOODFILL_MASK_ONLY
floodflags |= (255 << 8)
for i in range(listlen):
    num, im, mask, rect = cv2.floodFill(img_original, flood_mask, (seedlistx[i], seedlisty[i]), 1, (4,) * 3, (4,) * 3,
                                        floodflags)

print(np.mean(img_original))
# cv2.imshow("Image", flood_mask)
# cv2.waitKey(0)

print("THIS IS WHERE IT WOULD SHOW THE IMAGE")

flood_mask = flood_mask[:h, :w]
cnts = cv2.findContours(flood_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

results6 = pd.DataFrame(columns=['X', 'Y'])
results12 = pd.DataFrame(columns=['X', 'Y'])
results18 = pd.DataFrame(columns=['X', 'Y'])

for c in cnts:
    #    compute the center of the contour, then detect the name of the
    # shape using only the contour
    M = cv2.moments(c)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        M["m00"] = 1
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

    if not (cX==0 and cY==0):
        if cv2.contourArea(c) < 75:
            results6 = results6.append({'X': cX, 'Y': cY}, ignore_index=True)
        elif cv2.contourArea(c) >= 75 and cv2.contourArea(c) < 350:
            results12 = results12.append({'X': cX, 'Y': cY}, ignore_index=True)
        elif cv2.contourArea(c) >= 350 and cv2.contourArea(c) < 1500:
            results18 = results18.append({'X': cX, 'Y': cY}, ignore_index=True)

export_csv = results6.to_csv(r'media/Output_Final/Results6nm.csv', index=None,
                             header=True)
export_csv = results12.to_csv(r'media/Output_Final/Results12nm.csv', index=None,
                              header=True)
export_csv = results18.to_csv(r'media/Output_Final/Results18nm.csv', index=None,
                              header=True)

shutil.rmtree('media/Input')
os.mkdir('media/Input')

print("SUCCESS!!")

shutil.make_archive('media/GD_Output', 'zip', 'media/Output_Final')

print('CREATED ZIP FILE')
