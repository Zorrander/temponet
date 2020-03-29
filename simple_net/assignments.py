from .constraints import TemporalConstraint

class FullTaskAssignment(object):
    """docstring for FullTaskAssignment."""

    def __init__(self):
        self.task_assignments = []
        self.feasible = True

    def add_assignment(self, *argv):
        """ Add an action assignment into a full task assignment."""
        new_constraint = argv[0] if len(argv)==1 else TemporalConstraint(argv[0], argv[1], argv[2], argv[3])
        self.task_assignments.append((new_constraint, []))

    def add_constraint_change(self, new_constraint, task_assignment):
        for x in self.task_assignments:
            if x[0] == task_assignment:
                x[1].append(new_constraint)

    @property
    def feasible(self):
        return self._feasible

    @feasible.setter
    def feasible(self, feasible):
        self._feasible = feasible

    def __str__(self):
        output = "===== ASSIGNMENT ====="
        for assignment in self.task_assignments:
            output+="\n{}\n---------------\n{}".format(assignment[0], assignment[1])
        return output
