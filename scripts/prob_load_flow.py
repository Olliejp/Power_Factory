import csv
from pfsim import MontecarloLoadFlow

FOLDER_NAME = ''
PROJECT_NAME = 'test_scenarios_118'
STUDY_CASE_NAME = 'test_case_no_wind'

N_SAMPLES = 1000
STD_DEV = 0.1

# activate both project and study case
sim = MontecarloLoadFlow(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

#create montecarlo load flow iterable object
mcldf = sim.monte_carlo_loadflow(N_SAMPLES, STD_DEV)
# #create csv file to store voltages
path = r"C:\Users\olive\PycharmProjects\power_factory\load_flow"
with open(path + r'\res_prob_lf_1000_std0.1.csv', 'w', newline='') as csvfile:
 #iterate over mcldf object to get voltages
 for row_index, voltages in enumerate(mcldf):
     #write file header (bus names)
     if row_index == 0:
         csvwriter = csv.DictWriter(csvfile, voltages.keys())
         csvwriter.writeheader()
     #write file rows (voltages)
     csvwriter.writerow(voltages)

#p_total, q_total = sim.monte_carlo_loadflow(N_SAMPLES, STD_DEV)
#print(p_total, q_total)
