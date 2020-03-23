"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""

configuration = {
    "transformations": ["alloy_transform", "electronics_transform", "housing_transform"],
    "resources": ["R1", "R2", "R3", "R21", "R22", "R23", "R21'", "R22'", "R23'"],
    "alloy_transform": {
        "in": {"R1": 1.0, "R2": 2.0},
        "out": {"R1": 1.0, "R21": 1.0, "R21'": 1.0}
    },
    "electronics_transform": {
        "in": {"R1": 3.0, "R2": 2.0, "R21": 2.0},
        "out": {"R1": 3.0, "R22": 2.0, "R22'": 2.0}
    },
    "housing_transform": {
        "in": {"R1": 5.0, "R2": 1.0, "R3": 5.0, "R21": 3.0},
        "out": {"R1": 5.0, "R23": 1.0, "R23'": 1.0}
    }
}