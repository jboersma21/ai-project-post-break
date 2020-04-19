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
import pprint

# Implement state manager to traverse through of current state, future states, and previous states
class GameScheduler(object):
    def __init__(self, depth_bound, frontier_max_size, initial_resources, initial_countries, num_output_schedules, output_schedule_filename):
        self.cur_state = World(d_bound=depth_bound, weight_dict=initial_resources, country_dict=initial_countries)
        self.output_file = output_schedule_filename
        self.frontier_queue = list()  # priority queue that store states
        self.prev_states = list()  # stack of explored states
        self.depth_bound = depth_bound
        self.frontier_max_size = frontier_max_size
        self.inter_prob_success = 0
        self.init_output_schedules = num_output_schedules
        self.output_schedules_left = num_output_schedules
        self.completed_sched_eu = []

    # unfinished depth-bound search algorithm
    def execute_search(self):
        open(self.output_file, "w").close()             # clear file if already has output in it
        self.cur_state.prev_op.append("")
        heapq.heappush(self.frontier_queue, (self.cur_state.exp_utility * -1, self.cur_state))

        while self.output_schedules_left > 0:
            self.go_to_next_state()

    def go_to_next_state(self):
        successors_queue = list()
        self.cur_state = self.pop_future_state()
        for world in generate_successors(self.cur_state):
            world.search_depth += 1
            for country in world.countries:                     # update all measures for each successor before adding future state
                world.countries[country].update_discount_reward(world.search_depth)
                world.countries[country].update_c_prob_success()
            for referenced in world.referenced_countries:
                world.prob_success = world.prob_success * world.countries[referenced].c_prob_success
            world.update_exp_utility()
            self.inter_prob_success = world.prob_success
            world.prob_success = 1  # update back to 1 after calculating EU

            heapq.heappush(successors_queue, (world.exp_utility * -1, world))
        self.prev_states.append(self.get_cur_eu())

        while len(self.frontier_queue) < self.frontier_max_size:
            next_successor = heapq.heappop(successors_queue)[1]
            next_successor.prev_eu.append(self.get_cur_eu())
            cur_eu = next_successor.exp_utility
            if next_successor.search_depth == self.depth_bound:
                if cur_eu in self.completed_sched_eu:
                    return
                else:
                    next_successor.prev_eu.append(cur_eu)
                    self.completed_sched_eu.append(cur_eu)
                    self.output_schedules_left -= 1
                    output_str = "Schedule #: " + str(self.init_output_schedules - self.output_schedules_left) + "\n"
                    print("Schedule #: ", self.init_output_schedules - self.output_schedules_left)
                    for i in range(0, len(next_successor.prev_eu)):
                        print("\nSearch Depth: ", i)
                        output_str += "\nSearch Depth: " + str(i)
                        print('\t', next_successor.prev_op[i], " EU:", next_successor.prev_eu[i])
                        output_str += '\t' + str(next_successor.prev_op[i]) + "EU:" + str(next_successor.prev_eu[i]) + "\n"
                    output_str += "\n\n"
                    print("\n\n")
                    output_to_file(self.output_file, output_str)
                    return
            else:
                heapq.heappush(self.frontier_queue, (next_successor.exp_utility * -1, next_successor))

    def pop_future_state(self):
        return heapq.heappop(self.frontier_queue)[1]


    def get_cur_eu(self):
        return self.cur_state.exp_utility

def generate_successors(current_state):
    successors = list()
    # Add every transformation for every country
    for country in current_state.countries.keys():
        for operator in configuration["definitions"]:
            if operator != 'transfer':
                tmp_world = current_state.get_deep_copy()
                bins = 0.25
                while tmp_world.transform(transformation=operator, bins=bins, country=country) and bins <= 1:
                    if country not in tmp_world.referenced_countries:
                        tmp_world.referenced_countries.append(country)
                    successors.append(tmp_world)
                    bins += 0.25
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


def output_to_file(file_name, output_str):
    output_file = open(file_name, 'a')
    output_file.write(output_str)
    output_file.close()

def game_scheduler(resources_filename, initial_state_filename, operator_def_filename, output_schedule_filename,
                   num_output_schedules, depth_bound, frontier_max_size):
    data_import.read_operator_def_config(operator_def_filename)
    my_state_manager = GameScheduler(depth_bound,
                                     frontier_max_size,
                                     data_import.create_resource_dict(resources_filename),
                                     data_import.create_country_dict(initial_state_filename),
                                     num_output_schedules, output_schedule_filename)

    print('\nSearch on {}:'.format(initial_state_filename))
    my_state_manager.execute_search()
    print('\n')

def main(argv):
    for name in ['1']:
        game_scheduler(resources_filename='data/resources_{}.xlsx'.format(name),
                       initial_state_filename='data/initial_state_{}.xlsx'.format(name),
                       operator_def_filename='data/operator_def_{}.xlsx'.format(name),
                       output_schedule_filename='data/output_{}.txt'.format(name), num_output_schedules=30,
                       depth_bound=5, frontier_max_size=100)

if __name__ == "__main__":
    main(sys.argv)