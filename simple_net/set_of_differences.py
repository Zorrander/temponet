from .policies import Policy
from .constraints import TemporalConstraint
from .assignments import FullTaskAssignment
from .update_rules import dynamic_backpropagation_rule_I, dynamic_backpropagation_rule_II

class SetOfDifferences(object):

    def __init__(self):
        self.valid_assignments = []

    def count_valid_assignments(self):
        return len(self.valid_assignments)

    def update(self, event, agent):
        print (self.count_valid_assignments())
        self.valid_assignments = [full_asg for full_asg in self.valid_assignments if full_asg.step_assignments[event]==agent]
        print (self.count_valid_assignments())

    def _update_policy(self, node , assignment_counter):
        u = node[0]
        v = node[1]
        weight = node[2]
        assignment = self.valid_assignments[assignment_counter]
        assignment.set_relation(u, v, 'temporal_constraint', weight)

    def initialize_set_of_differences(self, base_solution, policy):
        """ Compute all the valid full task assignments """
        result = []
        policy.evaluate(base_solution)
        print("Creating the set of differences:")
        for p in policy.valid_assignments:
            self.valid_assignments.append(self.create_component_solution(p, base_solution))

    def create_component_solution(self, policy, stn):
        """ Create a task assignment.

        The function transforms a policy into a task assignment.

        Parameters:
        -----------
        Dict policy
            A valid policy dict(task:agent).
        nx.DiGraph  stn
            The STN form of the problem.
        """
        result = FullTaskAssignment()
        for x in range(0, len(policy)):
            agent = "Robot" if policy[x] else "Human"
            result.step_assignments.update({(x+1):agent})
        return result

    def backpropagate_task_assign(self, constraints, base_solution, full_assignment):
        """ Propagate the effect of the constraints in the base solution.

        The function propagates the effect of these tightenings through the base solution.
        """
        is_consistent = True
        updated_constraints = []
        for task_assignment in constraints:
            found = False
            for asg in full_assignment.task_assignments:
                if task_assignment==asg[0]:
                    found = True
            if not found:
                 full_assignment.add_assignment(task_assignment)
            new_constraints = self.apply_dbp_rules(task_assignment, base_solution)
            for new_constraint in new_constraints:
                if new_constraint:
                    #task_assignment[1].append(new_constraint)
                    updated_constraints.append(new_constraint)
        if is_consistent and updated_constraints :
            self.backpropagate_task_assign(updated_constraints, base_solution, full_assignment)
            return True
        else:
            return False

    def apply_dbp_rules(self, task_assignment, stn):
        activities = []
        propagations=[]
        if not isinstance(task_assignment.time_constraint, int):
            activities.append(TemporalConstraint(task_assignment.event_a, task_assignment.event_b, time=task_assignment.time_constraint[1]))
            activities.append(TemporalConstraint(task_assignment.event_b, task_assignment.event_a, time=-task_assignment.time_constraint[0]))
        else:
            activities.append(task_assignment)
        for activity in activities:
            prop_I = dynamic_backpropagation_rule_I(activity, stn)
            prop_II= dynamic_backpropagation_rule_II(activity, stn)
            (propagations.append(prop_I) if prop_I is not None else None)
            (propagations.append(prop_II) if prop_II is not None else None)
        return propagations

    def __str__(self):
        counter = 1
        output = ""
        for assignment in self.valid_assignments:
            output+="===== ASSIGNMENT {} =====\n\n{}\n\n".format(counter, assignment)
            counter+=1
        return output
