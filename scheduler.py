"""
Project Post Break
Team 6
Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma
"""

import sys
import heapq
import data_import
from world_objects import *
from config import *
import csv

import numpy as np
import matplotlib.pyplot as plt


NUM_TEST_FILES = 8
NUM_PARAM_SETS = 9
DEPTH_BOUND = 25
NUM_OUTPUT_SCHEDULES = 5
MAX_FRONTIER_SIZE = 50


# Implement state manager to traverse through of current state, future states, and previous states
class GameScheduler(object):
    def __init__(self, depth_bound, frontier_max_size, initial_resources, initial_countries, num_output_schedules, output_schedule_filename):

        self.cur_state = World(d_bound=depth_bound, weight_dict=initial_resources, country_dict=initial_countries)
        self.output_file = output_schedule_filename
        self.frontier_queue = list()                                # top-level priority queue that store states
        self.depth_bound = depth_bound
        self.frontier_max_size = frontier_max_size
        self.init_output_schedules = num_output_schedules           # initial number of schedules to output
        self.output_schedules_left = num_output_schedules           # number of schedules still needed to output
        self.completed_sched_eu = []     # keeps track of final EU of completed schedules so that they are not revisited
        self.output_data = dict()

    def execute_search(self):
        """
        Executes anytime search that terminates when num_output_schedules have been written
        """
        open(self.output_file, "w").close()             # clear file if already has output in it
        self.cur_state.prev_op.append("")               # empty op for initial state
        heapq.heappush(self.frontier_queue, (self.cur_state.exp_utility * -1, self.cur_state))
        # push initial state onto frontier_queue

        while self.output_schedules_left > 0:
            self.go_to_next_state()
        print('-> search complete')
        print('-> sending results to csv')
        self.output_results()
        print('-> csv output complete\n')

        # creating a graph plot of results
        plt.xlabel('Depth of Search')
        plt.ylabel('Expected Utility')
        plt.xlim(0, DEPTH_BOUND + 1)
        plt.ylim(0, None)
        plt.legend()

    def go_to_next_state(self):
        """
        Visits next state in frontier_queue, generates successors, and performs scheduling logic
        """
        successors_queue = list()                            # local priority queue to hold successors generated
        self.cur_state = self.pop_future_state()             # pop top state from frontier_queue to explore
        for world in generate_successors(self.cur_state):
            world.search_depth += 1
            for country in world.countries:         # update all measures for each successor before adding future state
                world.countries[country].update_discount_reward(world.search_depth)
                world.countries[country].update_c_prob_success()
            # only factor in prob. of success for countries mentioned in schedule
            for referenced in world.referenced_countries:
                world.prob_success = world.prob_success * world.countries[referenced].c_prob_success
            world.update_exp_utility()
            world.prob_success = 1      # update back to 1 after calculating EU

            heapq.heappush(successors_queue, (world.exp_utility * -1, world))   # push onto successors_queue heap

        # add successors to frontier_queue as long as it is below frontier_max_size
        while len(self.frontier_queue) < self.frontier_max_size:
            next_successor = heapq.heappop(successors_queue)[1]           # top successors from successors_queue
            next_successor.prev_eu.append(self.cur_state.exp_utility)     # add cur_state EU to prev_eu
            cur_eu = next_successor.exp_utility
            if next_successor.search_depth == self.depth_bound:           # found schedule at depth_bound
                if cur_eu in self.completed_sched_eu:                     # do not repeat final state at depth_bound
                    continue
                else:
                    next_successor.prev_eu.append(cur_eu)
                    self.completed_sched_eu.append(cur_eu)
                    self.output_schedules_left -= 1
                    schedule_index = self.init_output_schedules - self.output_schedules_left
                    schedule_summary = list()

                    # logic for compiling values for output and graphing
                    x_coord = np.array([])
                    y_coord = np.array([])
                    for i in range(1, len(next_successor.prev_eu)):
                        op_name, op_details = next_successor.prev_op[i].splitlines()
                        op_details = op_details.replace('\t', '')
                        schedule_summary.append((i, op_name, op_details, next_successor.prev_eu[i]))
                        x_coord = np.append(x_coord, [i])
                        y_coord = np.append(y_coord, [next_successor.prev_eu[i]])
                    plt.plot(x_coord, y_coord, marker='*', label="Schedule " + str(schedule_index))  # graph

                    self.output_data[schedule_index] = schedule_summary     # output completed schedule
                    print('-> schedule {} of {} complete'.format(schedule_index, self.init_output_schedules))
                    return
            # not at depth_bound, so push successor onto frontier_queue and continue searching for schedule
            else:
                heapq.heappush(self.frontier_queue, (next_successor.exp_utility * -1, next_successor))

    def pop_future_state(self):
        """
        Pops and returns the top state on the frontier queue (state with highest EU)
        """
        return heapq.heappop(self.frontier_queue)[1]

    def output_results(self):
        """
        Output results of a schedule to Excel file
        """
        with open(self.output_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Schedule', 'Depth', 'Operator Name', 'State Details'])
            for index in range(1, self.init_output_schedules + 1):
                for step in self.output_data[index]:
                    depth, op_name, op_details, eu = step
                    writer.writerow([index, depth, op_name, '{}  EU: {}'.format(op_details, eu)])
                writer.writerow(['', '', '', ''])


def generate_successors(current_state):
    """
    Generate all successors from a current state of the World
        - Successors are generated in two phases: transforms and transfers
        - Successors are binned in values of 25%, 50%, 75%, and 100% of the total possible amount of resources
    :param current_state: world object
    :return: list of all successors
    """
    successors = list()
    # Add every transformation for every country
    for country in current_state.countries.keys():
        for operator in configuration["definitions"]:
            if operator != 'transfer':
                tmp_world = current_state.get_deep_copy()
                bins = 0.25     # start with bin of 25%
                while tmp_world.transform(transformation=operator, bins=bins, country=country) and bins <= 1:
                    if country not in tmp_world.referenced_countries:
                        tmp_world.referenced_countries.append(country)
                    successors.append(tmp_world)
                    bins += 0.25    # add another 25% to bin
                    bins = round(bins, 2)
                    tmp_world = current_state.get_deep_copy()

    # Add every transfer for every pair of countries (both ways)
    for exporter in current_state.countries.keys():
        for destination in current_state.countries.keys():
            if exporter != destination:
                for resource in configuration["resources"]:
                    tmp_world = current_state.get_deep_copy()
                    bins = 0.25
                    while tmp_world.transfer(exporter=exporter, destination=destination, resource=resource, bins=bins) and bins <= 1:
                        if exporter not in tmp_world.referenced_countries:
                            tmp_world.referenced_countries.append(exporter)
                        if destination not in tmp_world.referenced_countries:
                            tmp_world.referenced_countries.append(destination)
                        successors.append(tmp_world)
                        bins += 0.25
                        bins = round(bins, 2)
                        tmp_world = current_state.get_deep_copy()
    return successors


def game_scheduler(resources_filename, initial_state_filename, operator_def_filename, output_schedule_filename,
                   parameter_filename, num_output_schedules, depth_bound, frontier_max_size):
    """
    Top-Level Function to initialize a game and run scheduling
    :param resources_filename: Resources and corresponding weights
    :param initial_state_filename: Initial state of world
    :param operator_def_filename: Operator definitions
    :param output_schedule_filename: File to output schedules to
    :param parameter_filename: Parameter values
    :param num_output_schedules: number of schedules to find
    :param depth_bound: maximum depth of search
    :param frontier_max_size: maximum size of priority queue
    """

    data_import.read_operator_def_config(operator_def_filename)     # read in operator defs
    data_import.read_paramater_def_config(parameter_filename)       # read in parameters
    my_state_manager = GameScheduler(depth_bound,
                                     frontier_max_size,
                                     data_import.create_resource_dict(resources_filename),
                                     data_import.create_country_dict(initial_state_filename),
                                     num_output_schedules, output_schedule_filename)

    print('\nSearch on {}:'.format(initial_state_filename))
    my_state_manager.execute_search()
    print('\n')

def main(argv):
    # runs given tests on scheduler
    for test in range(1, NUM_TEST_FILES + 1):
        name = str(test)
        game_scheduler(resources_filename='data/resources_1.xlsx'.format(name),
                       initial_state_filename='data/initial_states/initial_state_{}.xlsx'.format(name),
                       operator_def_filename='data/operator_def_1.xlsx'.format(name),
                       output_schedule_filename='data/outputs/output_{}-1.csv'.format(name),
                       parameter_filename='data/parameter_sets/parameters_1.xlsx'.format(name),
                       num_output_schedules=NUM_OUTPUT_SCHEDULES,
                       depth_bound=DEPTH_BOUND,
                       frontier_max_size=MAX_FRONTIER_SIZE)

        plt.savefig('data/plots/plot_{}-1.png'.format(name))                # outputs matplotlib of schedule utilities

    for test in range(1, NUM_PARAM_SETS + 1):
        name = str(test)
        game_scheduler(resources_filename='data/resources_1.xlsx'.format(name),
                       initial_state_filename='data/initial_states/initial_state_1.xlsx'.format(name),
                       operator_def_filename='data/operator_def_1.xlsx'.format(name),
                       output_schedule_filename='data/outputs/output_1-{}.csv'.format(name),
                       parameter_filename='data/parameter_sets/parameters_{}.xlsx'.format(name),
                       num_output_schedules=NUM_OUTPUT_SCHEDULES,
                       depth_bound=DEPTH_BOUND,
                       frontier_max_size=MAX_FRONTIER_SIZE)

        plt.savefig('data/plots/plot_1-{}.png'.format(name))
    sys.exit()

if __name__ == "__main__":
    main(sys.argv)