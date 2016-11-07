"""
---
Charles Arvey
AI Assignment # 4
Hill Climbing and Simulated Annealing to solve the Maximum Independent Set problem
---

--------------------------------------------
PROJECT DESCRIPTION
--------------------------------------------

Problem:
I have chosen to implement the hill climbing and simulated annealing algorithms to solve the max independent set
problem. Hill climbing will find a local maximum, while simulated annealing will attempt to find a global maximum but
is not guaranteed to find one.

Data Structures Used:
I chose to base my program around a Puzzle class that stores all the data structures and logic used. The graph itself
is represented through the networkx library (https://networkx.github.io/). This isn't used to solve the problem, but
rather to abstract away the logic of having to find children nodes and stuff of that sort in a data structure of my own.

The networkx graph gets data loaded into it through the parsing method, load_file. Following that, either available
algorithm can be ran on it in a non destructive manner. That is, the original graph itself is never modified and can
therefor be used over multiple iterations. The algorithm to run is determined by the user through the options passed
into the file.

--------------------------------------------
PROJECT SETUP AND EXECUTION
--------------------------------------------
Note that this script is written in python 3.5

The requirements for this script can be found in a separate file alongside this one called 'requirements.txt'.
To install the requirements, you can run (requires pip):

pip install -r requirements.txt

For HW submission I am commenting out matplotlib and removing its requirement from requirements.txt

Usage:
python mis.py --file FILE [--hill] [--sim] [--time TIME]

Arguments:
    - The --hill argument will run with the Hill Climbing algo (cannot be used with --sim)
    - The --sim argument will run with the Simulated Annealing algo (cannot be used with --hill)
    - The optional --time argument can be used to run the algorithm N number of times.

EX command to run simulated annealing on 'ran50.txt':
python mis.py --file ran50.txt --sim

EX command to run simulated annealing on 'samples/ran50.txt' 5 times:
python mis.py --file samples/ran50.txt --sim --time 5

The command above will output:
Running simulated Annealing on: samples/ran50.txt
Independent Set: ['39', '10', '42', '32', '26', '13', '36', '16', '47']
Length: 9
------------
Running simulated Annealing on: samples/ran50.txt for 5 iterations
Times: [0.015460550002899254, 0.018208978999609826, 0.01825022000048193, 0.015277151996997418, 0.018937782999273622]
Average time: 0.01722693679985241


"""


# import matplotlib
import networkx as nx
import random
import argparse
import timeit

# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt


parser = argparse.ArgumentParser("Specify a file, and either hill climbing or simulated annealing. A time option can also be specified for timing the function over N calls.")
parser.add_argument("--file", type=str, required=True,
                    help="graph file to parse")
parser.add_argument("--hill", dest="hill", action="store_true",
                    help="Run with hill climbing")
parser.add_argument("--sim", dest="sim", action="store_true",
                    help="Run with simulated annealing")
parser.add_argument("--time", dest="time", type=int,
                    help="Run the algo N times and return times and an avg")

parser.set_defaults(hill=False)
parser.set_defaults(sim=False)

class Puzzle:

    def __init__(self):
        self.graph = nx.Graph()

    def load_file(self, file_path):
        file = open(file_path)

        config_line = file.readline().strip("\n").split("\t")
        num_nodes = config_line[0]
        num_edges = config_line[1]

        node_connections = [conn.strip("\n").replace("   ", "\t").split("\t") for conn in file.readlines()]
        for conn in node_connections:
            # conn will be of the form ['node1', 'node2']
            node1 = conn[0]
            node2 = conn[1]

            self.graph.add_edge(node1, node2)

    def load_edges(self, node_pair):
        """
        Connects two nodes with an edge. This is a separate method so that adding in edges can be done
        outside of the load_file method. In case I decide to try dynamically creating graphs with some method,
        this separation will be useful.

        :param node_pair: a list of the two nodes that should be connected. e.g. [node1, node2]
        :return:
        """
        self.graph.add_edge(node_pair[0], node_pair[1])

    # commented out for HW submission
    # def draw(self, *args, **kwargs):

        # nx.draw(self.graph, **kwargs)
        # plt.show()

    def local_independent_maximum(self):
        """
        Find a local independent max set with a worst case time of O(n)
        :return: the set of all
        """

        # set of all independent nodes
        i_set = []

        # work off of a copy of the entire graph
        graph = self.graph.copy()

        # get list of all nodes in the graph
        nodes = graph.nodes()

        # perform this until
        while nodes:
            iter_nodes = iter(nodes)
            node = next(iter_nodes)
            i_set.append(node)

            children = list(nx.all_neighbors(graph, node))
            graph.remove_node(node)
            graph.remove_nodes_from(children)

            nodes = graph.nodes()

        return i_set

    def hill_climb(self, prob=None, prob_rate=None):
        """
        Use the local independent maximum method to find local maxes of different sizes until one is found

        Note about using this function with simulated annealing: by setting prob equal to x + prob_rate * c where
        x is some probability and c is a constant, then this loop will escape the first c number of local maximums
        (at the risk of escaping the global one and iterating through the rest of the nodes present)

        :param prob: if present then use this as the probability that the function will escape a local maximal
        :param prob_rate: the rate at which prob should decrease.
        :return:
        """
        max_independent_set = None
        node_count = len(self.graph.nodes())

        # as nodes will be a randomly ordered list of all the nodes, we are starting from random points in the graph
        # on each iteration of local_independent_maximum
        for i in range(node_count):
            max_set = self.local_independent_maximum()
            if not max_independent_set:
                max_independent_set = max_set

            if len(max_set) > len(max_independent_set):
                max_independent_set = max_set

            else:
                # if prob is not None, then hill_climb is being ran by simulated annealing
                if prob:
                    rand_num = random.random()
                    if rand_num > prob:
                        return max_independent_set

                    else:
                        prob -= prob_rate

                else:
                    return max_independent_set


    def simulated_annealing(self, prob=2, prob_rate=.2):
        """
        Use the hill_climb method with a continuously decreasing chance of breaking the loop to return a max set
        :param prob: the probability that the hill climb will escape a local maximal
        :return:
        """
        return self.hill_climb(prob, prob_rate)


    @staticmethod
    def pretty_data(independent_set):
        return "Independent Set: %s\nLength: %s" % (independent_set, len(independent_set))


options = parser.parse_args()

# ensure that the options have been input correctly
if options.hill and options.sim:
    raise AttributeError("Choose to run hill climbing (--hill) or simulated annealing (--sim)")

if not options.hill and not options.sim:
    raise AttributeError("You must choose to run hill climbing (--hill) or simulated annealing (--sim)")


graph = Puzzle() # init the Puzzle instance that will hold our graph and logic
graph.load_file(options.file) # load in the file passed in from the user

algorithm = None
func = None

if options.hill:
    algorithm = "Hill Climbing"
    func = graph.hill_climb

elif options.sim:
    algorithm = "simulated Annealing"
    func = graph.simulated_annealing


# run the hill climbing or simulated annealing
max_set = func()

# print out the independent set and length all pretty like
print("Running %s on: %s" % (algorithm, options.file))
pretty_data = Puzzle.pretty_data(max_set)
print(pretty_data)

# if the time option is present, then run func "time" number of iterations and get avg time
if options.time:
    print("------------")
    print("Running %s on: %s for %s iterations" % (algorithm, options.file, options.time))
    timer = timeit.Timer(stmt=func)
    times = timer.repeat(options.time, 1)
    avg = sum(times) / len(times)

    print("Times: %s\nAverage time: %s" % (times, avg))


# graph.draw(with_labels=True)