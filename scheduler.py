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
from config import *


# Implement state manager to traverse through of current state, future states, and previous states
class WorldStateManager(object):

    def __init__(self, depth_bound, initial_resources, initial_countries):
        self.cur_state = World(d_bound=depth_bound, weight_dict=initial_resources, country_dict=initial_countries)
        self.future_states = list()  # priority queue that store states based on big-u
        self.prev_states = list()  # stack of explored state big-Us
        self.cur_depth = 0

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
            for country in world.countries:
                world.countries[country].update_c_prob_success()
                world.countries[country].update_discount_reward()
                world.countries[country].update_exp_utility(world)
                world.prob_success = world.prob_success * world.countries[country].c_prob_success
        self.prev_states.append(self.cur_state.get_big_u())
        self.cur_state = self.pop_future_state()
        self.cur_depth += 1

    def add_future_state(self, world_state):
        heapq.heappush(self.future_states, (world_state.get_big_u() * -1, world_state))

    def pop_future_state(self):
        return heapq.heappop(self.future_states)[1]

    def print_cur_state_info(self):
        if self.cur_depth > 0:
            print('\t-> Operator: {}'.format(self.cur_state.prev_op))
        print('State {}:\t{}'.format(self.cur_depth, self.get_cur_big_u()))

    def get_cur_big_u(self):
        return self.cur_state.get_big_u()

    def get_cur_depth(self):
        return self.cur_depth

    # product of each individual country probabilities (logistic fxn values)
    def prob_success(self, world):

        return

    def expected_utility(self):
        # [ prob_success(schedule_j) * d_reward(country_i, schedule_j) ] + [ (1 - prob_success(schedule_j)) * C ]
        return


def generate_successors(current_state):
    successors = list()

    # Add every transformation for every country
    for country in current_state.countries.keys():
        for operator in configuration["definitions"]:
            if operator != 'transfer':                          # FIX LATER (MAYBE DONT READ IN TRANSFERS)
                tmp_world = current_state.get_deep_copy()
                bins = 1
                while tmp_world.countries[country].transform(transformation=operator, bins=bins):
                    ins = [i * bins for i in configuration['definitions'][operator]["in"].values()]
                    outs = [i * bins for i in configuration['definitions'][operator]["out"].values()]
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
    if sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        wb.remove(sheet)
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



def run_successor_test(resources_filename, initial_state_filename, operator_def_filename, output_schedule_filename):
    data_import.read_operator_def_config(file_name=operator_def_filename)
    my_state_manager = WorldStateManager(depth_bound=3,
                                         initial_resources=data_import.create_resource_dict(file_name=resources_filename),
                                         initial_countries=data_import.create_country_dict(file_name=initial_state_filename))
    output_successors_to_excel(file_name=output_schedule_filename, successors=generate_successors(my_state_manager.cur_state))

    print('\nExample Search on {}:'.format(resources_filename))
    my_state_manager.execute_search()
    print('\n')


def main(argv):
    # for name in ['Test1', 'Test2', 'Test3', 'Test4']:
    #     run_successor_test(file_name='data/Pre_Break/Initial-World-{}.xlsx'.format(name))

    for name in ['1']:
        run_successor_test(resources_filename='data/resources_{}.xlsx'.format(name),
                           initial_state_filename='data/initial_state_{}.xlsx'.format(name),
                           operator_def_filename='data/operator_def_3.xlsx',
                           output_schedule_filename='data/output_{}.xlsx'.format(name))


if __name__ == "__main__":
    main(sys.argv)
