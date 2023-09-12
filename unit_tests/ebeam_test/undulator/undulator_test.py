"""Test of the demo file demos/ebeam/undulator.py"""

import os
import sys
from copy import copy
import time

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_RES_DIR = FILE_DIR + '/ref_results/'

from unit_tests.params import *
from undulator_conf import *


def test_lattice_transfer_map(lattice, parameter=None, update_ref_values=False):
    """R maxtrix test"""

    r_matrix = lattice[0].transfer_maps(0.0)[1]
    
    if update_ref_values:
        return numpy2json(r_matrix)
    
    r_matrix_ref = json2numpy(json_read(REF_RES_DIR + sys._getframe().f_code.co_name + '.json'))
    
    result = check_matrix(r_matrix, r_matrix_ref, TOL, assert_info=' r_matrix - ')
    assert check_result(result)


@pytest.mark.parametrize('parameter', [0, 1, 2, 3, 4])
def test_R_matrix_diff_roll_off(lattice, parameter, update_ref_values=False):
    """R maxtrix test for undulators with different roll off parameters """
    K = 4.
    if parameter == 0:
        u = Undulator(lperiod=0.04, nperiods=100, Kx=K)
    elif parameter == 1:
        u = Undulator(lperiod=0.04, nperiods=100, Ky=K)
    elif parameter == 2:
        u = Undulator(lperiod=0.04, nperiods=100, Ky=K * np.sqrt(0.5), Kx=K * np.sqrt(0.5))
    elif parameter == 3:
        u = Undulator(lperiod=0.04, nperiods=100, Ky=K * np.sqrt(-0.5 + 0j), Kx=K * np.sqrt(1.5))
    else:
        u = Undulator(lperiod=0.04, nperiods=100, Ky=0, Kx=0)
    r_matrix = u.R(1)[0]

    if update_ref_values:
        return numpy2json(r_matrix)

    r_matrix_ref = json2numpy(json_read(REF_RES_DIR + sys._getframe().f_code.co_name + str(parameter) + '.json'))

    result = check_matrix(r_matrix, r_matrix_ref, TOL, assert_info=' r_matrix - ')
    assert check_result(result)


def test_twiss(lattice, parameter=None, update_ref_values=False):
    """Twiss parameters calculation function test"""

    beam = Beam()
    beam.E = 2.5
    beam.I = 0.1

    tw0 = Twiss(beam)
    tws = twiss(lattice[0], tw0, nPoints=100)
    
    tws = obj2dict(tws)
    
    if update_ref_values:
        return tws

    tws_ref = json_read(REF_RES_DIR + sys._getframe().f_code.co_name + '.json')
    
    result = check_dict(tws, tws_ref, TOL, 'absolute', assert_info=' tws - ')
    assert check_result(result)


@pytest.mark.parametrize('parameter', [0, 1])
def test_tracking_step(lattice, parameter, update_ref_values=False):
    """Tracking step function test
    :parameter=0 - tracking with {'global': TransferMap, 'Undulator': UndulatorTestTM}
    :parameter=1 - tracking with default {'global': TransferMap}
    """
    
    p = Particle(x=0.001, y=0.002)
    p.E = 2.5

    navi = Navigator(lattice[parameter])
    dz = 0.01

    P1 = []
    for iii in range(int(lattice[parameter].totalLen/dz)):
        tracking_step(lattice[parameter], [p], dz=dz, navi=navi)
        P1.append(copy.copy(p))

    tracking_step(lattice[parameter], p, dz=dz, navi=navi)
    
    P1 = obj2dict(P1)
    
    if update_ref_values:
        return P1

    p_ref = json_read(REF_RES_DIR + sys._getframe().f_code.co_name + str(parameter) +'.json')

    #assert check_dict(P1, p_ref, TOL)
    result = check_dict(P1, p_ref, TOL, assert_info=' P1 - ')
    assert check_result(result)


def setup_module(module):

    f = open(pytest.TEST_RESULTS_FILE, 'a')
    f.write('### DBA START ###\n\n')
    f.close()


def teardown_module(module):

    f = open(pytest.TEST_RESULTS_FILE, 'a')
    f.write('### DBA END ###\n\n\n')
    f.close()


def setup_function(function):
    
    f = open(pytest.TEST_RESULTS_FILE, 'a')
    f.write(function.__name__)
    f.close()

    pytest.t_start = time.time()


def teardown_function(function):
    f = open(pytest.TEST_RESULTS_FILE, 'a')
    f.write(' execution time is ' + '{:.3f}'.format(time.time() - pytest.t_start) + ' sec\n\n')
    f.close()


@pytest.mark.update
def test_update_ref_values(lattice, cmdopt):
    
    update_functions = []
    update_functions.append('test_lattice_transfer_map')
    update_functions.append('test_twiss')
    update_functions.append('test_R_matrix_diff_roll_off')
    update_functions.append('test_tracking_step')

    
    update_function_parameters = {}
    update_function_parameters['test_R_matrix_diff_roll_off'] = [0, 1, 2, 3, 4]
    update_function_parameters['test_tracking_step'] = [0, 1]
    
    parameter = update_function_parameters[cmdopt] if cmdopt in update_function_parameters.keys() else ['']

    if cmdopt in update_functions:
        for p in parameter:
            result = eval(cmdopt)(lattice, p, True)
        
            if os.path.isfile(REF_RES_DIR + cmdopt + str(p) + '.json'):
                os.rename(REF_RES_DIR + cmdopt + str(p) + '.json', REF_RES_DIR + cmdopt + str(p) + '.old')
            
            json_save(result, REF_RES_DIR + cmdopt + str(p) + '.json')
