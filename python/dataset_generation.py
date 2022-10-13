import cv2, glob
import imutils
import numpy as np
import os, random, re
from utils_ import numerical_sort, open_image

base_path = 'BASE_PATH/'
ref_images_path = base_path + 'dataset/reference_images/'
database_path = base_path + 'csr_responses/'


def resize_image(image_path: str, scale_percent: int = 80) -> np.matrix:
    """
    :param src_image: matrix
    :param scale_percent: value to be resized
    :rtype: resized image
    """
    image = open_image(image_path)
    h, w, d = image.shape

    # find the image's x- and y-center
    height_center, width_center = h // 2, w // 2
    center = min(height_center, width_center)

    h_0, h_1, w_0, w_1 = (height_center - center), (height_center + center), \
                         (width_center - center), (width_center + center)

    squared_image = image[h_0:h_1, w_0:w_1, :]
    image_size = int((center * 2 * scale_percent) / 100)
    dimension = (image_size, image_size)

    resized = cv2.resize(squared_image, dimension, interpolation=cv2.INTER_AREA)

    return (resized)


def image_generation(base_path: str, image_path: str, std_start: float = 0, std_stop: float = 0.3, rot: str = 'OFF',
                     blur_in: int = 1, blur_out: int = 4, stage: str = 'Enrollment'):
    """
    :param base_path: main base path
    :param image_path: image path
    :param std_start: min standard deviation for the uniform distribution
    :param std_stop: max standard deviation for the uniform distribution
    :param rot: ON if rotation is desired
    :param blur_in: min size for the blurring kernel
    :param blur_out: max size for the blurring kernel
    :param stage: "Enrollment" or "Authentication"
    :return: set of images
    """
    n_attempts = 1 if 'Enrollment' in stage else 20
    str_position = [m.start() for m in re.finditer(r"/", image_path)][-1]

    # Resize the image, the percentage cna be changed
    resized_image = resize_image(image_path)
    h, w, d = resized_image.shape

    for i in range(1, n_attempts + 1):
        folder_name = base_path + stage + '/' + image_path[str_position + 1:-4] + '/F_{0}'.format(i)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        counter = 7

        if rot == 'OFF':
            rnd_vals = np.random.uniform(std_start, std_stop, 5)
            for val in rnd_vals:
                gauss_noise = np.random.normal(0, val, resized_image.size)
                gauss_noise = gauss_noise.reshape(h, w, d).astype('uint8')
                img_gauss = cv2.add(resized_image, gauss_noise)
                for blur in range(blur_in, blur_out):
                    counter -= 1
                    ksize = (blur, blur)
                    image_blurred = cv2.blur(img_gauss, ksize)
                    if counter < 0:
                        break
                    else:
                        cv2.imwrite(folder_name + '/'
                                    + image_path[str_position + 1:-4]
                                    + '_gauss_' + str(round(val, 4)).replace('.', '_')
                                    + '_blur_' + str(blur)
                                    + '.jpg', image_blurred)
        else:
            # Copy the reference image into each folder
            cv2.imwrite(folder_name + '/' + image_path[str_position + 1:-4] + '.jpg', resized_image)
            rot_start, rot_stop = 1, 6
            for angle in random.sample(range(rot_start, rot_stop), (rot_stop - rot_start)):
                val = random.uniform(std_start, std_stop)
                gauss_noise = np.random.normal(0, val, resized_image.size)
                gauss_noise = gauss_noise.reshape(h, w, d).astype('uint8')
                img_gauss = cv2.add(resized_image, gauss_noise)
                image_rotated = imutils.rotate(img_gauss, angle)
                for blur in range(blur_in, blur_out):
                    counter -= 1
                    ksize = (blur, blur)
                    image_blurred = cv2.blur(image_rotated, ksize)
                    resized = cv2.resize(image_blurred)
                    if counter < 0:
                        break
                    else:
                        cv2.imwrite(folder_name + '/'
                                    + image_path[str_position + 1:-4]
                                    + '_rot_' + str(angle)
                                    + '_gauss_' + str(round(val, 4)).replace('.', '_')
                                    + '_blur_' + str(blur)
                                    + '.jpg', resized)


# Dataset Generation
def dataset_generation(path_reference_images: str):
    """
    :return: set of images
    """
    stages = ['Enrollment', 'Authentication']
    ref_images = sorted(glob.glob(path_reference_images + '*.jpg'), key=numerical_sort)
    for stage in stages[:]:
        for ref_image in ref_images[:]:
            image_generation(database_path, ref_image, stage=stage)


dataset_generation(ref_images_path)
