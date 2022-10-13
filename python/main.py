from contextlib import suppress
import datetime
import glob
from reliable_information import authentication_function
import multiprocessing as mp
import pandas as pd
import random
import re
import time
from utils_ import head_txt_csr_file, numerical_sort, mk_dir

N_CORES = 1

TODAY = str(datetime.datetime.today())[:10].replace('-', '')
base_path = 'BASE_PATH/'

data_folder_path = base_path + 'results/'
mk_dir(data_folder_path)

csr_responses_path = base_path + 'csr_responses/'
stages = ['Enrollment', 'Authentication']
case = ' case1'
txt_csr_enr = data_folder_path + TODAY + case + ' enrol_information.txt'
ssk_file_enr = data_folder_path + TODAY + case + ' enrol_ssk.pickle'

txt_csr_auth = data_folder_path + TODAY + case + ' auth_information.txt'
ssk_file_auth = data_folder_path + TODAY + case + ' auth_ssk.pickle'


def result_align_score(result):
    global align
    align.append(result)


if __name__ == '__main__':
    iter = 0
    for stage in stages:
        if 'Enrollment' in stage:
            head_txt_csr_file(txt_csr_enr)
            csr_responses = sorted(glob.glob(csr_responses_path + stage + '/*'), key=numerical_sort)
            ts0 = time.time()
            for csr_response in csr_responses[:]:
                coin = random.randint(0, 1)
                attempts = sorted(glob.glob(csr_response + '/*'), key=numerical_sort)
                align = []
                pool = mp.Pool(N_CORES)
                for attempt in attempts:
                    print('Attempt:', attempt)
                    pool.apply_async(authentication_function,
                                     args=(attempt, coin, 'h', 'r', 'n_AS', txt_csr_enr, 'txt', ssk_file_enr,
                                           'ssk_file_auth'),
                                     callback=result_align_score)
                pool.close()
                pool.join()
            print(f'{(time.time() - ts0) / 60}', 'minutes')
        else:
            head_txt_csr_file(txt_csr_auth)
            ts0 = time.time()
            ssk_file_enr = data_folder_path + '20220914' + case + ' enrol_ssk.pickle'
            txt_csr_enr = data_folder_path + '20220914' + case + ' enrol_information.txt'
            ssk_info = pd.read_pickle(ssk_file_enr)
            ssk_info.set_index('csr', inplace=True)
            csr_info = pd.read_csv(txt_csr_enr, delimiter='\t')
            csr_info.set_index("csr", inplace=True)
            csr_responses = sorted(glob.glob(csr_responses_path + stage + '/*'), key=numerical_sort)
            for csr_response in csr_responses[:]:
                attempts = sorted(glob.glob(csr_response + '/*'), key=numerical_sort)
                align = []
                pool = mp.Pool(N_CORES)
                # with suppress(Exception):
                for attempt in attempts:
                    print('Attmept:', attempt)
                    str0 = [m.start() for m in re.finditer(r"/", attempt)][-2]
                    str1 = [m.start() for m in re.finditer(r"/", attempt)][-1]
                    csr = attempt[str0 + 1:str1]
                    df_csr_info = csr_info.loc[csr]
                    coin = df_csr_info["coin"][0]
                    df_ssk_info = ssk_info.loc[csr]
                    h, r, n_AS = df_ssk_info['h'], df_ssk_info['r'].encode(), df_ssk_info['n_AS']
                    pool.apply_async(authentication_function,
                                     args=(
                                         attempt, coin, h, r, n_AS, 'txt', txt_csr_auth, ssk_file_enr,
                                         ssk_file_auth),
                                     callback=result_align_score)
                pool.close()
                pool.join()
            print(f'{(time.time() - ts0) / 60}', 'minutes')
