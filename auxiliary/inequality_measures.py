"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""

"""
Source Citation: https://stackoverflow.com/questions/48999542/more-efficient-weighted-gini-coefficient-in-python
From stackoverflow user: https://stackoverflow.com/users/288162/ga%c3%abtan-de-menten
"""

import numpy as np
from scipy.stats import variation


def gini_index(np_arr):
    sorted_x = np.sort(np_arr)
    n = len(np_arr)
    cumx = np.cumsum(sorted_x)
    return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n


def coeff_variation(np_arr):
    return variation(np_arr)


def theil_t(np_arr):
    mean = np.mean(np_arr)
    theil = np.sum((np_arr / mean) * np.log(np_arr / mean))
    return theil


def theil_l(np_arr):
    mean = np.mean(np_arr)
    theil = np.sum(np.log(mean / np_arr))
    return theil


def hoover_index(np_arr):
    mean = np.mean(np_arr)
    hoover = 0.5*((np.sum(abs(np_arr - mean)))/np.sum(np_arr))
    return hoover