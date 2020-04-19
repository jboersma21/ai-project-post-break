"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""

from scheduler import *
from copy import deepcopy
from config import *
from math import *


# Represents a single state (i.e. an individual world)
class World(object):

    def __init__(self, d_bound, weight_dict, country_dict):
        self.num_country = len(country_dict)    # number of countries in the world
        self.d_bound = d_bound                  # deepest level at which successors are generated
        self.weights = weight_dict              # resources and their corresponding weights
        self.countries = {}                     # dictionary of country objects
        self.prev_op = []                     # store previous operation details
        self.prev_eu = []
        self.self_country = None
        self.prob_success = 1
        self.exp_utility = 0
        self.search_depth = 0
        self.referenced_countries = []

        for country in country_dict:
            if country != 'Self':

                name = country
                resources = country_dict[country]  # resources for specific country
                if name == country_dict['Self']:
                    # set my_country to True because this is the self country
                    new_country = Country(name, resources, weight_dict, True)  # create country object with name and resources
                    self.self_country = new_country
                else:
                    # set my_country to False because not self country
                    new_country = Country(name, resources, weight_dict, False)  # create country object with name and resources
                self.countries[name] = new_country  # add country object to countries dictionary

    def __lt__(self, other):
        # referenced from group 7
        return self.get_exp_utility() > other.get_exp_utility()

    def get_deep_copy(self):
        return deepcopy(self)

    def transfer(self, exporter, destination, resource, bins):
        available = self.countries[exporter].resources[resource]
        amt = ceil(available * bins)
        if available < amt or resource == "R1":   # avoid exporting entire populations
            return False
        self.countries[exporter].resources[resource] -= amt
        self.countries[destination].resources[resource] += amt

        self.update_prev_op('transfer' + '\n\t' +'(TRANSFER {} {} ({} {}))'.format(exporter, destination, resource, amt))
        return True

    def transform(self, transformation, bins, country):
        multiplier = dict()
        for resource, amount in configuration['definitions'][transformation]["in"].items():
            amt = ceil(self.countries[country].resources[resource] * bins)
            multiplier[resource] = amt / amount
        min_mult = floor(min(multiplier.values()))
        if min_mult == 0:
            min_mult = 1
        for resource, amount in configuration['definitions'][transformation]["in"].items():
            use_amt = amount * min_mult
            if self.countries[country].resources[resource] < use_amt:
                return False
            self.countries[country].resources[resource] -= use_amt
        for resource, amount in configuration['definitions'][transformation]["out"].items():
            self.countries[country].resources[resource] += (amount * min_mult)

        ins = ()
        outs = ()
        for i, j in configuration['definitions'][transformation]["in"].items():
            ins += (i, j * min_mult),
        for i, j in configuration['definitions'][transformation]["out"].items():
            outs += (i, j * min_mult),
        self.update_prev_op(transformation + '\n\t' + '(TRANSFORM {} (INPUTS {} (OUTPUTS {})'.format(country, ins, outs))
        return True

    def update_exp_utility(self):
        # C = negative constant representing cost to country of proposing schedule that fails (experiment with)
        self.exp_utility = (self.prob_success * self.self_country.discount_reward) + ((1 - self.prob_success)
                                                                                 * configuration["parameters"]["C"])

    def get_exp_utility(self):
        return self.exp_utility

    def update_prev_op(self, details):
        self.prev_op.append(details)

# Represents an individual country
class Country(object):
    def __init__(self, name, resource_dict, weight_dict, self_val):
        self.name = name                          # country name
        self.resources = resource_dict            # dictionary containing amount of resources the country possesses
        self.weights = weight_dict                # dictionary containing resources and corresponding weights
        self.init_state_q = self.state_quality()       # initial state quality for country
        self.discount_reward = 0
        self.c_prob_success = 0
        self.my_country = self_val

    def state_quality(self):
        population = self.resources['R1']
        housing_val = self.weights['R23'] * (1 - population / (3 * (self.resources['R23'] + 5)))
        alloy_val = self.weights['R21'] * (1 - population / (self.resources['R21'] + 5))
        electronics_val = self.weights['R22'] * (1 - population / (self.resources['R22'] + 5))
        food_val = self.weights['R24'] * (1 - population / (3 * (self.resources['R24'] + 5)))
        farm_val = self.weights['R25'] * (1 - population / (50 * (self.resources['R25'] + 5)))

        fossilEnergyUsable_val = self.weights['R26'] * (1 - population / (30 * (self.resources['R26'] + 5)))
        renewableEnergyUsable_val = self.weights['R27'] * (1 - population / (40 * (self.resources['R27'] + 5)))

        waste_val = (-self.weights["R21'"] * self.resources["R21'"]) - (self.weights["R22'"] * self.resources["R22'"]) - \
                    (self.weights["R23'"] * self.resources["R23'"]) - (self.weights["R24'"] * self.resources["R24'"]) - \
                    (self.weights["R25'"] * self.resources["R25'"]) - (self.weights["R26'"] * self.resources["R26'"]) - \
                    (self.weights["R27'"] * self.resources["R27'"])

        util = housing_val + food_val + fossilEnergyUsable_val + renewableEnergyUsable_val + electronics_val + \
               alloy_val + farm_val + (waste_val / (5 * population))
        return util

    """
        Calculates the discounted reward to a country.
        @param end_state_q (float) - state quality of end state
        @param start_state_q (float) - state quality of start state
        @param N (int) - number of time steps in a schedule
        @return (float) - discounted reward; can be positive or negative
     """

    def d_reward(self, n):
        # 0 <= gamma < 1 (experiment with different values)
        return (configuration["parameters"]["GAMMA"] ** n) * (self.state_quality() - self.init_state_q)
        # country's current state quality minus its initial state quality

    """
        Calculates the logistic function value for a country.
        Determines the probability that a country will participate in a given schedule.
        @param dr (float) - discounted reward
        @return (float) - logistic fxn probability 
    """
    def logistic_fxn(self, dr):
        # input to logistic function (experiment with different values)
        # K and X_0
        return 1 / (1 + exp((-configuration["parameters"]["K"]) * (dr - configuration["parameters"]["X_0"])))

    def update_discount_reward(self, n):                                           # REFERENCE TEAM 5 FOR THIS DESIGN
        self.discount_reward = self.d_reward(n)

    def update_c_prob_success(self):
        self.c_prob_success = self.logistic_fxn(self.discount_reward)


