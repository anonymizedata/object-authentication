import cv2
import glob
import numpy as np
import os
import pandas as pd
import re

numbers = re.compile(r'(\d+)')
a = 1


def names_reference_tags(reference_imgs_path):
    ref_imgs = sorted(glob.glob(reference_imgs_path + '/*.jpg'), key=numerical_sort)
    short_names = []
    for img in ref_imgs:
        short_names.append(img.replace(reference_imgs_path + '/', '').replace('.jpg', ''))

    return short_names


def open_image(file_name):
    """
    :param file_name: path of the image
    :rtype: (image)
    """
    image = cv2.imread(file_name)
    return image


def numerical_sort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def mk_dir(folder_path):
    """
    :param folder_path: Folder path
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def string_blobs(array_blobs):
    """
    :param array_blobs: array
    :return:
    """
    blobs_string = ''

    # Review the condition
    for line in range(len(array_blobs)):
        if np.all((array_blobs[line] == 0)) == False:
            bit_x0 = f"{int(array_blobs[line][0]):#0{6}x}"[2:]
            bit_y0 = f"{int(array_blobs[line][1]):#0{6}x}"[2:]
            blobs_string += (bit_x0 + bit_y0)

    return blobs_string


def head_txt_csr_file(file_name):
    with open(file_name, 'w') as f:
        f.write('csr' + '\t'
                + 'attempt' + '\t'
                + 'csr_name' + '\t'
                + 'x_max' + '\t'
                + 'm_blobs' + '\t'
                + 'N' + '\t'
                + 'n' + '\t'
                + 'k' + '\t'
                + 'coin' + '\t'
                + 'time_minutiae' + '\t'
                + 'time_embedding'
                + '\n')


def identifiers(x, y, k, N, a=a):
    """
    :param x: x-position
    :param y: y-position
    :param k: average radii
    :return: interval information
    """
    x_start, y_start = (x // (a * k)), (y // (a * k))
    x_end, y_end = (x_start + 1), (y_start + 1)

    index = y_start * N + x_end
    centers = np.array([int((x_start * a * k) + (a * k) // 2), int((y_start * a * k) + (a * k) // 2)])

    return index, centers


def blob_movement(x, y, k, N, coin, x_max, a=a):
    global x_new, y_new, index, centers, s

    s_ = (a * k) // 2
    x_max = N * k * a
    mod = k * a

    if (x % mod == 0) and (y % mod == 0):
        x_new = ((x + s_) % x_max) if (coin == 1) else ((x - s_) % x_max)
        y_new = ((y + s_) % x_max) if (coin == 1) else ((y + s_) % x_max)  # it was initially: (y + s)
    elif (x % mod == 0) and (y % mod != 0):
        x_new, y_new = ((x + s_) % x_max) if (coin == 1) else (x - s_) % x_max, y
    elif (x % mod != 0) and (y % mod == 0):
        x_new, y_new = x, ((y + s_) % x_max) if (coin == 1) else ((y - s_) % x_max)
    else:
        x_new, y_new = x, y

    index, centers = identifiers(x_new, y_new, mod, N)
    s = np.array([centers[0] - x, centers[1] - y])

    return (s, index, centers)


def blob_indexing(x_max, k, blobs_detected, a=a):
    """
    Placing the blobs into a big grid
    """
    N = len(np.arange(0, x_max, a * k))
    # N = len(np.arange(0, x_max, a * k))  + 1
    n = N ** 2
    omega = pd.DataFrame(np.zeros((n, 3)).astype(str), columns=['x', 'y', 'r'])

    for i in range(len(blobs_detected)):
        x, y = blobs_detected['x'][i], blobs_detected['y'][i]
        index = (y // (a * k)) * N + ((x // (a * k)) + 1)
        omega.loc[index] = blobs_detected.loc[i]

    return N, omega
