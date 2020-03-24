"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""

import sys
import heapq
from openpyxl import load_workbook

import data_import
from world_objects import World
from config import configuration
from math import exp

# 0 <= gamma < 1 (experiment with different values)
GAMMA = 0.75

# input to logistic function (experiment with different values)
X_0 = 0
K = 1

# negative constant representing cost to country of proposing schedule that fails (experiment with)
C = -2


# Implement state manager to traverse through of current state, future states, and previous states
class WorldStateManager(object):

    def __init__(self, depth_bound, initial_resources, initial_countries):
        self.cur_state = World(d_bound=depth_bound, weight_dict=initial_resources, country_dict=initial_countries)
        self.future_states = list()  # priority queue that store states based on big-u
        self.prev_states = list()  # stack of explored state big-Us
        self.depth = 0

    # unfinished depth-bound search algorithm
    def execute_search(self):
        self.print_cur_state_info()
        while self.cur_state.get_big_u() not in self.prev_states:
            self.go_to_next_state()
            self.print_cur_state_info()
            # to-do: add depth-bounded logic

    def go_to_next_state(self):
        self.future_states = list()  # clear old list of successors?
        for world in generate_successors(self.cur_state):
            self.add_future_state(world_state=world)
        self.prev_states.append(self.cur_state.get_big_u())
        self.cur_state = self.pop_future_state()
        self.depth += 1

    def add_future_state(self, world_state):
        heapq.heappush(self.future_states, (world_state.get_big_u() * -1, world_state))

    def pop_future_state(self):
        return heapq.heappop(self.future_states)[1]

    def print_cur_state_info(self):
        if self.depth > 0:
            print('\t-> Operator: {}'.format(self.cur_state.prev_op))
        print('State {}:\t{}'.format(self.depth, self.get_cur_big_u()))

    def get_cur_big_u(self):
        return self.cur_state.get_big_u()

    ###############################################
    #           NEW CODE FOR POST-BREAK           #
    ###############################################

    """
       Calculates the un-discounted reward to a country.
       @param end_state_q (float) - state quality of end state
       @param start_state_q (float) - state quality of start state
       @return (float) - un-discounted reward; can be positive or negative
    """

    def u_reward(self, end_state_q, start_state_q):
        return end_state_q - start_state_q  # change so parameters are country & schedule?
        # same w/ d_reward below

    """
        Calculates the discounted reward to a country.
        @param end_state_q (float) - state quality of end state
        @param start_state_q (float) - state quality of start state
        @param N (int) - number of time steps in a schedule
        @return (float) - discounted reward; can be positive or negative
     """

    def d_reward(self, end_state_q, start_state_q, N):
        return (GAMMA ** N) * (end_state_q - start_state_q)

    """
        Calculates the logistic function value for a country.
        Determines the probability that a country will participate in a given schedule.
        @param dr (float) - discounted reward
        @return (float) - logistic fxn probability 
    """

    def logistic_fxn(self, dr):
        return 1 / (1 + exp((-K) * (dr - X_0)))

    # product of each individual country probabilities (logistic fxn values)
    def prob_success(self):
        return

    def expected_utility(self):
        # [ prob_success(schedule_j) * d_reward(country_i, schedule_j) ] + [ (1 - prob_success(schedule_j)) * C ]
        return


def generate_successors(current_state):
    successors = list()

    # Add every transformation for every country
    for country in current_state.countries.keys():
        for operator in configuration["transformations"]:
            tmp_world = current_state.get_deep_copy()
            bins = 1
            while tmp_world.countries[country].transform(transformation=operator, bins=bins):
                ins = [i * bins for i in configuration[operator]["in"].values()]
                outs = [i * bins for i in configuration[operator]["out"].values()]
                tmp_world.set_prev_op('{} (in={} out={}) (bins={})'.format(operator, ins, outs, bins))
                successors.append(tmp_world)
                bins += 1
                tmp_world = current_state.get_deep_copy()

    # Add every transfer for every pair of countries (both ways)
    for exporter in current_state.countries.keys():
        for destination in current_state.countries.keys():
            if exporter != destination:
                for resource in configuration["resources"]:
                    tmp_world = current_state.get_deep_copy()
                    bins = 1
                    while tmp_world.transfer(exporter=exporter, destination=destination, resource=resource, bins=bins):
                        tmp_world.set_prev_op('{} (from={} to={} resource={} amount={})'
                                              ''.format('transfer', exporter, destination, resource, bins))
                        successors.append(tmp_world)
                        bins += 1
                        tmp_world = current_state.get_deep_copy()

    return successors


def output_successors_to_excel(file_name, successors):
    wb = load_workbook(file_name)
    sheet_name = 'Successors (Test Results)'
    if sheet_name in wb.get_sheet_names():
        sheet = wb.get_sheet_by_name(sheet_name)
        wb.remove_sheet(sheet)
    ws = wb.create_sheet(sheet_name)
    cur_row = 1
    cur_col = 1

    for idx, state in enumerate(successors):
        if idx > 9:  # only print first 10 successors
            break
        ws.cell(row=cur_row, column=cur_col).value = 'Successor'
        cur_col += 1
        ws.cell(row=cur_row, column=cur_col).value = idx + 1
        cur_col += 2
        ws.cell(row=cur_row, column=cur_col).value = 'Big-U'
        cur_col += 1
        ws.cell(row=cur_row, column=cur_col).value = state.get_big_u()
        cur_col += 2
        ws.cell(row=cur_row, column=cur_col).value = 'Prev Op'
        cur_col += 1
        ws.cell(row=cur_row, column=cur_col).value = state.prev_op

        cur_row += 1
        cur_col = 1
        ws.cell(row=cur_row, column=cur_col).value = 'Country'
        cur_col += 1
        for r in configuration['resources']:
            ws.cell(row=cur_row, column=cur_col).value = r
            cur_col += 1

        cur_row += 1
        cur_col = 1
        for name, country in state.countries.items():
            ws.cell(row=cur_row, column=cur_col).value = name
            cur_col += 1
            for r in configuration['resources']:
                ws.cell(row=cur_row, column=cur_col).value = country.resources[r]
                cur_col += 1
            cur_col = 1
            cur_row += 1

        cur_row += 1

    print('{} Test Complete'.format(file_name))
    wb.save(file_name)


def run_successor_test(file_name):
    my_state_manager = WorldStateManager(depth_bound=3,
                                         initial_resources=data_import.create_resource_dict(file_name=file_name),
                                         initial_countries=data_import.create_country_dict(file_name=file_name))
    output_successors_to_excel(file_name=file_name, successors=generate_successors(my_state_manager.cur_state))

    print('\nExample Search on {}:'.format(file_name))
    my_state_manager.execute_search()
    print('\n')


def main(argv):
    for name in ['Test1', 'Test2', 'Test3', 'Test4']:
        run_successor_test(file_name='data/Initial-World-{}.xlsx'.format(name))


if __name__ == "__main__":
    main(sys.argv)
