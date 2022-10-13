from ecdsa._compat import remove_whitespace
from ecdsa import ellipticcurve
from ecdsa.ecdsa import Public_key, Private_key
from random import randrange, randint

_p = int(remove_whitespace("""115792089210356248762697446949407573530086143415290314195533631308867097853951"""))
_r = int(remove_whitespace("""115792089210356248762697446949407573529996955224135760342422259061068512044369"""))
_b = int(remove_whitespace("""5AC635D8 AA3A93E7 B3EBBD55 769886BC 651D06B0 CC53B0F6 3BCE3C3E 27D2604B"""), 16)
_Gx = int(remove_whitespace("""6B17D1F2 E12C4247 F8BCE6E5 63A440F2 77037D81 2DEB33A0 F4A13945 D898C296"""), 16)
_Gy = int(remove_whitespace("""4FE342E2 FE1A7F9B 8EE7EB4A 7C0F9E16 2BCE3357 6B315ECE CBB64068 37BF51F5"""), 16)

curve_256 = ellipticcurve.CurveFp(_p, -3, _b, 1)
generator_256 = ellipticcurve.PointJacobi(curve_256, _Gx, _Gy, 1, _r, generator=True)

g = generator_256
n = g.order()


def sign_key_gen(R):
    secret = int(R, 16)
    pubkey = Public_key(g, g * secret)
    privkey = Private_key(pubkey, secret)

    return pubkey, privkey


def digital_signature(privkey, nonces):
    fresh = randrange(1, n)
    signature = privkey.sign(nonces, fresh)

    return signature


def verification(pubkey, signature, n_AS, n_AD):
    return pubkey.verifies(int((n_AS + n_AD), 16), signature)
