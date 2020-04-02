import copy
import json
import networkx as nx
from os.path import expanduser
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt

DEFAULT_HUMAN_EXECUTION_TIME = (10, 20)
DEFAULT_ROBOT_EXECUTION_TIME = (20, 30)

class BaseSolution():
    def __init__(self):
        self._graph = nx.DiGraph()

    def relax_network(self):
        """ Relax the temporal constraints.

        The disjunctive constraints can be combined by taking only the lower and upper bounds.
        """
        for u, v, weight in self._graph.edges(data='temporal_constraint'):
            if not u=="Start":
                human_expectations = weight[0]
                robot_expectations = weight[1]
                self.set_relation(u, v, 'temporal_constraint', (min(human_expectations[0], robot_expectations[0]), max(human_expectations[1], robot_expectations[1])))

    def transform_dispatchable_graph(self, method="apsp"):
        """ Compute the Base Solution.

        The Base Solution consists in a dispatchable graph.
        One-step propagation makes explicit all constraints on neighboring events.
        """
        if method == "apsp":
            print("Construct distance graph:")
            self.construct_distance_graph()
            print("Calculating the APSP form of the graph:")
            self.all_pairs_shortest_paths()
            #nx.write_graphml(self._graph, "apsp.graphml")
            #print("Removing dominated edges:")
            #self.prune_redundant_constraints()
            #self.graph_to_json()
        elif method == "chordal":
            pass

    def model_temporal_problem(self, sem_collection):
        """ Converts the problem into an STN

        Translate the lists of steps and their constraints into timepoints and links between them.
        """
        not_relevant = ["<http://www.w3.org/2002/07/owl#Thing>", "<http://www.w3.org/2002/07/owl#Resource>"]
        action_class = ["<http://onto-server-tuni.herokuapp.com/Panda#ManipulationTask>", "<http://onto-server-tuni.herokuapp.com/Panda#Event>"]
        object_class = ["<http://onto-server-tuni.herokuapp.com/Panda#Object>"]
        for triple_a in sem_collection.list_triples:
            if triple_a.predicate=="<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" and triple_a.object in action_class:
                action_type = [triple_b for triple_b in sem_collection.list_triples if triple_a.subject == triple_b.subject]
            if triple_a.predicate=="<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>" and triple_a.object in object_class:
                object_type = [triple_b for triple_b in sem_collection.list_triples if triple_a.subject == triple_b.subject]
            break
        self.add_event(action_type, object_type)

    def timepoints(self):
        """Get the timepoints of the network."""
        return [task for task in self._graph.nodes(data=True) if not task[0] == "Start"]

    def update_after_completion(self, event, time):
        self._graph.nodes[event]['is_done'] = True


    def find_available_steps(self, current_time):
        """Get the available events in the network."""
        return [(step, data['object']) for step, data in self._graph.nodes.data() if not data['is_done']]

    def find_predecessor_graph(self):
        pass

    def retrieve_subgraph(self, step):
        return self._graph.subgraph( [n for n,attrdict in self._graph.node.items() if not n == "Start" and attrdict['step'] == step ] )

    def are_available(self, events):
        return False if False in map(self._is_available, events) else True

    def get_event(self, event, data=False):
        """Return the value for an attribute of the node 'event' if data. All the attributes otherwise."""
        return self._graph.nodes(data=data)[event] if data else self._graph.nodes(data=True)[event]

    def add_event(self, action, object, is_done=False):
        """Create a new node in the graph."""
        id = nx.number_of_nodes(self._graph)+1
        self._graph.add_node(action, object=object, is_done=is_done, is_claimed=False)
        return id

    def set_event(self, name, data, value):
        """ Set the attribute 'data' of the node 'name' to 'value'"""
        nx.set_node_attributes(self._graph, value, data)

    def has_relation(self, u, v):
        """ Return the value of an edge. False if it does not exist."""
        return self._graph.edges[u, v]['temporal_constraint'] if self._graph.has_edge(u, v) else False

    def set_relation(self, u, v, data, value):
        """Set the value of an edge. Create if it does not exist yet."""
        if not self.has_relation(u, v):
            self._graph.add_edge(u, v)
        self._graph.edges[u, v][data] = value

    def adjacent_nodes(self, node=False):
        """Return the list of events related to the argument"""
        return list(self._graph.adj[node[0]]) if type(node) is tuple else list(self._graph.adj[node])

    def construct_distance_graph(self):
        """ Translate the constraint form representation into its associated distance graph.

        The distance graph indicates the same interval as the constraint but yields two equivalent inequalities.
        """
        new_edges = []
        for u, v, weight in self._graph.edges(data='temporal_constraint'):
            lower_bound = weight[0] if not isinstance(weight, int) else weight
            upper_bound = weight[1] if not isinstance(weight, int) else weight
            self.set_relation(u, v, 'temporal_constraint', upper_bound)
            self.set_relation(v, u, 'temporal_constraint', -lower_bound)
            new_edges.append((v, u, -lower_bound))

    def all_pairs_shortest_paths(self):
        """ Compute all pairs shortest paths with Floyd-Warshall algorithm

        Computes a fully-connected network, with binary constraints relating each pair of events.
        """
        distance = nx.floyd_warshall(self._graph, weight='temporal_constraint')
        for node_a in distance:
            for node_b in distance[node_a]:
                if not(node_a==node_b or (node_a, node_b) in list(self._graph.edges)):
                    self.set_relation(node_a, node_b, 'temporal_constraint', distance[node_a][node_b])

    def prune_redundant_constraints(self):
        """ Remove dominated edges.

        Remove dominated edges to make STN dispatchable.
        """
        graph = copy.deepcopy(self._graph)
        for A, B, weight in self._graph.edges(data='temporal_constraint'):
            for C in set(self._graph.successors(A)).intersection(self._graph.successors(B)):
                a_c = self.has_relation(A, C)
                b_c = self.has_relation(B, C)
                if self.is_dominated(a_c, b_c, weight):
                    try:
                        graph.remove_edge(A, C)
                    except:
                        pass
                    break
        self._graph = graph

    def is_dominated(self, edge_ac, edge_bc, edge_ab):
        if (edge_ac > 0 and edge_bc > 0) or (edge_ac < 0 and edge_ab < 0):
            return True if edge_ac == edge_ab + edge_bc else False
        else:
            return False

    def graph_to_json(self):
        filename = input("Enter a file name to save the plan: ")
        filename = expanduser("~")+"/"+filename+".owl"
        d = json_graph.node_link_data(self._graph)  # node-link format to serialize
        # write json
        file = open(filename, "w+")
        json.dump(d, file)

    def display_graph(self, title=""):
        pos = nx.shell_layout(self._graph)
        plt.title(title)
        nx.draw_networkx_nodes(self._graph, pos, cmap=plt.get_cmap('jet'), node_size = 500)
        nx.draw_networkx_labels(self._graph, pos)
        nx.draw_networkx_edges(self._graph, pos, edge_color='r', arrows=True)
        nx.draw_networkx_edge_labels(self._graph, pos=nx.spring_layout(self._graph))
        plt.show()

    def print_graph(self):
        print(list(self._graph.nodes(data=True)))
        print(list(self._graph.edges(data=True)))
