import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle

class Periodogram:
    '''
    Periodogram object for storing and operating on Lomb-Scargle periodograms
    '''
    t: np.array
    '''Time series'''
    data: np.array
    '''Flux or magnitude time series'''
    freqs: np.array
    '''Frequency grid for the periodogram'''
    amps: np.array
    '''Amplitude spectrum of the time series. Only one of amps or powers will be populated based on the mode'''
    powers: np.array
    '''Power spectrum of the time series. Only one of amps or powers will be populated based on the mode'''
    fbounds: tuple
    '''(fmin, fmax) frequency bounds'''
    nyq_mult: int
    '''Multiple of the Nyquist frequency to use as the maximum frequency'''
    oversample_factor: int
    '''Oversample factor for the frequency grid'''
    mode: str
    """'amplitude' or 'power'"""

    def __init__(self, t: np.array, data: np.array, fbounds: tuple = None, nyq_mult: int = 1, oversample_factor: int = 5, mode: str = 'amplitude'):
        '''
        Constructor for Periodogram object
        '''
        self.freqs = None
        self.amps = None
        self.powers = None
        self.fbounds = fbounds
        self.nyq_mult = nyq_mult
        self.oversample_factor = oversample_factor
        self.mode = mode
        self.amplitude_power_spectrum(t, data)

    def amplitude_power_spectrum(self, t: np.array, data: np.array):
        '''
        Calculate the amplitude spectrum of the time series y(t)
        
        Parameters
        ----------
        t : array_like
            The time series
        y : array_like
            Flux or magnitude time series
        fbounds : tuple
            (fmin, fmax) frequency bounds
        nyq_mult : float
            Multiple of the Nyquist frequency to use as the maximum frequency
        oversample_factor : float
            Oversample factor for the frequency grid
        mode : str
            'amplitude' or 'power'

        Returns
        -------
        freqs : array_like
            Frequency grid
        amps : array_like
            Amplitude spectrum
        '''
        tmax = t.max()
        tmin = t.min()
        fmin, fmax = self.fbounds if self.fbounds is not None else (None, None)
        df = 1.0 / (tmax - tmin)
        
        if fmin is None:
            fmin = df
        if fmax is None:
            fmax = (0.5 / np.median(np.diff(t)))*self.nyq_mult

        freqs = np.arange(fmin, fmax, df / self.oversample_factor)
        
        model = LombScargle(t, data)
        sc = model.power(freqs, method="fast", normalization="psd")

        if self.mode == 'amplitude':
            amps = np.sqrt(4./len(t)) * np.sqrt(sc)
            self.freqs = freqs
            self.amps = amps
        elif self.mode == 'power':
            powers = np.sqrt(4./len(t))**2 * sc
            self.freqs = freqs
            self.powers = powers

    def plot(self, ax: plt.axes = None, mode: str = 'amplitude', **kwargs):
        '''
        Plot the periodogram
        
        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            The axes to plot on
        mode : str
            'amplitude' or 'power'
        show_peaks : bool
            If True, plot the identified peaks
        '''
        if ax is None:
            ax = plt.gca()

        if mode == 'amplitude':
            ax.plot(self.freqs, self.amps, **kwargs) 
        elif mode == 'power':
            ax.plot(self.freqs, self.powers, **kwargs)
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Amplitude' if mode == 'amplitude' else 'Power')
        return ax
    