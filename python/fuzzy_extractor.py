import hashlib
import numpy as np
import random
import pandas as pd
from scipy.spatial.distance import chebyshev
from utils_ import blob_movement, string_blobs

a = 1


def secure_sketch(omega_reliable, x_max, coin, k, N, stage='Authentication'):
    center = pd.DataFrame(np.zeros((len(omega_reliable), 3)).astype(str), columns=['x', 'y', 'r'])
    omega_ = pd.DataFrame(np.zeros((len(omega_reliable), 3)).astype(str), columns=['x', 'y', 'r'])
    sketch = pd.DataFrame(np.zeros((len(omega_reliable), 3)).astype(str), columns=['x', 'y', 'r'])

    for i in omega_reliable.index:
        if omega_reliable.loc[i].astype(str).str.isdigit().all() == True:
            s, index, centers = blob_movement(omega_reliable["x"][i], omega_reliable["y"][i], k, N, coin, x_max)
            sketch.loc[index] = np.concatenate([s, [omega_reliable["r"][i]]])
            center.loc[index] = np.concatenate([centers, [omega_reliable["r"][i]]])
            omega_.loc[index] = omega_reliable["x"][i], omega_reliable["y"][i], omega_reliable["r"][i]

    if stage == 'Authentication':
        return center, omega_
    else:
        s = sketch.astype(float).astype(int)  # change here
        return center, omega_, s


def robust_secure_sketch(omega, s):
    omega_str = string_blobs(omega.to_numpy()).encode()
    s_str = string_blobs(s.to_numpy()).encode()

    h = "{0:d}".format(int(hashlib.sha256(omega_str + s_str).hexdigest(), 16))

    return (h, omega_str)


def generation(omega, s):
    r = "{0:d}".format(random.randint(0, 2 ** 256)).encode()
    h, omega_str = robust_secure_sketch(omega, s)
    P = (s, h, r.decode())

    R = "{0:d}".format(int(hashlib.sha256(omega_str + r).hexdigest(), 16))

    return (P, R)


def robust_reconstruction(omega_prime, omega_centers, s, k, h, a=a):
    omega_rec = omega_centers - s

    omega_rec_str = string_blobs(omega_rec.to_numpy()).encode()
    s_str = string_blobs(s.to_numpy()).encode()

    h_rec = "{0:d}".format(int(hashlib.sha256(omega_rec_str + s_str).hexdigest(), 16))

    chebyshev_dist = [j for j in range(len(omega_rec)) if chebyshev((omega_rec["y"][j], omega_rec["x"][j]),
                                                                    (omega_prime["y"][j],
                                                                     omega_prime["x"][j])) >= (a * k // 2)]
    if (len(chebyshev_dist) == 0) and (h == h_rec):
        return (omega_rec, omega_rec_str)
    else:
        return (omega_rec, '0')


def reproduction(omega_prime, omega_centers, s, k, h, r):
    omega_rec, omega_rec_str = robust_reconstruction(omega_prime, omega_centers, s, k, h)

    if omega_rec_str == '0':
        R = "{0:d}".format(int(0.0))
    else:
        R = "{0:d}".format(int(hashlib.sha256(omega_rec_str + r).hexdigest(), 16))

    return omega_rec, R
