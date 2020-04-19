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
        self.prev_op = []                       # store previous operation details of schedule states
        self.prev_eu = []                       # store expected utilities from previous states in schedule
        self.self_country = None                # country object that is "self"
        self.prob_success = 1
        self.exp_utility = 0
        self.search_depth = 0
        self.referenced_countries = []          # countries that have been referenced in current schedule

        # logic for binding "self" to the correct country
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
        """
        Applies a transfer operator to a World – called during generate_successors()
        :param exporter: country giving a resource
        :param destination: country receiving a resource
        :param resource: resource being transferred
        :param bins: percentage of total resources that are being binned into
        :return: True if operation is valid, False otherwise
        """
        available = self.countries[exporter].resources[resource]    # total available amount of resource
        amt = ceil(available * bins)                                # bin total available amount
        if available < amt or resource == "R1":   # avoid exporting population
            return False
        self.countries[exporter].resources[resource] -= amt
        self.countries[destination].resources[resource] += amt

        self.update_prev_op('transfer' + '\n\t' +'(TRANSFER {} {} ({} {}))'.format(exporter, destination, resource, amt))
        return True

    def transform(self, transformation, bins, country):
        """
        Applies a given transformation operator to a World – called during generate_successors()
        :param transformation: transformation to apply
        :param bins: percentage of total resources that are being binned into
        :param country: country to apply transformation to
        :return: True if operation is valid, False otherwise
        """
        multiplier = dict()
        for resource, amount in configuration['definitions'][transformation]["in"].items():
            amt = ceil(self.countries[country].resources[resource] * bins)      # get amount of a resource that is binned
            multiplier[resource] = amt / amount               # the multiplier applied to the resource's base amount in the operator definition

        min_mult = floor(min(multiplier.values()))              # minimum multiplier of all resource amounts
        if min_mult == 0:
            min_mult = 1
        for resource, amount in configuration['definitions'][transformation]["in"].items():
            use_amt = amount * min_mult     # amount to use for transform
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
        """
        Calculates and updates the expected utility for a world
            C = negative constant representing cost to country of proposing schedule that fails (experiment with)
        """
        self.exp_utility = (self.prob_success * self.self_country.discount_reward) + ((1 - self.prob_success)
                                                                                 * configuration["parameters"]["C"])

    def get_exp_utility(self):
        """
        Returns the expected utility for a world
        """
        return self.exp_utility

    def update_prev_op(self, details):
        """
        Appends previous operation to a World's prev_op list
            Used to keep track of previous operations occurring in a schedule
        :param details: String that contains the formatted previous operation
        """
        self.prev_op.append(details)

# Represents an individual country
class Country(object):
    def __init__(self, name, resource_dict, weight_dict, self_val):
        self.name = name                                # country name
        self.resources = resource_dict                  # dictionary containing amount of resources the country possesses
        self.weights = weight_dict                      # dictionary containing resources and corresponding weights
        self.init_state_q = self.state_quality()        # initial state quality for country
        self.discount_reward = 0
        self.c_prob_success = 0
        self.my_country = self_val                      # True if country is "self", False otherwise

    def state_quality(self):
        """
        State Quality Calculation
            Takes into account all resources, with unique weightings for each resource that are
            normalized by population.
        """
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

    def d_reward(self, n):
        """
        Calculates and returns discounted reward for a country
        :param n: number of time steps in a schedule (current depth of search)
        0 <= gamma < 1 (experiment with different values)
        """
        return (configuration["parameters"]["GAMMA"] ** n) * (self.state_quality() - self.init_state_q)


    def logistic_fxn(self, dr):
        """
        Calculates the logistic function value for a country.
        Determines the probability that a country will participate in a given schedule.
        @param dr (float) - discounted reward
        @return (float) - logistic fxn probability
        K and X_0 = input to logistic function (experiment with different values)
        """
        return 1 / (1 + exp((-configuration["parameters"]["K"]) * (dr - configuration["parameters"]["X_0"])))

    def update_discount_reward(self, n):
        """
        Updates discounted reward for a country
        """
        self.discount_reward = self.d_reward(n)

    def update_c_prob_success(self):
        """
        Updates country's individual probabiluty of success
        """
        self.c_prob_success = self.logistic_fxn(self.discount_reward)


