# Project in AI post break deliverable - Group 6
<h1>Jake Boersma, Charlie MacVicar, Ohad Beck, Colin Moody</h1>

<h2>How to Run the Code</h2>
1. Make sure you have the following packages installed (install with pip):
    - matplotlib
    - numpy
    - openpyxl
    - scipy
    - setuptools
    - six
    
2. Create an initial state using the following formatting: initial_state_<>.py. Start with '1' (i.e. initial_state_1.py) and increase for your desired number of test files.
    - File should be located under /data/initial_state_<>.py

3. Open scheduler.py and define the following class constant variables (at the top of the file):
    - NUM_TEST_FILES -           however many test files/initial states you are scheduling for (1 to n)
    - DEPTH_BOUND -              depth bound of the anytime, depth-bound, forward searching scheduler
    - NUM_OUTPUT_SCHEDULES -     how many schedules to create per initial state (i.e. different paths to attempt)
    - MAX_FRONTIER_SIZE -        maximum size of frontier - limits number of scheduling possibilities

4. Run function scheduler.py using python 3

        python3 scheduler.py

5. Review output in output_<>.csv. There will be a separate file for each initial state you created.
  

<h2>Notes</h2>
- The search algorithm is all run through the main function in scheduler.py. We hold an object WorldStateManager which traverses through the past, present, and future states. To search through these states, we call go_to_next_state if there are output schedules left to be scheduled. go_to_next_state is the main function that traverses through the search. The output is processed through scheduler.py.
State handling
- world_objects.py keeps a single state. We encabsulate the state in a World object and we also have a country object that is used to keep the state in the World object. Each country and world have their respective functions as seen in the script. This script also containrs the different parameters associated with the world such as gamma, x, K, and C. These can be easily experimented with through easy changes.
- data_import.py imports all the data from the excel sheets and creates the necessary data structures to hold all the data from the input excel sheets.
