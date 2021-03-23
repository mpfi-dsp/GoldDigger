# imports
from GDapp.models import add_analyzed_image, add_gold_particle_coordinates, add_histogram_image, add_output_file
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
from django.conf import settings
# from sklearn.cluster import Kmeans


def get_artifact_status(model):
    # gets rid of the constant artifact in the up left corner
    if model == '87kGoldDigger':
        artifact = True
    else:
        artifact = False
    return artifact

# clears directories that need to be empty for a new run
def clear_out_old_files(model):
    shutil.rmtree('media/Output', ignore_errors=True)
    os.makedirs('media/Output')
    shutil.rmtree('media/Output_Appended', ignore_errors=True)
    os.makedirs('media/Output_Appended')
    shutil.rmtree('media/Output_Appended/test', ignore_errors=True)
    os.makedirs('media/Output_Appended/test')
    shutil.rmtree('media/PIX2PIX/results/{0}/test_latest/images'.format(model), ignore_errors=True)
    os.makedirs('media/PIX2PIX/results/{0}/test_latest/images'.format(model))
    shutil.rmtree('media/Output_ToStitch', ignore_errors=True)
    os.makedirs('media/Output_ToStitch')
    shutil.rmtree('media/Output_Final', ignore_errors=True)
    os.makedirs('media/Output_Final')

# crop mask file to the same size as the cropped image file
def crop_mask(mask, height256, width256):
    mask_path = pathlib.Path('media/Mask', mask)
    img_mask = io.imread(mask_path)
    img_mask = img_mask[:height256, :width256, :3]
    imageio.imwrite('media/Output_Final/' +
                    'CroppedMask'+'.png', img_mask)
    print("completed crop_mask function")
    return(img_mask)

#  gives height and width to give an image dimensions that are divisible by 256
def get_dimensions(img_new):
    shape = img_new.shape
    height = shape[0] // 256
    height256 = height * 256
    width = shape[1] // 256
    width256 = width * 256
    return height256, width256, height, width

# make 1 256x256 crop
def create_small_image(current_progress, total_progress, front_end_updater, img_size, img_new_w, i, j, r):
        current_progress += 1
        front_end_updater.update_progress(
            current_progress/total_progress * 100, 1)
        A = np.zeros((img_size[0], img_size[1], 3))
        A[:, :, :] = img_new_w[i, j, :, :]
        imageio.imwrite('media/Output/' + str(r) + '.png', A)
        r += 1
        return current_progress, r


# look in INPUT folder, crop photo and save crop to OUTPUT folder
# Cut up in order, append white images
def load_data_make_jpeg(image, mask, model, front_end_updater, imageName=''):
    file_list = pathlib.Path('media/Input', image)
    print(file_list)
    for entry in [file_list]:
        front_end_updater.post_message('loading image')
        front_end_updater.update_progress(10, 1)
        img_size = (256, 256, 3)
        img_new = io.imread(entry)

        height256, width256, height, width = get_dimensions(img_new)

        img_new = img_new[:height256, :width256, :3]
        img_mask = None
        if mask is not None:
            img_mask = crop_mask(mask, height256, width256)
        front_end_updater.update_progress(50, 1)
        img_new_w = view_as_blocks(img_new, img_size)
        img_new_w = np.uint8(img_new_w)
        imageio.imwrite('media/Output_Final/' +
                        f'Cropped-{imageName}-with-{model}' + '.png', img_new)
        r = 0
        total_progress = img_new_w.shape[0] * img_new_w.shape[1]
        current_progress = 0
        front_end_updater.post_message('cutting up image')
        # the cutting up image step is what gives all the "Lossy conversion" warnings in celery terminal
        front_end_updater.update_progress(90, 1)
        for i in range(img_new_w.shape[0]):
            for j in range(img_new_w.shape[1]):
                current_progress, r = create_small_image(current_progress, total_progress, front_end_updater, img_size, img_new_w, i, j, r)


    return file_list, width, height, img_mask


def combine_white(white, folderA, front_end_updater):
    print(os.getcwd())
    os.chdir(folderA)
    total_progress = len(os.listdir('.'))
    current_progress = 0
    for file in os.listdir('.'):
        front_end_updater.update_progress(
            current_progress/total_progress * 100, 1)
        current_progress += 1
        imA = io.imread(file)
        newimage = np.concatenate((imA, white), axis=1)
        imageio.imwrite('../Output_Appended/test/' + file, newimage)

    os.chdir('../../')
    print(os.getcwd())


# Save to OUTPUT folder
def save_to_output_folder(file_list, model):
    for entry in file_list:
        split_name = entry.split('/')
        #print(split_name)
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


def count_green_dots(model, imageName='', thresh_sens=4):
    # From Diego:
    # 1. Finds green square and then the center of that (x,y)
    # 2. Then I perform a flood fill on that (x,y) on the original image
    # 3. So it fills out the entire dark particle
    # 4. Then I find the contour of that mask and the xy of that new circle
    # 5. I do this so inconsistencies in the green mask dont affect the area of the gold particle
    # Basically it just uses the green masks to find a seed point to start flood filling. This makes sure that the mask is the exact size of the gold particle
    img = cv2.imread('media/Output_Final/OutputStitched.png')
    img_original = cv2.imread(f'media/Output_Final/Cropped-{imageName}-with-{model}.png')
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
        num, im, mask, rect = cv2.floodFill(img_original, flood_mask, (seedlistx[i], seedlisty[i]), 1, (thresh_sens,) * 3, (thresh_sens,) * 3,
                                            floodflags)

    print(np.mean(img_original))
    # cv2.imshow("Image", flood_mask)
    # cv2.waitKey(0)

    flood_mask = flood_mask[:h, :w]
    cnts = cv2.findContours(
        flood_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts


def check_if_coordinate_is_in_mask(x, y, mask):
    if mask is None:
        return True
    # if coordinate is in white region on the mask image, return false (do not count it)
    elif np.array_equal(mask[x, y], np.array((255, 255, 255))):
        return False
    else:  # if coordinate is not in white region return true (do count it)
        return True


def get_contour_centers(cnts, img_mask):
    # group using k means
    # report size distributions
    # show relative size histograms and cutoffs

    all_coordinates = pd.DataFrame(columns=['X','Y','Area'])
    coords_in_mask = pd.DataFrame(columns=['X','Y','Area'])

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
            all_coordinates = all_coordinates.append({'X': cX, 'Y': cY,'Area':cv2.contourArea(c)},
                                                     ignore_index=True)

            if check_if_coordinate_is_in_mask(cY, cX, img_mask):

                # add condition to get rid of some of the crazy outliers in histogram later on
                if cv2.contourArea(c) < 500:
                    coords_in_mask = coords_in_mask.append({'X': cX, 'Y': cY,'Area':cv2.contourArea(c)},
                                                       ignore_index=True)
    return all_coordinates, coords_in_mask

def sort_from_thresholds(coords_in_mask, particle_group_count, thresholds_list_string):
    #print(thresholds_list_string)
    thresholds_list=[]
    #print(thresholds_list_string.split(","))

    for x in thresholds_list_string.split(","):
        thresholds_list.append(int(x))

    print("thresholds_list:")
    print(thresholds_list)

    results1 = pd.DataFrame(columns=['X', 'Y'])
    results2 = pd.DataFrame(columns=['X', 'Y'])
    results3 = pd.DataFrame(columns=['X', 'Y'])

    for index, row in coords_in_mask.iterrows():

        if particle_group_count == 1:
            if row['Area'] > thresholds_list[0] and row['Area'] < thresholds_list[1]:
                results1 = results1.append({'X': row['X'], 'Y': row['Y']}, ignore_index=True)

        if particle_group_count == 2:
            if row['Area'] > thresholds_list[0] and row['Area'] < thresholds_list[1]:
                results1 = results1.append({'X': row['X'], 'Y': row['Y']}, ignore_index=True)
            elif row['Area'] > thresholds_list[2] and row['Area'] < thresholds_list[3]:
                results2 = results2.append({'X': row['X'], 'Y': row['Y']}, ignore_index=True)

        if particle_group_count == 3:
            if row['Area'] > thresholds_list[0] and row['Area'] < thresholds_list[1]:
                results1 = results1.append({'X': row['X'], 'Y': row['Y']}, ignore_index=True)
            elif row['Area'] > thresholds_list[2] and row['Area'] < thresholds_list[3]:
                results2= results2.append({'X': row['X'], 'Y': row['Y']}, ignore_index=True)
            elif row['Area'] > thresholds_list[4] and row['Area'] < thresholds_list[5]:
                results3 = results3.append({'X': row['X'], 'Y': row['Y']}, ignore_index=True)


    return results1, results2, results3


def clear_out_input_dirs():
    shutil.rmtree('media/Input', ignore_errors=True)
    os.mkdir('media/Input')


def update_progress(progress_recorder, step, total_steps, message):
    if progress_recorder is not None:
        progress_recorder.set_progress(step, total_steps, message)


def save_preview_figure(coordinates, front_end_updater):
    img = cv2.imread('media/Output_Final/OutputStitched.png')
    img2 = img[:, :, ::-1]
    plt.figure(1)
    plt.imshow(img2)
    plt.scatter(coordinates.X.values, coordinates.Y.values,
                facecolors='none', edgecolors='r')
    plt.gca().set_axis_off()
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    preview_file_path = 'media/Output_Final/preview.png'
    if os.path.exists(preview_file_path):
        os.remove(preview_file_path)
    plt.savefig(preview_file_path, bbox_inches='tight',
                pad_inches=0)
    add_analyzed_image(front_end_updater.pk, preview_file_path)


def save_histogram(coordinates, front_end_updater):
    plt.figure(2)
    plt.hist(coordinates.Area.values, bins=100)
    plt.title('Particle Area Histogram')
    plt.xlabel('Size (px)')
    plt.ylabel('Count')
    hist_path = 'media/Output_Final/preview_histogram.png'
    if os.path.exists(hist_path):
        os.remove(hist_path)
    plt.savefig(hist_path, bbox_inches='tight')
    add_histogram_image(front_end_updater.pk, hist_path)


# eleanor added for coordinates6nm
def save_coordinates(coordinates, name, front_end_updater):
    coordinates_path = 'media/Output_Final/' + name + '.csv'

    if os.path.exists(coordinates_path):
        os.remove(coordinates_path)
    coordinates.to_csv(coordinates_path, index=False)
    #add_coordinatesGroup1(front_end_updater.pk, coordinates6nm_path)


def save_all_results(coordinates, coordinates1, coordinates2, coordinates3, model, front_end_updater, imageName=''):
    sub_path = 'results'
    results_path = os.path.join(settings.MEDIA_ROOT, sub_path)
    if not os.path.isdir(results_path):
        os.makedirs(results_path)
    timestr = time.strftime("%Y%m%d%H%M%S")
    coordinates_path_relative = os.path.join(
        sub_path, 'coordinates' + timestr + '.csv')
    coordinates_path_absolute = os.path.join(
        settings.MEDIA_ROOT, coordinates_path_relative)
    coordinates.to_csv(coordinates_path_absolute, index=None,
                       header=True)
    add_gold_particle_coordinates(
        front_end_updater.pk, coordinates_path_absolute)

    # Eleanor added for 6nm
    #coordinates6nm_path_relative = os.path.join(
    #    sub_path, 'coordinates6nm' + timestr + '.csv')
    #coordinates6nm_path_absolute = os.path.join(
    #    settings.MEDIA_ROOT, coordinates6nm_path_relative)
    #coordinates6nm.to_csv(coordinates6nm_path_absolute, index=None,
    #                      header=True)
    #add_coordinatesGroup1(front_end_updater.pk, coordinates6nm_path_absolute)

    save_coordinates(coordinates1, f'coordsGroup1-{imageName}-with-{model}', front_end_updater)
    save_coordinates(coordinates2, f'coordsGroup2-{imageName}-with-{model}', front_end_updater)
    save_coordinates(coordinates3, f'coordsGroup3-{imageName}-with-{model}', front_end_updater)
    save_preview_figure(coordinates, front_end_updater)
    save_histogram(coordinates, front_end_updater)




def run_gold_digger(model, input_image_list, particle_group_count, thresholds_list_string, thresh_sens=4, mask=None, front_end_updater=None):
    print(f'Running with {model}')
    if thresholds_list_string == '':
        print('NO THRESHOLDS')
        return

    imageName = pathlib.Path(input_image_list).stem
    print(f'Image name: {imageName}')

    front_end_updater.update(1, "starting")
    artifact = get_artifact_status(model)
    clear_out_old_files(model)
    front_end_updater.update(2, "loading and cutting up image")



    file_list, width, height, img_mask = load_data_make_jpeg(
        input_image_list, mask, model, front_end_updater, imageName=imageName)
    front_end_updater.update(4, "combining with white background")
    white = io.imread('media/White/white.png')
    combine_white(white, 'media/Output', front_end_updater)
    front_end_updater.update(5, "running PIX2PIX...")
    os.system(
        'python3 media/PIX2PIX/test.py --dataroot media/Output_Appended/ --name {0} --model pix2pix --direction AtoB --num_test 1000000 --checkpoints_dir media/PIX2PIX/checkpoints/ --results_dir media/PIX2PIX/results/'.format(
            model))
    print("RAN PIX2PIX")
    front_end_updater.update(6, "Finished. stitching files together...")
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
    front_end_updater.update(7, "Identifying green dots")
    cnts = count_green_dots(model, imageName=imageName, thresh_sens=thresh_sens)
    print("THIS IS WHERE IT WOULD SHOW THE IMAGE")
    all_coordinates, coords_in_mask = get_contour_centers(cnts, img_mask)
    #print(thresholds_list_string)
    #print(thresholds_list_string.split(","))
    #thresholds_list_string = "2, 10, 15, 40"

    print("image name?: " + input_image_list)
    print(pathlib.Path(input_image_list).stem)

    results1, results2, results3 = sort_from_thresholds(coords_in_mask,
                                                        particle_group_count, thresholds_list_string)

    save_all_results(coords_in_mask, results1, results2, results3, model, front_end_updater, imageName=imageName)

    clear_out_input_dirs()
    print("SUCCESS!!")
    front_end_updater.update(8, "Saving files")

    output_file = shutil.make_archive(f'media/Output-{imageName}-with-{model}', 'zip', 'media/Output_Final')

    #output_path = os.path.join(settings.MEDIA_ROOT, 'GD_Output.zip')
    add_output_file(front_end_updater.pk, f'media/Output-{imageName}-with-{model}.zip')

    print('CREATED ZIP FILE')
    front_end_updater.update(9, "All done")
    front_end_updater.analysis_done()
