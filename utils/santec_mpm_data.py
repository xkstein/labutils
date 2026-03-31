'''
This module is for interpreting data from the santec MPM
'''
import numpy as np
import pandas as pd
import io

def get_ranges_from_header(lines: io.FileIO | list):
    '''Extracts the senstivity ranges of each sweep from file header'''
    reading_ranges = False
    channel_ranges = {}

    for line in lines:
        if line.startswith('Power meter range'):
            reading_ranges = True
        if line.strip() == '--HEADER END--':
            break
        if reading_ranges:
            entries = [ l.strip() for l in line.split(',') ]
            range_units = [ el[-3:] for el in entries[3:] ]
            ranges = [ tuple( float(_el.strip()) for _el in el[:-3].split('～') ) for el in entries[3:] ]
            channel_name = entries[2][1:-1].upper()
            channel_ranges[channel_name] = ranges
            channel_ranges[channel_name + '_units'] = range_units
    else:
        raise Exception('Channel Ranges not found in file')

    return channel_ranges

def stitch_sweeps(sweeps: list, sweep_ranges: list):
    '''
    Stitches sweeps of decreasing senstivity
    
    Arguments:
        sweeps: list of sweep data in order of decreasing senstivity
        sweep_range: range of corresponding to the data in sweeps
    '''
    assert len(sweeps) == len(sweep_ranges), 'Need range information for every sweep'

    if len(sweeps) == 1:
        return np.array(sweeps[0])

    data = np.array(sweeps[0])
    for _range, _sweep in zip(sweep_ranges[1:], sweeps[1:]):
        saturated_data = data[data > ( np.mean(data) + np.std(data) )]
        if len(saturated_data) > 0:
            ceil = np.mean(saturated_data)
        else:
            ceil = np.max(data)
        
        if ceil < min(_range) - 5:
            # this is really hacky, but sometimes if you have a deep stopband, the 
            ceil = min(_range)
        
        new_data = np.array(_sweep)
        data[new_data > ceil - 1] = new_data[new_data > ceil - 1]
    return data

def read_mpm_file(path):
    '''
    Parses raw data file from Santec MPM
    
    Stitching algorithm (sorting from high to low sensitivity):
        1. Try to detect the saturation point of the last sweep
        2. If that can't be found: default to using the lower bound of sensitivity 
            of the current channel
        3. All values in the existing data that are above this threshold in 
            the current sweep are replaced by the corresponding data from the current sweep
    
    Arguments:
        path: filename of the data file

    Returns:
        array: wavelength
        array: Stitched intensity data
        array[array]: Raw intensity data
        list[tuple]: Channel range values
    '''
    with open(path, 'r') as fp:
        channel_ranges = get_ranges_from_header(fp)

    skiprows = 0
    with open(path, 'r') as fp:
        for ind, line in enumerate(fp):
            if line.strip().startswith('--RAW DATA START--'):
                skiprows = ind + 1

    df = pd.read_csv(path, skiprows=skiprows)
    df = df.set_index('Wavelength(nm)')

    channel = df.columns[-1].split('_')[3].upper()
    assert channel.startswith('CH')

    cols = df.columns[-len(channel_ranges[channel]):][::-1]
    assert all([ col.startswith('Raw') for col in cols ]), 'misread the channel ranges'
    sweeps = df[cols].to_numpy().T
    sweep_ranges = channel_ranges[channel][::-1]
    stitched = stitch_sweeps(sweeps, sweep_ranges)
    
    return df.index.to_numpy(), stitched, sweeps, sweep_ranges
