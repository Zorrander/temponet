import copy
import types
import itertools

class Policy:

    def __init__(self):
      self.threshold = 1000
      self.threshold2 = 1000
      self.valid_assignments = []
      #if func is not None:
        # self.evaluate = types.MethodType(func, self)

    def evaluate(self, base_solution):
        self.name = "balanced"
        steps = []
        for step, subgraph in base_solution._graph.nodes.data():
            steps.append(step)
        for repartition in list(itertools.product([False, True], repeat=len(steps))):
            working_time_h, iddle_time_h, working_time_r, iddle_time_r = self.compute_working_time(repartition, base_solution)
            working_time = abs(working_time_h - working_time_r)
            if working_time < self.threshold:
                self.threshold = working_time
                self.valid_assignments = [repartition]
                self.data = [[working_time_h, iddle_time_h, working_time_r, iddle_time_r]]
            elif working_time == self.threshold:
                self.valid_assignments.append(repartition)
                self.data.append([working_time_h, iddle_time_h, working_time_r, iddle_time_r])

    def compute_working_time(self, repartition, base_solution):
        ''' Simulate an execution to calculate each worker's working time '''
        working_time_h, iddle_time_h, working_time_r, iddle_time_r = (0,)*4
        human_waiting, robot_waiting = (False,)*2
        stn = copy.deepcopy(base_solution)
        while stn.available_steps():
            if (working_time_h <= working_time_r or robot_waiting) and not human_waiting:
                moves = [step for step in stn.available_steps() if not repartition[step-1]]
                if moves:
                    #working_time_h+=self.simulate_step(moves[0])
                    working_time_h+=20
                    stn.update_after_completion(moves[0], 0)
                    if robot_waiting:
                        robot_waiting = False
                        iddle_time_r+= abs(working_time_h- working_time_r)
                        working_time_r+= working_time_h - working_time_r
                else:
                    human_waiting = True
            elif (working_time_h > working_time_r or human_waiting) and not robot_waiting:
                moves = [step for step in stn.available_steps() if repartition[step-1]]
                if moves:
                    #working_time_r+=self.simulate_step(moves[0])
                    working_time_r+=30
                    stn.update_after_completion(moves[0], 0)
                    if human_waiting:
                        human_waiting = False
                        iddle_time_h+=abs(working_time_r - working_time_h)
                        working_time_h+=working_time_r - working_time_h
                else:
                    robot_waiting = True
            else:
                print("WORKING TIMES ARE: {} - {} - {} - {} - {} - {}".format(working_time_h, iddle_time_h, working_time_r, iddle_time_r, human_waiting, robot_waiting))
                print("Impossible case")
        return working_time_h, iddle_time_h, working_time_r, iddle_time_r

    def simulate_step(self, step):
        working_time=0
        for u, v, weight in step[1].edges(data='temporal_constraint'):
            if weight>0:
                working_time+=weight
        return working_time

def balanced_repartition(self, steps, stn):
    self.name = "balanced"
    for repartition in list(itertools.product([False, True], repeat=len(steps))):
        working_time_h, iddle_time_h, working_time_r, iddle_time_r = self.compute_working_time(repartition, stn)
        working_time = abs(working_time_h - working_time_r)
        if working_time < self.threshold:
            self.threshold = working_time
            self.valid_assignments = [repartition]
            self.data = [[working_time_h, iddle_time_h, working_time_r, iddle_time_r]]
        elif working_time == self.threshold:
            self.valid_assignments.append(repartition)
            self.data.append([working_time_h, iddle_time_h, working_time_r, iddle_time_r])

def capacity_based_repartition(self, steps, stn):
    self.name = "capacity"
    for repartition in list(itertools.product([False, True], repeat=len(steps))):
        working_time_h, iddle_time_h, working_time_r, iddle_time_r = self.compute_working_time(repartition, stn)
        working_time = working_time_h + working_time_r
        idle_time = iddle_time_h + iddle_time_r
        if working_time < self.threshold - 30 and not idle_time > self.threshold2 + 40:
            self.threshold = working_time
            self.threshold2 = idle_time
            self.valid_assignments = [repartition]
            self.data = [[working_time_h, iddle_time_h, working_time_r, iddle_time_r]]
        elif working_time < self.threshold + 30 and not idle_time > self.threshold2 + 40:
            self.valid_assignments.append(repartition)
            self.data.append([working_time_h, iddle_time_h, working_time_r, iddle_time_r])

def activity_based_repartition(self, steps, stn):
    self.name = "activity"
    for repartition in list(itertools.product([False, True], repeat=len(steps))):
        working_time_h, iddle_time_h, working_time_r, iddle_time_r = self.compute_working_time(repartition, stn)
        iddle_time = iddle_time_h + iddle_time_r
        working_time = working_time_h + working_time_r
        if iddle_time < self.threshold2 - 30  and not working_time > self.threshold + 40:
            self.threshold2 = iddle_time
            self.threshold = working_time
            self.valid_assignments = [repartition]
            self.data = [[working_time_h, iddle_time_h, working_time_r, iddle_time_r]]
        elif iddle_time < self.threshold2 + 30 and not working_time > self.threshold + 40:
            self.valid_assignments.append(repartition)
            self.data.append([working_time_h, iddle_time_h, working_time_r, iddle_time_r])

policies = [
    balanced_repartition,
    capacity_based_repartition,
    activity_based_repartition
]
