# Project in AI post break deliverable - Group 6
<h1>Jake Boersma, Charlie MacVicar, Ohad Beck, Colin Moody</h1>
<h2>Instructions to run code</h2>
  The input files needed to run the scheduler are operator_def_1.xlsx and resources_1.xlsx in the data folder. There are also 2 additional folders needed in the data folder, data/initial_states/... and data?parameter_sets/.... Both of these folders must hold at least one file that follows the schema. To run the scheduler you just need to run the scheduler.py file which has the main function which calls upon everything else.
<h2>Search algorithm </h2>
  The search algorithm is all run through the main function in scheduler.py. We hold an object WorldStateManager which traverses through the past, present, and future states. To search through these states, we call go_to_next_state if there are output schedules left to be scheduled. go_to_next_state is the main function that traverses through the search. The output is processed through scheduler.py.
<h2>State handling</h2>
  world_objects.py keeps a single state. We encabsulate the state in a World object and we also have a country object that is used to keep the state in the World object. Each country and world have their respective functions as seen in the script. This script also containrs the different parameters associated with the world such as gamma, x, K, and C. These can be easily experimented with through easy changes.
<h2>Data import</h2>
  data_import.py imports all the data from the excel sheets and creates the necessary data structures to hold all the data from the input excel sheets.
