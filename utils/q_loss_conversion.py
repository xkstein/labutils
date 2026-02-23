import numpy as np

c = 299792458

def alpha_to_alpha_dB(alpha):
    '''alpha in m^-1 => alpha in dB m^-1'''
    return 10 * np.log10( np.exp(-alpha) )

def alpha_dB_to_alpha(alpha_dB):
    '''alpha in dB m^-1 => alpha in m^-1'''
    return -np.log( 10 ** ( alpha_dB / 10 ) )

def Q_to_alpha(Q, res_length=2*np.pi*200e-6, rough_neff=2, 
                 measurement_wavelength=1550e-9):
    '''alpha in m^-1'''
    loss_per_rt = 2 * np.pi * rough_neff * res_length / measurement_wavelength / Q
    alpha = -1 / res_length * np.log(1 - loss_per_rt)
    return alpha

def Q_to_alpha_dB(Q, res_length=2*np.pi*200e-6, rough_neff=2, 
                measurement_wavelength=1550e-9):
    '''alpha in dB m^-1'''
    return alpha_to_alpha_dB(
            Q_to_alpha(Q, res_length, rough_neff, measurement_wavelength)
        )

def alpha_to_Q(alpha, res_length, rough_neff=2, wavelength=1550e-9):
    '''takes alpha in m^-1'''
    loss_per_rt = 1 - np.exp(-alpha * res_length)
    Q = 2 * np.pi * res_length * rough_neff / wavelength / loss_per_rt
    return Q

def alpha_dB_to_Q(alpha_dB, res_length, rough_neff=2, wavelength=1550e-9):
    '''takes alpha in dB m^-1'''
    return alpha_to_Q(alpha_dB_to_alpha(alpha_dB), res_length, rough_neff, wavelength)

if __name__ == '__main__':
    assert np.isclose(Q_to_alpha(2.93e6), 2.77, 1e-2)
    assert np.isclose(Q_to_alpha_dB(2.93e6), -12, 1e-1)
    assert np.isclose(
            alpha_dB_to_alpha(Q_to_alpha_dB(2.93e6)),
            Q_to_alpha(2.93e6)
    )
    assert np.isclose(alpha_dB_to_Q(Q_to_alpha_dB(2.93e6), 2*np.pi*200e-6), 2.93e6)
    print('Q: 2.93 Mil')
    print(Q_to_alpha(2.93e6))
    print(Q_to_alpha_dB(2.93e6))
    print(alpha_dB_to_Q(Q_to_alpha_dB(2.93e6), 2*np.pi*200e-6))
