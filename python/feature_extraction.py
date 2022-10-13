import cv2
import glob
import pandas as pd
import re
from skimage.feature import blob_log
import time
from utils_ import open_image, numerical_sort, blob_indexing


def blobs_extraction(attempt: str, coin: int, txt_enrollment: str):
    """
    :param attempt: the folder's path with a set of images
    :param coin: 1 or 0
    :param txt_enrollment: It is the file path
    :return: x_max, coin, k, omega_concat, N
    """
    # x_max and y_max are the image's size, k the blobs diameter, N the number of intervals in one-dimension
    global x_max, y_max, k, N

    # min, max and intermediate standard deviation for Gaussian kernel of the set of images
    if 'Image_972' in attempt:
        min_sigma, max_sigma, num_sigma = 6, 12, 6
    elif 'Image_975' in attempt or 'Image_997' in attempt:
        min_sigma, max_sigma, num_sigma = 8, 18, 8
    elif 'Image_1079' in attempt:
        min_sigma, max_sigma, num_sigma = 8, 20, 8
    elif 'Image_618' in attempt:
        min_sigma, max_sigma, num_sigma = 9, 14, 9
    elif 'Image_1104' in attempt or 'Image_2366' in attempt:
        min_sigma, max_sigma, num_sigma = 10, 16, 10
    elif 'Image_6' in attempt or 'Image_7' in attempt:
        min_sigma, max_sigma, num_sigma = 12, 16, 14
    elif 'tag9' in attempt or 'tag10' in attempt or 'tag11' in attempt or 'tag13' in attempt or 'tag14' in attempt \
            or 'tag15' in attempt or 'tag16' in attempt or 'tag17' in attempt:
        min_sigma, max_sigma, num_sigma = 4, 8, 6
    else:
        min_sigma, max_sigma, num_sigma = 6, 14, 12

    responses = sorted(glob.glob(attempt + '/*.jpg'), key=numerical_sort)
    omega_concat = []
    for response in responses:
        ts1 = time.time()
        IMAGE_ = open_image(response)
        x_max, y_max, _ = IMAGE_.shape

        str0 = [m.start() for m in re.finditer(r"/", response)][-3]
        str1 = [m.start() for m in re.finditer(r"/", response)][-2]
        str2 = [m.start() for m in re.finditer(r"/", response)][-1]

        gray_scale = cv2.cvtColor(IMAGE_, cv2.COLOR_BGR2GRAY)
        # Blobs detection and extraction
        blobs_vector = (blob_log(gray_scale,
                                 min_sigma=min_sigma, max_sigma=max_sigma, num_sigma=num_sigma,
                                 threshold=0.07, overlap=1, exclude_border=2)).astype(int)  # Blob's detection

        m_blobs, _ = blobs_vector.shape
        # average fo the blobs diameter
        k = int(blobs_vector[:, 2].mean()) * 2
        # transform an array into a df
        blobs_detected_df = pd.DataFrame(blobs_vector, columns=["x", "y", "r"]).sort_values(
            ["x", "y"], ascending=[True, True]).reset_index(drop=True)
        time_blobs_detection = f'{round(time.time() - ts1, 4)}'

        ts2 = time.time()
        N, omega = blob_indexing(x_max, k, blobs_detected_df)
        time_grid = f'{round(time.time() - ts2, 4)}'
        omega_concat.append(omega)

        # write the outputs on a txt file
        with open(txt_enrollment, 'a') as file:
            file.write(response[str0 + 1:str1] + '\t'
                       + response[str1 + 1: str2] + '\t'
                       + response[str2 + 1:] + '\t'
                       + str(x_max) + '\t'
                       + str(m_blobs) + '\t'
                       + str(N) + '\t'
                       + str(N ** 2) + '\t'
                       + str(k) + '\t'
                       + str(coin) + '\t'
                       + (time_blobs_detection) + '\t'
                       + (time_grid)
                       + '\n')

    omega_concat = pd.concat(omega_concat, axis=1)

    if 'Enrollment' in attempt:
        return x_max, coin, k, omega_concat, N
    else:
        return x_max, k, omega_concat, N
