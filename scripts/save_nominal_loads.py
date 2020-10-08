from pfsim import PowerFactorySim
import csv

FOLDER_NAME = ''
PROJECT_NAME = 'test_scenarios_118'
STUDY_CASE_NAME = 'test_case_no_wind'

buses = '*.ElmTerm'
lines = '*.ElmLne'
loads = '*.ElmLod'
switches = '*.staSwitch'
generators = '*.ElmSym'
#The object names in powefactory

# activate both project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

loads = sim.app.GetCalcRelevantObjects(loads)

keys = []
p_load = []
q_load = []

for key in loads:
    keys.append(key.loc_name)

for value in loads:
    p_load.append(value.plini)

for value in loads:
    q_load.append(value.qlini)

nominal_active = {k: v for k, v in zip(keys, p_load)}
nominal_reactive = {k: v for k, v in zip(keys, q_load)}

path = r"C:\Users\olive\PycharmProjects\power_factory\nominal_loads"

with open(path + r'\active_nominal.csv', 'w') as f:
    for key in nominal_active.keys():
        f.write("%s,%s\n"%(key,nominal_active[key]))

with open(path + r'\reactive_nominal.csv', 'w') as f:
    for key in nominal_reactive.keys():
        f.write("%s,%s\n"%(key,nominal_reactive[key]))


#reader = csv.reader(open(path + r'\active_nominal.csv', 'r'))
# d = {}
# for k, v in reader:
#     d[k] = v
#
# reader = csv.reader(open(path + r'\reactive_nominal.csv', 'r'))
# p = {}
# for k, v in reader:
#     p[k] = v



