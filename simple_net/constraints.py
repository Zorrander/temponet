class TemporalConstraint(object):
    """docstring for TemporalConstraint."""

    def __init__(self, event_a, event_b, time, agent=False):
        self.event_a = event_a
        self.event_b = event_b
        self.agent = agent
        if isinstance(time, int) or event_a == "Start" or event_b == "Start":
            self.time_constraint = time
        else:
            self.time_constraint = time[0] if agent=="Human" else time[1]
        self.execution_time = False

    @property
    def time_constraint(self):
        """Get the available events in the network."""
        return self._time_constraint

    @time_constraint.setter
    def time_constraint(self, time):
        self._time_constraint = time

    def __eq__(self, t_constraint):
        return True if (t_constraint.event_a == self.event_a and t_constraint.event_b == self.event_b) else False

    def __gt__(self, t_constraint):
        return self.time_constraint > t_constraint.time_constraint

    def __str__(self):
        t = self.time_constraint
        return "{} == {} --> {}({})".format(self.event_a, self.event_b, t, self.agent) if isinstance(t, int) else "{} == {} --> {}-{}({})".format(self.event_a, self.event_b, t[0], t[1], self.agent)
