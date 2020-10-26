# imports
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
import errno
import os
import stat
import shutil
# from sklearn.cluster import Kmeans


def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


def get_artifact_status(model):
    # gets rid of the constant artifact in the up left corner
    if model == '87kGoldDigger':
        artifact = True
    else:
        artifact = False
        return artifact


def clear_out_old_files(model):
    shutil.rmtree('media/Output', ignore_errors=True)
    os.makedirs('media/Output')

    shutil.rmtree('media/Output_Appended', ignore_errors=True)
    os.makedirs('media/Output_Appended')

    shutil.rmtree('media/Output_Appended/test', ignore_errors=True)
    os.makedirs('media/Output_Appended/test')

    shutil.rmtree(
        'media/PIX2PIX/results/{0}/test_latest/images'.format(model), ignore_errors=True)
    os.makedirs('media/PIX2PIX/results/{0}/test_latest/images'.format(model))

    shutil.rmtree('media/Output_ToStitch', ignore_errors=True)
    os.makedirs('media/Output_ToStitch')

    shutil.rmtree('media/Output_Final', ignore_errors=True)
    os.makedirs('media/Output_Final')

    try:
        os.remove('media/GD_Output.zip')
    except:
        pass


# look in INPUT folder, crop photo and save crop to OUTPUT folder
# Cut up in order, append white images

def load_data_make_jpeg(image, mask):
    file_list = pathlib.Path('media/Input', image)
    print(file_list)
    for entry in [file_list]:

        img_size = (256, 256, 3)
        img_new = io.imread(entry)
        # img_new = (img_new/256).astype('uint8')
        shape = img_new.shape
        height = shape[0] // 256
        height256 = height * 256
        width = shape[1] // 256
        width256 = width * 256

        img_new = img_new[:height256, :width256, :3]
        img_mask = None
        if mask is not None:
            mask_path = pathlib.Path('media/Mask', mask)
            img_mask = io.imread(mask_path)
            img_mask = img_mask[:height256, :width256, :3]
        img_new_w = view_as_blocks(img_new, img_size)
        img_new_w = np.uint8(img_new_w)
        imageio.imwrite('media/Output_Final/' +
                        'CroppedVersion' + '.png', img_new)
        r = 0
        for i in range(img_new_w.shape[0]):
            for j in range(img_new_w.shape[1]):
                A = np.zeros((img_size[0], img_size[1], 3))
                A[:, :, :] = img_new_w[i, j, :, :]
                # A = np.uint8(A)
                imageio.imwrite('media/Output/' + str(r) + '.png', A)
                r += 1
    return file_list, width, height, img_mask


def combine_white(white, folderA):
    print(os.getcwd())
    os.chdir(folderA)
    for file in os.listdir('.'):
        imA = io.imread(file)
        newimage = np.concatenate((imA, white), axis=1)
        imageio.imwrite('../Output_Appended/test/' + file, newimage)

    os.chdir('../../')
    print(os.getcwd())


# Save to OUTPUT folder
def save_to_output_folder(file_list, model):
    for entry in file_list:
        split_name = entry.split('/')
        print(split_name)
        dirA = 'media/PIX2PIX/results/{0}/test_latest/images/'.format(model)
        pathA = os.path.join(dirA, split_name[-1])
        dirB = 'media/Output_ToStitch/'
        pathB = os.path.join(dirB, split_name[-1])
        shutil.move(pathA, pathB)

# STICH TOGETHER


def stitch_row(n, master, folderstart, artifact, widthdiv256):
    image1 = imageio.imread(folderstart + master[n])
    if (artifact):
        image1[0:35, 220:256, :] = 0
    file1 = np.array(image1)

    image2 = imageio.imread(folderstart + master[n + 1])
    if (artifact):
        image2[0:35, 220:256, :] = 0
    file2 = np.array(image2)

    full_row = np.concatenate((file1, file2), axis=1)
    for i in range(n + 2, n + widthdiv256):
        image3 = imageio.imread(folderstart + master[i])
        if (artifact):
            image3[0:35, 220:256, :] = 0
        file_next = np.array(image3)
        full_row = np.concatenate((full_row, file_next), axis=1)
    return full_row


def stitch_image(folderstart, widthdiv256, heighttimeswidth, artifact):
    files = os.listdir(folderstart)
    file_list = []
    for file in files:
        split_name = re.split('\D', file)
        file_list.append(split_name[0])

    file_list.sort(key=float)
    master = []
    for file in file_list:
        name = file + '_fake_B.png'
        master.append(name)

    picture = stitch_row(0, master, folderstart, artifact, widthdiv256)
    for n in range(widthdiv256, heighttimeswidth, widthdiv256):
        next_row = stitch_row(n, master, folderstart, artifact, widthdiv256)
        picture = np.concatenate((picture, next_row), axis=0)
    return picture, file_list


def count_green_dots():
    # From Diego:
    # 1. Finds green square and then the center of that (x,y)
    # 2. Then I perform a flood fill on that (x,y) on the original image
    # 3. So it fills out the entire dark particle
    # 4. Then I find the contour of that mask and the xy of that new circle
    # 5. I do this so inconsistencies in the green mask dont affect the area of the gold particle
    # Basically it just uses the green masks to find a seed point to start flood filling. This makes sure that the mask is the exact size of the gold particle
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

    flood_mask = flood_mask[:h, :w]
    cnts = cv2.findContours(
        flood_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts

def check_if_coordinate_is_in_mask(x,y,mask):
    if mask is None:
        return True
    elif mask[x,y] != (255,255,255):
        return True
    else:
        return False


def get_contour_centers_and_group(particle_group_count, cnts, img_mask):
    # group using k means
    # report size distributions
    # show relative size histograms and cutoffs
    results6 = pd.DataFrame(columns=['X', 'Y'])
    results12 = pd.DataFrame(columns=['X', 'Y'])
    results18 = pd.DataFrame(columns=['X', 'Y'])
    all_coordinates = pd.DataFrame(columns=['X','Y','Area'])
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

        if not (cX == 0 and cY == 0):
            all_coordinates = all_coordinates.append({'X': cX, 'Y': cY,'Area':cv2.contourArea(c)}, ignore_index=True)
            if check_if_coordinate_is_in_mask(cX, cY, img_mask):
                if cv2.contourArea(c) < 75:
                    results6 = results6.append(
                        {'X': cX, 'Y': cY}, ignore_index=True)
                elif cv2.contourArea(c) >= 75 and cv2.contourArea(c) < 350:
                    results12 = results12.append(
                        {'X': cX, 'Y': cY}, ignore_index=True)
                elif cv2.contourArea(c) >= 350 and cv2.contourArea(c) < 1500:
                    results18 = results18.append(
                        {'X': cX, 'Y': cY}, ignore_index=True)
            if cv2.contourArea(c) < 75:
                results6 = results6.append(
                    {'X': cX, 'Y': cY}, ignore_index=True)
            elif cv2.contourArea(c) >= 75 and cv2.contourArea(c) < 350:
                results12 = results12.append(
                    {'X': cX, 'Y': cY}, ignore_index=True)
            elif cv2.contourArea(c) >= 350 and cv2.contourArea(c) < 1500:
                results18 = results18.append(
                    {'X': cX, 'Y': cY}, ignore_index=True)

    return all_coordinates, results6, results12, results18


def save_files_to_csv(results6, results12, results18):
    export_csv = results6.to_csv(r'media/Output_Final/Results6nm.csv', index=None,
                                 header=True)
    export_csv = results12.to_csv(r'media/Output_Final/Results12nm.csv', index=None,
                                  header=True)
    export_csv = results18.to_csv(r'media/Output_Final/Results18nm.csv', index=None,
                                  header=True)


def clear_out_input_dirs():
    shutil.rmtree('media/Input')
    os.mkdir('media/Input')


def update_progress(progress_recorder, step, total_steps, message):
    if progress_recorder is not None:
        progress_recorder.set_progress(step, total_steps, message)

def save_preview_figure(coordinates):
    img = cv2.imread('media/Output_Final/OutputStitched.png')
    img2 = img[:,:,::-1]
    plt.figure(1)
    plt.imshow(img2)
    plt.scatter(coordinates.X.values,coordinates.Y.values, facecolors='none',edgecolors='r')
    plt.gca().set_axis_off()
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    preview_file_path = 'media/Output_Final/preview.png'
    if os.path.exists(preview_file_path):
        os.remove(preview_file_path)
    plt.savefig(preview_file_path, bbox_inches = 'tight',
        pad_inches = 0)

def save_histogram(coordinates):
    plt.figure(2)
    plt.hist(coordinates.Area.values, bins=100)
    plt.title('Particle Area Histogram')
    plt.xlabel('Size (px)')
    plt.ylabel('Count')
    hist_path = 'media/Output_Final/preview_histogram.png'
    if os.path.exists(hist_path):
        os.remove(hist_path)
    plt.savefig(hist_path, bbox_inches='tight')


class ProgressBarWrapper:

    def __init__(self, progress_recorder, total_steps):
        self.progress_recorder = progress_recorder
        self.total_steps = total_steps

    def update(self, steps, message):
        if self.progress_recorder is not None:
            self.progress_recorder.set_progress(
                steps, self.total_steps, message)


def run_gold_digger(model, input_image_list, particle_group_count, mask=None, progress_recorder=None):
    print(f'Running with {model}')
    progress_setter = ProgressBarWrapper(progress_recorder, 20)
    progress_setter.update(1, "starting")
    artifact = get_artifact_status(model)
    clear_out_old_files(model)
    progress_setter.update(2, "loading and cutting up image")
    file_list, width, height, img_mask = load_data_make_jpeg(
        input_image_list, mask)
    progress_setter.update(4, "combining with white background")
    white = io.imread('media/White/white.png')
    combine_white(white, 'media/Output')
    progress_setter.update(5, "running PIX2PIX...")
    os.system(
        'python3 media/PIX2PIX/test.py --dataroot media/Output_Appended/ --name {0} --model pix2pix --direction AtoB --num_test 1000000 --checkpoints_dir media/PIX2PIX/checkpoints/ --results_dir media/PIX2PIX/results/'.format(
            model))
    print("RAN PIX2PIX")
    progress_setter.update(6, "Finished. stitching files together...")
    # Take only the Fake_B photos and stich together
    file_list = glob.glob(
        'media/PIX2PIX/results/{0}/test_latest/images/*_fake_B.png'.format(model))
    print("---BEFORE STITCH---")
    widthdiv256 = width
    heighttimeswidth = width * height
    folderstart = 'media/Output_ToStitch/'
    save_to_output_folder(file_list, model)
    picture, file_list = stitch_image(
        folderstart, widthdiv256, heighttimeswidth, artifact)
    imageio.imwrite('media/Output_Final/OutputStitched.png', picture)
    progress_setter.update(7, "Identifying green dots")
    cnts = count_green_dots()
    print("THIS IS WHERE IT WOULD SHOW THE IMAGE")
    all_coordinates, results6, results12, results18 = get_contour_centers_and_group(particle_group_count,
                                                                   cnts, img_mask)
    save_preview_figure(all_coordinates)
    save_histogram(all_coordinates)
    save_files_to_csv(results6, results12, results18)
    clear_out_input_dirs()
    print("SUCCESS!!")
    progress_setter.update(8, "Saving files")
    shutil.make_archive('media/GD_Output', 'zip', 'media/Output_Final')
    print('CREATED ZIP FILE')
    progress_setter.update(9, "All done")
