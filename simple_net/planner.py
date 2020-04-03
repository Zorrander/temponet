import os
import csv
from .base_solution import BaseSolution
from .set_of_differences import SetOfDifferences

class Planner(object):
    """Compile a plan.

    Converts the information retrieved from the knowledge base into a
    Multi-agent Disjunctive Temporal Constraint Network With Uncertainty
    """

    def __init__(self, policy=None):
        self.base_solution = BaseSolution()
        #self.set_of_differences = SetOfDifferences()
        self.planning_policy = policy

    def create_plan(self, sem_collection):
        """ Model a temporal plan """
        try:
            self.base_solution.model_temporal_problem(sem_collection)
            self.base_solution.relax_network()
            self.base_solution.transform_dispatchable_graph()
            return self.base_solution
        except Exception as e:
            print(e)

    def find_available_steps(self, time):
        try:
            return self.base_solution.find_available_steps(time)
        except Exception as e:
            print(e)

    def print_plan(self):
        self.base_solution.print_graph()

    def export_data(self):
        with open(os.path.join("./", self.planning_policy.name + '.csv'), mode='w') as working_times:
            data_csv = csv.writer(working_times, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for full_assignment in self.planning_policy.data:
                data_csv.writerow(full_assignment)
