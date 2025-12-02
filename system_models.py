import numpy as np
from scipy import signal


def closed_loop(C, num, den):
    num_ol = np.polynomial.polynomial.polymul(C.num[::-1], num[::-1])[::-1]
    den_ol = np.polynomial.polynomial.polymul(C.den[::-1], den[::-1])[::-1]
    L = max(len(den_ol), len(num_ol))
    den_ol = np.pad(den_ol, (L - len(den_ol), 0))
    num_ol = np.pad(num_ol, (L - len(num_ol), 0))
    den_cl = den_ol + num_ol
    return signal.TransferFunction(num_ol, den_cl)


def create_plant(K, tau_s, tau_p):
    num = [K]
    den = np.convolve([tau_s, 1], [tau_p, 1])
    return signal.TransferFunction(num, den), num, den


def create_controllers(Kc_P, Kc_PI, Ti_PI, Kc_PID, Ti_PID, Td_PID):
    controllers = {}
    controllers['P'] = signal.TransferFunction([Kc_P], [1])
    controllers['PI'] = signal.TransferFunction([Kc_PI*Ti_PI, Kc_PI], [Ti_PI, 0])
    controllers['PID'] = signal.TransferFunction(
        [Kc_PID*Ti_PID*Td_PID, Kc_PID*Ti_PID, Kc_PID], 
        [Ti_PID, 0]
    )
    return controllers
