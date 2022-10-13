import pandas as pd
import re
import time
from feature_extraction import blobs_extraction
import numpy as np
from os.path import exists
import pickle
from random import randint
from digital_signature import sign_key_gen, digital_signature, verification
from fuzzy_extractor import generation, reproduction, secure_sketch
from utils_ import mk_dir

base_path = 'BASE_PATH/'
s_folder_path = base_path + 'secure_sketch/'
mk_dir(s_folder_path)


def robust_blobs(df: pd.DataFrame, file: str):
    """
    extract the robust blobs based os a set of images
    :param df: input dataframe
    :param file: file name
    :return: dataframe with the robust positions
    """
    # It is created an dataframe with the same size as df, pilled of string values.
    dataframe = pd.DataFrame(np.zeros((len(df), 3)).astype(str), columns=['x', 'y', 'r'])
    # The threshold is defined as the total number of columns divided by 3 because of the triplets (x,y,r).
    # Then, by 2 for obtaining the half of the images.)
    threshold = len(df.columns.values) // 3 // 2
    if 'case1' in file:
        for i in range(len(df)):
            if (df.loc[i] != '0.0').all() == True:
                x = np.round(np.mean(df.loc[i]["x"]))
                y = np.round(np.mean(df.loc[i]["y"]))
                r = np.round(np.mean(df.loc[i]["r"]))
                dataframe.loc[i] = x.astype(int), y.astype(int), r.astype(int)
            else:
                continue
    else:
        for i in range(len(df)):
            if ((df.loc[i] != '0.0').sum() // 3) > threshold:
                x = np.round(df.loc[i]['x'].replace('0.0', np.NaN).mean())
                y = np.round(df.loc[i]['y'].replace('0.0', np.NaN).mean())
                r = np.round(df.loc[i]['r'].replace('0.0', np.NaN).mean())
                dataframe.loc[i] = x.astype(int), y.astype(int), r.astype(int)
            else:
                continue

    return dataframe


def authentication_function(attempt: str, coin: int, h, r, n_AS,
                            txt_enr: str, txt_auth: str,
                            ssk_file_enr, ssk_file_auth):
    """
    :param attempt: folder with a set of images
    :param coin: 1 or 0
    :param h: a hash value
    :param r: random value of 256-bits
    :param n_AS: random value of 256-bits
    :param txt_enr: txt file
    :param txt_auth: txt file
    :param ssk_file_enr:
    :param ssk_file_auth:
    :return:
    """
    global signature, n_AD, psk, answer
    stage = 'Enrollment'
    str1 = [m.start() for m in re.finditer(r"/", attempt)][-2]
    str2 = [m.start() for m in re.finditer(r"/", attempt)][-1]

    if stage in attempt:
        x_max, coin, k, omega_concat, N = blobs_extraction(attempt, coin, txt_enr)
        t0 = time.time()
        omega_robust = robust_blobs(omega_concat, txt_enr)
        time_robust = round(time.time() - t0, 4)
    else:
        x_max, k, omega_concat, N = blobs_extraction(attempt, coin, txt_auth)
        t0 = time.time()
        omega_robust = robust_blobs(omega_concat, txt_auth)
        time_robust = round(time.time() - t0, 4)

    data = []

    if stage in attempt:
        t1 = time.time()
        _, omega_, sketch = secure_sketch(omega_robust, x_max, coin, k, N, stage=stage)
        sketch.to_pickle(s_folder_path + attempt[str1 + 1:str2] + '.pkl')
        time_ssk = round(time.time() - t1, 4)

        t2 = time.time()
        P, R = generation(omega_.astype(float).astype(int), sketch)
        _, h, r = P
        time_gen = round(time.time() - t2, 4)

        pubkey, _ = sign_key_gen(R)
        n_AS = "{0:x}".format(randint(0, 2 ** 256))
        data.append([attempt[str2 + 1:], attempt[str1 + 1:str2],
                     R, h, r, pubkey, n_AS,
                     time_robust, time_ssk, time_gen])

        if not exists(ssk_file_enr):
            dataframe = pd.DataFrame(data, columns=['attempt', 'csr', 'R', 'h', 'r', 'pubkey', 'n_AS',
                                                    'time_robust', 'time_ssk', 'time_gen'])
            dataframe.to_pickle(ssk_file_enr)
        else:
            df = pd.read_pickle(ssk_file_enr)
            df.loc[len(df)] = data[0]
            df.to_pickle(ssk_file_enr)

        print("R Enrollment:\t", R)
    else:
        ssk_info = pd.read_pickle(ssk_file_enr)
        ssk_info.set_index('csr', inplace=True)
        psk = ssk_info.loc[attempt[str1 + 1:str2]]['pubkey']

        t1 = time.time()
        omega_centers, omega_ = secure_sketch(omega_robust, x_max, coin, k, N)
        time_rec = round(time.time() - t1, 4)

        t2 = time.time()
        s = pd.read_pickle(s_folder_path + attempt[str1 + 1:str2] + '.pkl')
        omega_rec, R = reproduction(omega_.astype(float).astype(int), omega_centers.astype(float).astype(int), s, k, h,
                                    r)
        time_rep = round(time.time() - t2, 4)
        n_AD = "{0:x}".format(randint(0, 2 ** 256))

        if R == "{0:d}".format(int(0.0)):
            signature, answer = 'NA', 0
        else:
            _, privkey = sign_key_gen(R)
            signature = digital_signature(privkey, int((n_AS + n_AD), 16))
            answer = 1 if verification(psk, signature, n_AS, n_AD) else 0

        print("R Authentication:\t", (R))

        real = 0 if 'inter' in txt_enr or 'inter' in txt_auth else 1

        data.append([attempt[str2 + 1:], attempt[str1 + 1:str2],
                     'R', 'h', 'r', 'n_AS', 'n_AD', 'signature', answer, real,
                     time_robust, time_rec, time_rep])

        if not exists(ssk_file_auth):
            dataframe = pd.DataFrame(data, columns=['attempt', 'csr', 'R', 'h', 'r', 'n_AS', 'n_AD',
                                                    'signature', 'answer', 'real', 'time_robust', 'time_rec',
                                                    'time_rep'])
            dataframe.to_pickle(ssk_file_auth)
        else:
            df = pd.read_pickle(ssk_file_auth)
            df.loc[len(df)] = data[0]
            df.to_pickle(ssk_file_auth)

    return None
