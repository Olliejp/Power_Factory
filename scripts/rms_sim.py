from pfsim import PowerFactorySim
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import time

FOLDER_NAME = ''
PROJECT_NAME = 'test_scenarios_118(3)'
STUDY_CASE_NAME = 'test_case_26%_wind'
MONITORED_VARIABLES = {
    '*.ElmSym': ['c:firel','s:outofstep', 'n:u:bus1', 'm:I:bus1', 'm:phiui:bus1']
}

# activate both project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

LOAD_RANGE = [0.8, 0.9, 1, 1.1, 1.2]
CLEARING_TIMES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
LINES = sim.app.GetCalcRelevantObjects('*.ElmLne')
GENERATORS = sim.app.GetCalcRelevantObjects('*.ElmSym')
inertia = sim.calculate_system_inertia(STUDY_CASE_NAME)
NUMBER_OF_SAMPLES = 50
counter = 1
end = len(LOAD_RANGE) * len(CLEARING_TIMES) * NUMBER_OF_SAMPLES

sim.reset_loads_to_nominal()

# enable short circuits on all lines
sim.enable_short_circuits()

tick = time.time()

for line in random.sample(LINES, NUMBER_OF_SAMPLES):
    for load in LOAD_RANGE:
        # scale loads
        active, reactive = sim.get_loads_from_file()
        sim.set_all_loads_pq(active, reactive, load, scale=True)
        for clear_time in CLEARING_TIMES:
            # delete any previous short circuit event before starting next
            sim.delete_short_circuit()
            # create short circuit on each line
            sim.create_short_circuit(
                target_name=line.loc_name + '.ElmLne',
                time=0,
                duration=clear_time,
                fault_type=0,
                name='sc')
            sim.prepare_dynamic_sim(
                monitored_variables=MONITORED_VARIABLES,
                sim_type='rms',
                start_time=-10.0,
                step_size=0.001,
                end_time=5)

            sim.run_dynamic_sim()

            # create empty dictionaries for each variable of interest
            rot_angle = {}
            volt_mag = {}
            current_mag = {}
            angle = {}
            out_step = {}

            # get time step
            t = {"time": sim.get_dynamic_results(time_step=True)}

            # get rotor angles
            for gen in GENERATORS:
                if gen.i_mot == 0:
                    rot_angle['rotor_angle ' + gen.loc_name] = sim.get_dynamic_results(gen.loc_name + '.ElmSym',
                                                                                       'c:firel')
            for gen in GENERATORS:
                if gen.i_mot == 0:
                    volt_mag['volt_mag ' + gen.loc_name] = sim.get_dynamic_results(gen.loc_name + '.ElmSym',
                                                                                       'n:u:bus1')

            for gen in GENERATORS:
                if gen.i_mot == 0:
                    current_mag['current_mag ' + gen.loc_name] = sim.get_dynamic_results(gen.loc_name + '.ElmSym',
                                                                                       'm:I:bus1')
            for gen in GENERATORS:
                if gen.i_mot == 0:
                    angle['phase_angle ' + gen.loc_name] = sim.get_dynamic_results(gen.loc_name + '.ElmSym',
                                                                                       'm:phiui:bus1')

            for gen in GENERATORS:
                if gen.i_mot == 0:
                    out_step['out_step ' + gen.loc_name] = sim.get_dynamic_results(gen.loc_name + '.ElmSym',
                                                                                       's:outofstep')

            # concat all dictionaries
            df = {}
            for dictionary in [t, volt_mag, current_mag, angle, rot_angle, out_step]:
                df.update(dictionary)

            # writing dictionary to pandas dataframe
            df = pd.DataFrame.from_dict(df)

            # plt.plot(df['time'], df['rotor_angle Gen 12'])
            # plt.plot(df['time'], df['rotor_angle Gen 10'])
            # plt.plot(df['time'], df['rotor_angle Gen 25'])
            # plt.xlabel('time [s]')
            # plt.ylabel('rotor angle [deg]')
            # plt.show()

            spinning_reserve = sim.calculate_spinning_reserve(STUDY_CASE_NAME)

            # write dataframe to csv
            path = r"C:\Users\olive\RMS_26_line_103-105_OOS"
            df.to_csv(
                path + r'\line_103-105' + '_' + str(line.loc_name) + '_' + 'clearing-' + str(
                    clear_time) + '_' + 'load-' + str(
                    load) + '_' + 'inertia-' + str(
                    round(inertia, 2)) + '_' + 'spinreserve-' + str(round(spinning_reserve, 2)) + '_' + '.csv')

            print("Iteration: " + str(counter) + " of " + str(end) + " done")
            print("Time elapsed: " + str((time.time() - tick) / 60) + " minutes")
            counter += 1
            # p, q = sim.get_all_loads_pq()
            # print(p, "bla")

# reset to base p and q loads
sim.reset_loads_to_nominal()
print("script ended")
