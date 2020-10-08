from pfsim import PowerFactorySim
import numpy as np
import pandas as pd
import random

FOLDER_NAME = ''
PROJECT_NAME = 'test_scenarios_118'
STUDY_CASE_NAME = 'test_case_no_wind'
MONITORED_VARIABLES = {
    '*.ElmSym': ['s:outofstep']
}

# activate both project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

MIN_CLEARING_TIME=0.05
MAX_CLEARING_TIME=3.0
STEP=0.05
NUMBER_OF_SAMPLES = 30
SCENARIO = "0%WT" #for easy labeling in csv
LOADS = "nominal" #for easy labeling in csv
pole_slip = False
header = ["Line", "Clearing time", "Scenario", "Load"]
clear_time = np.empty([1,2])

clearing_times = np.arange(MIN_CLEARING_TIME, MAX_CLEARING_TIME+STEP, STEP)

# enable short circuits on all lines
sim.enable_short_circuits()

#get lines
lines = sim.app.GetCalcRelevantObjects('*.ElmLne')

for line in random.sample(lines,NUMBER_OF_SAMPLES+1):
    for clearing in clearing_times:
        # delete any previous short circuit event before starting next
        sim.delete_short_circuit()
        # create short circuit on each line and increase clearing time in steps
        sim.create_short_circuit(
            target_name=line.loc_name + '.ElmLne',
            time=1,
            duration=clearing,
            fault_type=0,
            name='sc')
        sim.prepare_dynamic_sim(
            monitored_variables=MONITORED_VARIABLES,
            sim_type='rms',
            start_time=0.0,
            step_size=0.01,
            end_time=10)

        sim.run_dynamic_sim()

        # get results no wind - FOR CLEANER CODE USE DICTIONARY
        t, G1 = sim.get_dynamic_results(
            'Gen 10.ElmSym', 's:outofstep')
        _, G2 = sim.get_dynamic_results(
            'Gen 12.ElmSym', 's:outofstep')
        _, G3 = sim.get_dynamic_results(
            'Gen 25.ElmSym', 's:outofstep')
        _, G4 = sim.get_dynamic_results(
            'Gen 26.ElmSym', 's:outofstep')
        _, G5 = sim.get_dynamic_results(
            'Gen 31.ElmSym', 's:outofstep')
        _, G6 = sim.get_dynamic_results(
            'Gen 46.ElmSym', 's:outofstep')
        _, G7 = sim.get_dynamic_results(
            'Gen 49.ElmSym', 's:outofstep')
        _, G8 = sim.get_dynamic_results(
            'Gen 54.ElmSym', 's:outofstep')
        _, G9 = sim.get_dynamic_results(
            'Gen 59.ElmSym', 's:outofstep')
        _, G10 = sim.get_dynamic_results(
            'Gen 61.ElmSym', 's:outofstep')
        _, G11 = sim.get_dynamic_results(
            'Gen 65.ElmSym', 's:outofstep')
        _, G12 = sim.get_dynamic_results(
            'Gen 66.ElmSym', 's:outofstep')
        _, G13 = sim.get_dynamic_results(
            'Gen 69.ElmSym', 's:outofstep')
        _, G14 = sim.get_dynamic_results(
            'Gen 80.ElmSym', 's:outofstep')
        _, G15 = sim.get_dynamic_results(
            'Gen 87.ElmSym', 's:outofstep')
        _, G16 = sim.get_dynamic_results(
            'Gen 89.ElmSym', 's:outofstep')
        _, G17 = sim.get_dynamic_results(
            'Gen 100.ElmSym', 's:outofstep')
        _, G18 = sim.get_dynamic_results(
            'Gen 103.ElmSym', 's:outofstep')
        _, G19 = sim.get_dynamic_results(
            'Gen 111.ElmSym', 's:outofstep')

        for i in zip(G1, G2, G3, G4, G5, G6,
                     G7, G8, G9, G10, G11, G12,
                     G13, G14, G15, G16, G17, G18, G19):
            if 1 in i:
                print("**Critical clearing time for " +str(line.loc_name) +" is " +str(clearing))
                clear_time = [str(line.loc_name), str(clearing), SCENARIO, LOADS]
                header = np.vstack((header, clear_time))
                pole_slip = True
                break
            elif clearing == MAX_CLEARING_TIME and 1 not in i:
                print("*Critical Clearing time for " + str(line.loc_name) + " is greater than 3 seconds")
                clear_time = [str(line.loc_name), "greater 3 seconds", SCENARIO, LOADS]
                header = np.vstack((header, clear_time))
                break

        if pole_slip:
            pole_slip = False
            break

        print("RMS for " +str(line.loc_name) +" finished with clearing time of " +str(clearing))

data = pd.DataFrame(header)
path = r"C:\Users\olive\PycharmProjects\power_factory\CCT"
data.to_csv(path+r'\CCT'+'_'+SCENARIO+'_'+LOADS)
