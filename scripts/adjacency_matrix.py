import numpy as np
import pandas as pd
#from sklearn.cluster import AgglomerativeClustering

from pfsim import PowerFactorySim

FOLDER_NAME = ''
PROJECT_NAME = 'test_scenarios_118'
STUDY_CASE_NAME = 'test_case_no_wind'

# activate both project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

#get elements which connect to buses
lines = sim.app.GetCalcRelevantObjects('*.ElmLne')
trafos = sim.app.GetCalcRelevantObjects('*.ElmTr2')
links = lines + trafos

#load bus voltages
path = r"C:\Users\olive\PycharmProjects\power_factory\load_flow"
voltages = pd.read_csv(path + r'\res_prob_lf.csv', sep=',', index_col=0)
bus_names = voltages.columns.values

#create a zero filled dataframe for adjacency matrix
adjacency = pd.DataFrame(0, index=bus_names, columns=bus_names)
#fill adjacency with 1 where connection exists
for link in links:
    link.i_Usage=0
    from_bus = link.GetNode(0).loc_name
    to_bus = link.GetNode(1).loc_name
    #set connections to 1
    adjacency.at[from_bus, to_bus] = 1
    adjacency.at[to_bus, from_bus] = 1
    print("from_bus: ", from_bus)
    print("to_bus: ", to_bus)
    
return adjacency
