from pfsim import PowerFactorySim

FOLDER_NAME = ''
PROJECT_NAME = 'test_scenarios_118'
STUDY_CASE_NAME = 'test_case_no_wind'

buses = '*.ElmTerm'
lines = '*.ElmLne'
loads = '*.ElmLod'
switches = '*.staSwitch'
generators = '*.ElmSym'
#The object names in powefactory

objects = [lines, loads, generators]
#for any objects/elements in the system you want to inspect, just add to this array

# activate both project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

for object in objects:
    sim.return_objects(object, print_list=True)
#for full list of all elements change to True