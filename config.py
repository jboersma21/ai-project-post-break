"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""

# GAMMA: 0 <= gamma < 1 (experiment with different values)

# X_0 and K
# input to logistic function (experiment with different values)

# C = negative constant representing cost to country of proposing schedule that fails (experiment with)

"""
Dictionary of dictionaries/lists to hold values read in from Excel files
    Operations = list of operator names
    Resources = list of resources
    Definitions: dictionary of operators with definitions
        - Tuple input is read and formatted as nested dictionaries
    Parameters: dictionary of parameters and values
"""
configuration = {
    "operations": [],
    "resources": [],
    "definitions": {
    },
    "parameters": {
    }
}

