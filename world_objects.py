"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""

from copy import deepcopy
from config import configuration
from auxiliary.inequality_measures import *


# Represents a single state (i.e. an individual world)
class World(object):

    def __init__(self, d_bound, weight_dict, country_dict):
        self.num_country = len(country_dict)    # number of countries in the world
        self.d_bound = d_bound                  # deepest level at which successors are generated
        self.weights = weight_dict              # resources and their corresponding weights
        self.countries = {}                     # dictionary of country objects
        self.prev_op = None                     # store previous operation details

        for country in country_dict:
            name = country
            resources = country_dict[country]  # resources for specific country
            new_country = Country(name, resources, weight_dict)  # create country object with name and resources
            self.countries[name] = new_country  # add country object to countries dictionary

    def __lt__(self, other):
        # referenced from group 7
        return self.get_big_u() > other.get_big_u()

    def get_deep_copy(self):
        return deepcopy(self)

    def print_search_state(self):
        for country in self.countries:
            country_obj = self.countries[country]
            print(country)
            for resource in country_obj.resources:
                print('\t' + resource, country_obj.resources[resource])

    def little_u_array(self):
        u_lst = []
        for country in self.countries.values():
            utility = country.little_u()
            u_lst.append(utility)

        return np.array(u_lst)

    def transfer(self, exporter, destination, resource, bins=1):
        available = self.countries[exporter].resources[resource]
        if (available < bins and resource != "R1") or available <= bins:    # avoid exporting entire population
            return False
        self.countries[exporter].resources[resource] -= bins
        self.countries[destination].resources[resource] += bins
        return True

    def get_big_u(self):
        u_array = self.little_u_array()
        sum_u = np.sum(u_array)  # sum of per-capita little-u
        return sum_u / gini_index(u_array)

    def set_prev_op(self, details):
        self.prev_op = details


# Represents an individual country
class Country(object):

    def __init__(self, name, resource_dict, weight_dict):
        self.name = name                          # country name
        self.resources = resource_dict            # dictionary containing amount of resources the country possesses
        self.weights = weight_dict                # dictionary containing resources and corresponding weights

    def little_u(self):
        housing_val = self.weights['R23']*(1 - (self.resources['R1']) / (2 * (self.resources['R23'] + 5)))
        alloy_val = self.weights['R21']*self.resources['R21']
        electronics_val = self.weights['R22']*self.resources['R22']
        waste_val = (-self.weights["R21'"]*self.resources["R21'"]) - (self.weights["R22'"]*self.resources["R22'"]) - \
                    (-self.weights["R23'"]*self.resources["R23'"])
        population = self.resources['R1']
        return (housing_val + alloy_val + electronics_val + waste_val) / population

    def transform(self, transformation, bins=1):
        used = dict()
        for resource, amount in configuration[transformation]["in"].items():
            amount *= bins
            if self.resources[resource] < amount:
                return False
            used[resource] = amount
        for resource, amount in used.items():
            self.resources[resource] -= amount
        for resource, amount in configuration[transformation]["out"].items():
            self.resources[resource] += amount * bins
        return True
