import numpy as np
import pandas as pd
import os
import re
import os

from expy import shared


def readSetting(filepath='setting.txt'):
    '''
    Read the setting file and put the items into a dict.
    If the 'timingSet' is in the file, create a "timing" in the dict to put the timing parameter.

    Parameters
    ----------
    filepath：str (default:'setting.txt')
        The path of the setting file.

    Returns
    -------
    setting: dict
        todo.
    '''

    setting = dict()
    with open(filepath) as f:
        try:
            for s in re.compile(r'[-]{2,}').split(f.read()):
                if len(s) > 0:
                    if s[0] == '\n':
                        s = s[1:]
                    if s[-1] == '\n':
                        s = s[:-1]

                    name, *content = s.split('\n')
                    setting[name[1:-1]] = content

            if 'timingSet' in setting:
                setting['timing'] = dict()
                # Set timing of each phase
                for dur in setting['timingSet']:
                    k, v = dur.replace(' ', '').split(':')
                    if '-' in v:
                        limit = v.split('-')
                        setting['timing'][k] = [int(limit[0]), int(limit[1])]
                    else:
                        setting['timing'][k] = int(v)
        except:
            raise ValueError('Please check your setting.txt!')

    return setting

def readStimuli(filepath, blockID=None, sheetname=0):
    '''
    Get the stimuli from a csv/excel file

    Parameters
    ----------
    filepath：str
        The path of the data file
    blockID: int
    sheetname: int

    Returns
    -------
    stimuli: pandas.DataFrame
        The selected stimuli data
    '''
    if filepath.split('.')[-1] == 'csv':
        stimuli = pd.read_csv(filepath, sep=',', encoding='gbk')
    elif filepath.split('.')[-1] in ['xls', 'xlsx']:
        stimuli = pd.read_excel(filepath, sep=',', sheetname=0)
    else:
        raise ValueError('Only support csv and Excel file')
    if blockID:
        # stimuli = stimuli[stimuli[blockID[0]]==blockID[1]]
        stimuli = stimuli[stimuli[blockID[0]] == blockID[1]].sample(n=4)
    stimuli.index = range(len(stimuli))
    return stimuli

def readDir(dirpath, shuffle=True):
    '''
    List the files in a directory

    Parameters
    ----------
    dirpath：str
        The path of target directory
    shuffle: True, False(default)
        Whether shuffle the list or not 

    Return
    ---------
    files: list
        The filename list
    '''
    files = [dirpath + f for f in os.listdir(dirpath)]
    if shuffle:
        np.random.shuffle(files)
    return files

def saveResult(blockID, resp, columns=['respKey', 'RT'], stim=None, stim_columns=None):
    '''
    Save experiment result to a file named {subjID}_{blockID}_result.csv.
    If stim is not None, the stimuli data would attach to the response result.

    Parameters
    ----------
    blockID：int
        The ID of current block
    resp：list
        The list of response data
    columns: list
        The names of response data columns
    stim: pandas.DataFrame, or list
        The data of stimuli
    stim_columns: None, or list
        The names of stimuli data columns

    Return
    ---------
    None
    '''   
    if not os.path.exists('result'):
        os.mkdir('result')
    result = pd.DataFrame(resp, columns=columns)
    if not stim is None:
        if type(stim) is list:
            stim = pd.DataFrame(stim, columns=stim_columns)
        result = stim.join(result)

    result.to_csv('result\\' + shared.subj + '_' +
                  str(blockID) + '_result.csv', index=None)

def sendTrigger(data, mode='P'):
    '''
    Send trigger

    Parameters
    ----------
    data: int, or str
        The trigger content
    mode: 'P', or 'S'
        The port type: 'P' refers to parallel port, 'S' refers to serial port

    Return
    ---------
    None
    '''
    try:
        if mode == 'P':
            shared.Objdll.Out32(shared.setting['port'], 0)
        elif mode == 'S':
            # send a string which might change
            shared.ser.write(bytes(data, encoding='utf-8'))
            # shared.ser.write(b'something') # send a string directly

            # n=int('0b00010001',2)
            # shared.ser.write(n.to_bytes((n.bit_length()+7)//8, 'big')) # send
            # a binary code
        else:
            raise ValueError('Only support "S" or "P" (serial/parallel) mode!')
    except:
        print('The port might be closed.')
