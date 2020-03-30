"""
Project Post Break

Team 6

Colin Moody, Ohad Beck, Charlie MacVicar, Jake Boersma

"""
import string
from openpyxl import load_workbook
from config import *
import re

DATA_FILE = 'data/Pre_Break/Initial-World.xlsx'

RESOURCE_DATA_FILE = 'data/resources.xlsx'
INITIAL_STATE_DATA_FILE = 'data/initial_state.xlsx'
OPERATOR_DEF_DATA_FILE = 'data/operator_def.xlsx'


def create_resource_dict(file_name=RESOURCE_DATA_FILE):
    """
    Creates a dictionary containing resource and weight info.
    Keys: name of resource
    Values: weight of corresponding resource
    """
    wb = load_workbook(file_name)
    resources_sheet = wb.get_sheet_by_name('Resources')
    resource_dict = {}
    for row in range(2, resources_sheet.max_row + 1):
        key = get_val(resources_sheet, 'A', row)
        value = get_val(resources_sheet, 'B', row)
        config_new["resources"].append(key)             # adding resources to config file
        resource_dict[key] = value
    return resource_dict


def create_country_dict(file_name=INITIAL_STATE_DATA_FILE):
    """
    Creates a dictionary containing country info.
    Keys: name of country
    Values: dictionary where key = resource_name and value = resource_amount
    """
    wb = load_workbook(file_name)
    country_sheet = wb.get_sheet_by_name('Countries')
    country_dict = {}
    for row in range(2, country_sheet.max_row + 1):
        key = get_val(country_sheet, 'A', row)
        resrc_dict = {}
        for col in range(2, country_sheet.max_column + 1):
            resrc_key = get_val(country_sheet, col_letter(col), 1)
            resrc_value = get_val(country_sheet, col_letter(col), row)
            resrc_dict[resrc_key] = resrc_value
        resrc_dict["R21'"] = 0
        resrc_dict["R22'"] = 0
        resrc_dict["R23'"] = 0
        country_dict[key] = resrc_dict
    return country_dict

def read_operator_def(file_name=OPERATOR_DEF_DATA_FILE):
    """
    FILL IN
    """
    wb = load_workbook(file_name)
    op_sheet = wb.get_sheet_by_name('Operators')
    for row in range(2, op_sheet.max_row + 1):
        op_name = get_val(op_sheet, 'A', row)
        if op_name is not None:
            config_new["transformations"].append(op_name)
        op_str = get_val(op_sheet, 'B', row)
        if op_str is not None:
            splits = re.split(r'[()\s]\s*', str(op_str))

            config_new["definitions"].update({op_name: {"in": {}, "out": {}}})

            input_idx = 0
            output_idx = 0
            counter = 0
            for x in splits:
                if x == '':
                    splits.remove(x)

            for token in splits:
                if token == 'INPUTS':
                    input_idx = counter
                if token == 'OUTPUTS':
                    output_idx = counter
                counter += 1
            for i in range(input_idx + 1, output_idx, 2):
                if splits[i] != '' and splits[i + 1] != '':
                    config_new["definitions"][op_name]["in"].update({splits[i]: splits[i + 1]})

            for j in range(output_idx + 1, len(splits), 2):
                if splits[j] != '' and splits[j + 1] != '':
                    config_new["definitions"][op_name]["out"].update({splits[j]: splits[j + 1]})


    print(config_new)


def col_letter(col_num):
    letter_dict = dict(enumerate(string.ascii_uppercase, 1))
    return letter_dict[col_num]


def get_val(sheet, col, row):
    """Returns the value of a cell."""
    return sheet[col + str(row)].value


def print_resource_dict(dic):
    """Prints a resource dictionary's key and values line by line."""
    for key in dic:
        print(key, dic[key])


def print_country_dict(dic):
    """Prints a country dictionary's key and values line by line."""
    for key in dic:
        dic2 = dic[key]
        print(key)
        for key2 in dic2:
            print('\t' + key2, dic2[key2])


if __name__ == '__main__':
    read_operator_def('data/operator_def_1.xlsx')