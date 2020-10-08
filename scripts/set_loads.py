from pfsim import PowerFactorySim
import numpy as np

FOLDER_NAME = ''
PROJECT_NAME = 'IEEE 118bus_modified'
STUDY_CASE_NAME = 'BASE CASE'

# activate both project and study case
sim = PowerFactorySim(
    folder_name=FOLDER_NAME,
    project_name=PROJECT_NAME,
    study_case_name=STUDY_CASE_NAME)

MEAN = 40
STANDARD_DEVIATION = 5
POWER_FACTOR = 0.95

sim.set_loads(MEAN,STANDARD_DEVIATION,POWER_FACTOR)

