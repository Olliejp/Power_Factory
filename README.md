# Powerfactory dynamic simulations code for IEEE 118 bus system

## Structure

    .
    ├── Modules/pfsim.py         # Modules to cover most powerfactory functionality regarding RMS simulations
    ├── Scripts/                 # Scripts utilising modules for specific simulation tasks

## Modules

- __init__ : initialises Powerfactory in engine mode and activates project and study case
- **return_objects**: prints network elements of interest within currently activated project
- **set_loads**: will set system loads randomly from a probability distrubution 
- **reset_loads_to_nominal**: resets all loads in the system from values previously saved to a .csv file
- **get_loads_from_file**: read and return loads saved in a csv file
- **set_all_loads_pq**: sets all active and reactive loads in the system. Scaling of loads can also be achieved. 
- **get_all_loads_pq**: return all current system active and reactive loads
- **set_dispatch**: set system dispatch to match system loads
- **prepare_dynamic_sim**: prepares dynamic simulation initial conditions and runs load flow
- **enable_short_circuits**: lines are by default unavailable. This function sets available for all lines in system
- **create_short_circuit**: creates a short circuit in Powerfactory's events folder
- **delete_short_circuit**: removes short circuit from events folder
- **run_dynamic_sim**: executes RMS simulation
- **get_voltage_scan**: returns results voltage violations from simulation scan
- **get_frequency_scan**: returns results frequency violations from simulation scan
- **calculate_system_inertia**: calculates total system inertia given a specific operating condition 
- **calculate_spinning_reserve**: calculates total system spinning reserve given a specific operating condition 
- **get_dynamic_results**: returns simulation results
- **prepare_loadflow**: prepares conditions for power flow calulation
- **run_loadflow**: executes power flow calculation
- **get_bus_voltages**: returns all bus voltages following power flow calculation

## Scripts

    .
    ├── rms_sim.py                   # runs multiple RMS simulations in a loop and saves simulation results to .csv
    ├── cct.py                       # calculates critical clearing time for each line in the system
    ├── accessing_elements.py        # returns elements of interest
    ├── save_nominal_loads.py        # Saves nominal system loads to .csv for future reference
    ├── set_loads.py                 # 
    ├── prob_load_flow.py            # Executes load flow in loop drawing params from normal probability distrubution
    ├── adjacency_matrix.py          # Constructs adjacency matrix for system topology 
