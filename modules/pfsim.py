import sys
import os
import csv
import numpy as np
import random
import warnings
from math import sqrt, cos, log, pi

sys.path.append(
    r"C:\Program Files\DIgSILENT\PowerFactory 2020 SP2A\Python\3.8")
import powerfactory as pf


class PowerFactorySim(object):

    def __init__(self, folder_name='', project_name='Project', study_case_name='Study Case'):
        # start powerfactory
        self.app = pf.GetApplicationExt()
        # activate project
        self.project = self.app.ActivateProject(os.path.join(folder_name, project_name))
        # activate study case
        study_case_folder = self.app.GetProjectFolder('study')
        study_case = study_case_folder.GetContents(
            study_case_name + '.IntCase')[0]
        self.study_case = study_case
        self.study_case.Activate

    def return_objects(self, element,
                       print_list=True):

        """
        Function to return objects of interest within the active study case, useful for sense checking
        Arguments:
            element - object/element of interest
            print_list - False if only the number of unique elements is required
        """

        object = self.app.GetCalcRelevantObjects(element)
        print("Number of " + str(element) + " is: " + str(len(object)))
        active = []
        total_active_cap = []
        reactive = []
        gen_counter = 0
        if print_list:
            for i in object:
                if element == '*.ElmLod':
                    print(i.loc_name, "Active Power: " + str(i.plini), "Reactive Power: " + str(i.qlini))
                    active.append(i.plini)
                    reactive.append(i.qlini)
                elif element == '*.ElmSym':
                    number_gen_plus_motors = len(object)
                    if i.i_mot == 0:
                        gen_counter += 1
                        print(i.loc_name, "Dispatch Active Power: " + str(round(i.pgini, 3)),
                              "Dispatch Reactive Power: " + str(round(i.qgini, 3)),
                              "Active Power op limits Min: " + str(round(i.Pmin_uc, 3)) + " Max: " + str(
                                  round(i.Pmax_uc, 3)))
                        total_active_cap.append(i.Pmax_uc)
                        active.append(i.pgini)
                        reactive.append(i.qgini)
                else:
                    print(i.loc_name)
        if element == '*.ElmLod':
            print("Total active load power: ", sum(active))
            print("Total reactive load power: ", + sum(reactive))

        if element == '*.ElmSym':
            print("Total active dispatch power: ", sum(active))
            print("Total reactive dispatch power: ", + sum(reactive))
            print("Total system active power capacity: ", + sum(total_active_cap))
            print("Number of generators is: " + str(gen_counter) + "\nNumber of motors is: " + str(
                number_gen_plus_motors - gen_counter))

    def set_loads(self, mean=100,
                  standard_deviation=20, power_factor=95):

        """
        Function to set all loads in the system, drawn from a distribution.
        Arguments:
            mean - of the distribution to be sampled
            standard_deviation - spread of sampling from mean
            power_factor - if constant power factor required, set argument
        """

        # collect all load elements
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        # create keys for loads dictionary form all names of loads
        keys = []
        for key in loads:
            keys.append(key.loc_name)
        # create values for keys drawn from distribution
        values = []
        for _ in range(len(keys)):
            values.append(round(np.random.normal(mean, standard_deviation), 2))
        # create p and q loads dictionary for fixed power factor
        p_loads = {k: v for k, v in zip(keys, values)}
        q_loads = {k: v for k, v in zip(keys, [round(i * (1 - power_factor), 2) for i in values])}
        # set active and reactive loads
        for load in loads:
            load.plini = p_loads[load.loc_name]
            load.qlini = q_loads[load.loc_name]

    def reset_loads_to_nominal(self):

        """
        Function to reset all active and reactive loads in the system to their
        nominal values. Nominal loads read from directory
        """

        path = r"C:\Users\olive\PycharmProjects\power_factory\nominal_loads"

        # read nominal active loads from directory
        active_reader = csv.reader(open(path + r'\active_nominal.csv', 'r'))
        active_loads = {}
        for k, v in active_reader:
            active_loads[k] = float(v)
        # read nominal reactive loads from dictionary
        reactive_reader = csv.reader(open(path + r'\reactive_nominal.csv', 'r'))
        reactive_loads = {}
        for k, v in reactive_reader:
            reactive_loads[k] = float(v)
        # collect all load elements
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        # loop through loads and reset values for active and reactive power
        for load in loads:
            load.plini = active_loads[load.loc_name]
            load.qlini = reactive_loads[load.loc_name]

    def get_loads_from_file(self):

        """
        Function to return loads that were stored in a csv file locally
        """

        path = r"C:\Users\olive\PycharmProjects\power_factory\nominal_loads"

        # read nominal active loads from directory
        active_reader = csv.reader(open(path + r'\active_nominal.csv', 'r'))
        active_loads = {}
        for k, v in active_reader:
            active_loads[k] = float(v)
        # read nominal reactive loads from dictionary
        reactive_reader = csv.reader(open(path + r'\reactive_nominal.csv', 'r'))
        reactive_loads = {}
        for k, v in reactive_reader:
            reactive_loads[k] = float(v)

        return active_loads, reactive_loads

    def set_all_loads_pq(self, p_load, q_load, scale_factor=None):

        """
        Function to set all loads in the system. If loads need to be scaled from 
        nominal system values set scale_factor
        """

        loads = self.app.GetCalcRelevantObjects('*.ElmLod')

        if scale_factor is not None:
            for key in p_load:
                p_load[key] *= scale_factor
            for key in q_load:
                q_load[key] *= scale_factor
            for key in p_load:
                p_load[key] = int(p_load[key])
            for key in q_load:
                q_load[key] = int(q_load[key])

        for load in loads:
            load.plini = p_load[load.loc_name]
            load.qlini = q_load[load.loc_name]

    def get_all_loads_pq(self):

        """
        Function to return all system loads under current state
        """

        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        p_base = {}
        q_base = {}

        for load in loads:
            p_base[load.loc_name] = load.plini
            q_base[load.loc_name] = load.qlini

        return p_base, q_base

    def set_dispatch(self):

        """
        Function to set total system dispatch to total system load. Dispatch will be 
        equal across all machines
        """

        generators = self.app.GetCalcRelevantObjects('*.ElmSym')
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        # create keys for generator dictionary form all names of generators
        keys = []
        values = []
        for key in generators:
            keys.append(key.loc_name)
        active_loads = []
        for load in loads:
            active_loads.append(load.plini)
        for _ in range(len(keys)):
            values.append((sum(active_loads) / len(keys)))
        p_dispatch = {k: v for k, v in zip(keys, values)}
        # set dispatch
        for gen in generators:
            gen.pgini = p_dispatch[gen.loc_name]

    def prepare_dynamic_sim(self, monitored_variables,
                            sim_type='rms', start_time=0.0,
                            step_size=0.01, end_time=10.0):

        """
        Prepares conditions for transient simulation and executes load flow
        Arguments:
            monitored_variables - dictionary {element: variable_1,...,n}
            sim_type - rms or emt
            times - start, step and end
        """
        # get results file
        self.res = self.app.GetFromStudyCase('*.ElmRes')
        for elm_name, var_names in monitored_variables.items():
            # get all network elements that match 'elm_name'
            elements = self.app.GetCalcRelevantObjects(elm_name)
            # select variables to monitor for each element
            for element in elements:
                self.res.AddVars(element, *var_names)
        # get initial conditions and time domain sim.objects
        self.inc = self.app.GetFromStudyCase('ComInc')
        self.sim = self.app.GetFromStudyCase('ComSim')
        # set simulation type.. ie either 'rms' or 'ins' (for emt)
        self.inc.iopt_sim = sim_type
        # set start time, step sizeu and end time
        self.inc.tstart = start_time
        self.inc.dtgrd = step_size
        self.sim.tstop = end_time
        # set initial condtions
        self.inc.Execute()

    def enable_short_circuits(self):
        """
        since by default lines are unavailable, function to change all to available
        """
        lines = self.app.GetCalcRelevantObjects('*.ElmLne')
        for line in lines:
            if line.ishclne == 0:
                line.ishclne = 1
        print("All lines available for short circuit")

    def create_short_circuit(self, target_name,
                             time, fault_type,
                             duration=None, name='sc'):

        """
        Creates short circuit event in the events folder
        if duration is specified, a clearing event will also be created
        Arguments:
            target_name - name of line
            time - start time of short circuit
            duration - duration before clearing
            fault_type - 0 for three phase, fault codes can be found in PF
        """

        # get element where the short circuit will be made
        target = self.app.GetCalcRelevantObjects(target_name)[0]
        # get events folder from active study case
        evt_folder = self.app.GetFromStudyCase('IntEvt')
        # create an empty event of type EvtShc
        evt_folder.CreateObject('EvtShc', name)
        # get the newly created event
        sc = evt_folder.GetContents(name + '.EvtShc')[0]
        # set time, target and type of short circuit (ie single or three phase)
        sc.time = time
        sc.p_target = target
        sc.i_shc = fault_type
        # set clearing event if required
        if duration is not None:
            # create an empty event for the clearing event
            evt_folder.CreateObject('EvtShc', name + '_clear')
            # get the new event
            scc = evt_folder.GetContents(name + '_clear' + '.EvtShc')[0]
            scc.time = time + duration
            scc.p_target = target
            scc.i_shc = 4

    def delete_short_circuit(self, name='sc'):

        """
        For running multiple events in a loop, old events need to be deleted
        and new ones re-initialised. This function deletes all events in
        events folder assuming they were created from the method in this class
        """
        # get the events folder
        evt_folder = self.app.GetFromStudyCase('IntEvt')
        # find short circuit events and clear if they exist
        sc = evt_folder.GetContents(name + '.EvtShc')
        scc = evt_folder.GetContents(name + '_clear' + '.EvtShc')
        if sc:
            sc[0].Delete()
        if scc:
            scc[0].Delete()

    def run_dynamic_sim(self):
        return bool(self.sim.Execute())

    def get_voltage_scan(self):

        """
        Function to return voltage scan results from previous RMS simulation
        """

        scan_folder = self.app.GetFromStudyCase('IntScn')
        fault = scan_folder.GetContents('*.ScnFrt')[0]
        num_of_violations = fault.GetNumberOfViolations()
        time_stamp = []
        for i in range(1, num_of_violations+1):
            time_stamp.append(fault.GetViolationTime(i))
        return num_of_violations, time_stamp

    def get_frequency_scan(self):

        """
        Function to return frequency scan results from previous RMS simulation
        """

        scan_folder = self.app.GetFromStudyCase('IntScn')
        fault = scan_folder.GetContents('*.ScnFreq')[0]
        num_of_violations = fault.GetNumberOfViolations()
        time_stamp = []
        for i in range(1, num_of_violations+1):
            time_stamp.append(fault.GetViolationTime(i))
        return num_of_violations, time_stamp

    def calculate_system_inertia(self, study_case_name):

        """
        Function to return the total system inertia for a specific operating condition 
        """

        #if i.i_mot == 0:
        H_i = []
        S_bi = []
        S_b_wind = []

        generators = self.app.GetCalcRelevantObjects('*.TypSym')
        wind_generators = self.app.GetCalcRelevantObjects('*.ElmGenstat')
        for gen in generators:
            if "SC" not in gen.loc_name:
                H_i.append(gen.h)
                S_bi.append(gen.sgn)
        if study_case_name == 'test_case_no_wind':
            return (sum(np.multiply(H_i, S_bi)))/(sum(S_bi))
        else:
            for wind in wind_generators:
                S_b_wind.append(wind.sgn*wind.ngnum)
            return sum(np.multiply(H_i, S_bi))/(sum(S_bi)+sum(S_b_wind))

    def calculate_spinning_reserve(self, study_case_name):

        """
        Function to return the total system spinning reserve for a specific operating condition 
        """

        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        generators = self.app.GetCalcRelevantObjects('*.ElmSym')
        wind_generators = self.app.GetCalcRelevantObjects('*.ElmGenstat')
        p_base = []
        spinning_base = []
        wind_dispatch = []

        for load in loads:
            p_base.append(load.plini)
        if study_case_name == 'test_case_no_wind':
            for gen in generators:
                if gen.i_mot == 0:
                    spinning_base.append(gen.Pmax_uc)
            return(sum(spinning_base))-(sum(p_base))
        else:
            for gen in generators:
                if gen.i_mot == 0:
                    spinning_base.append(gen.Pmax_uc)
            for wind in wind_generators:
                wind_dispatch.append(wind.pgini*wind.ngnum)
            x = sum(p_base) - sum(wind_dispatch)
            return sum(spinning_base) - x

    def get_dynamic_results(self ,elm_name=None, var_name=None, offset=10000, time_step=False):

        """
        Simulation has been executed by run_dynamic_sim. This function
        gets results assuming the variables were called when setting up the simulation.
        Arguments:
             elm_name - element name (ie bus or line)
             var_name - name of variable
             offset - from what time step to truncate data, e.g if pre contingency data is not required
        returns:
            time stamp and required variables as lists
        """
        # read the results and time steps and store them as lists
        time = []
        var_values = []
        # load results from file
        self.app.ResLoadData(self.res)
        # get number of rows (time steps) in the results file
        n_rows = self.app.ResGetValueCount(self.res, 0)
        # get network element of interest
        if time_step:
            for i in range(0, n_rows-offset):
                time.append(self.app.ResGetData(self.res, i+offset, -1)[1])
            return time
        else:
            element = self.app.GetCalcRelevantObjects(elm_name)[0]
            # find column in results file which holds the result of interest
            col_index = self.app.ResGetIndex(
                self.res, element, var_name)
            for i in range(0, n_rows-offset):
                var_values.append(self.app.ResGetData(self.res, i+offset, col_index)[1])
            return var_values


    def prepare_loadflow(self, ldf_mode='balanced'):

        """
        Function to prepare conditions for load flow calculation
        """

        modes = {'balanced': 0,
                 'unbalanced': 1,
                 'dc': 2}
        # get load flow object
        self.ldf = self.app.GetFromStudyCase('ComLdf')
        # set load flow mode
        self.ldf.iopt_net = modes[ldf_mode]

    def run_loadflow(self):
        return bool(self.ldf.Execute())

    def get_bus_voltages(self):

        """
        Function to return bus voltages following load flow calculation
        """

        voltages = {}
        # collect all bus elements for voltages
        buses = self.app.GetCalcRelevantObjects('*.ElmTerm')
        # store as dictionary
        for bus in buses:
            if bus.iUsage==0:
                voltages[bus.loc_name] = bus.GetAttribute('m:u')

        return voltages

class MontecarloLoadFlow(PowerFactorySim):

    """
    Class to run a monte carlo load flow. Credit:

    {Probabilistic Power Flow Module for PowerFactory DIgSILENT,
    Saeed Teimourzadeh, Behnam Mohammadi-Ivatloo}
    """

    def gen_normal_loads_pq(self, p_total, q_total, p_base, q_base, std_dev=0.1):
        #generate two random number from uniform distribution
        rand1 = random.uniform(0,1)
        rand2 = random.uniform(0,1)
        #sample loads from a normal distribution
        p_total_rand = p_total*(1 + std_dev*sqrt(-2*log(rand1))*cos(2*pi*rand2))
        q_total_rand = q_total * (1 + std_dev * sqrt(-2 * log(rand1)) * cos(2 * pi * rand2))
        loads = self.app.GetCalcRelevantObjects('*.ElmLod')
        #store normally distributed load values as dict
        p_normal = {}
        q_normal = {}
        for load in loads:
            p_normal[load.loc_name] = (p_base[load.loc_name]/p_total*p_total_rand)
            q_normal[load.loc_name] = (q_base[load.loc_name]/q_total*q_total_rand)

        return p_normal, q_normal

    def monte_carlo_loadflow(self, n_samples, std_dev, max_attempts=10):
        self.prepare_loadflow()
        #get initial loads
        p_base, q_base = self.get_all_loads_pq()
        #calculate total base system load
        p_total = sum(p_base.values())
        q_total = sum(q_base.values())

        #sample load flow
        for sample in range(n_samples):
            #re-attempt load flow in case of non-convergence
            for attempt in range(max_attempts):
                #generate random normally distributed loads
                p_normal, q_normal = self.gen_normal_loads_pq(
                    p_total, q_total, p_base, q_base, std_dev=std_dev
                )
                #set system loads to random loads
                self.set_all_loads_pq(p_normal, q_normal)
                #run load flow
                failed = self.run_loadflow()
                if failed:
                    warnings.warn(
                        "sample " +str(sample)
                        + " did not converge, re-attempt "
                        + str(attempt + 1) + " out of "
                        + str(max_attempts)
                    )
                else:
                    break

            yield self.get_bus_voltages()

        #restore system to base loads
        self.set_all_loads_pq(p_base, q_base)




