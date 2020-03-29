"""
Dynamic Backpropagation Rules module.

A starting point for resolving the issue of Dynamic Controllability is  to  consider
triangular STNU networks,  i.e.,  networks involving three timepoints and including a contingent
link.

Recursively applying these rules, when an edge is tightened in a dispatchable distance graph,
will either expose an inconsistency or result in a dispatchable graph. It only requires a
subset of the edges to be checked to ensure that the modified constraint is consistent,
rather than all edges when the all-pairs graph is computed.

Reference
---------

P. Morris, N. Muscettola, and T. Vidal, "Dynamic Control Of Plans With Temporal Uncertainty".
"""
from jena_models.constraints import TemporalConstraint

DEFAULT_HUMAN_EXECUTION_TIME = (10, 20)
DEFAULT_ROBOT_EXECUTION_TIME = (20, 30)


def dynamic_backpropagation_rule_I(temporal_constraint, base_solution):
    """docstring for TemporalConstraint."""
    A = temporal_constraint.event_a
    B = temporal_constraint.event_b
    neighbors = [i for i in base_solution.adjacent_nodes(B) if not A==i]
    for C in neighbors:
        if has_positive_constraint_change(base_solution, temporal_constraint) and is_negative_constraint(base_solution, B, C):
                new_weight = temporal_constraint.time_constraint + base_solution.has_relation(B, C)
                current_weight = base_solution.has_relation(A, C)
                if not current_weight or (new_weight < current_weight):
                    return TemporalConstraint(A, C, new_weight)

def dynamic_backpropagation_rule_II(temporal_constraint, base_solution):
    """docstring for TemporalConstraint."""
    B = temporal_constraint.event_a
    A = temporal_constraint.event_b
    neighbors = [i[0] for i in base_solution.timepoints if (B in base_solution.adjacent_nodes(i[0]) and not A==i[0])]
    for C in neighbors:
        if has_negative_constraint_change(base_solution, temporal_constraint) and is_positive_constraint(base_solution, C, B):
            weight = temporal_constraint.time_constraint + base_solution.has_relation(C, B)
            if not base_solution.has_relation(C, A) or (weight < base_solution.has_relation(C, A)):
                return TemporalConstraint(C, A, weight)

def has_positive_constraint_change(base_solution, temporal_constraint):
    new_constraint = temporal_constraint.time_constraint
    original_constraint = base_solution.has_relation(temporal_constraint.event_a, temporal_constraint.event_b)
    if original_constraint:
        return True if new_constraint > 0 and not(new_constraint==original_constraint) else False
    else:
        return True if new_constraint > 0 else False

def has_negative_constraint_change(base_solution, temporal_constraint):
    new_constraint = temporal_constraint.time_constraint
    original_constraint = base_solution.has_relation(temporal_constraint.event_a, temporal_constraint.event_b)
    if original_constraint:
        return True if new_constraint < 0 and not(new_constraint==original_constraint) else False
    else:
        return True if new_constraint < 0 else False

def is_positive_constraint(base_solution, u, v):
    return True if base_solution.has_relation(u, v) > 0 else False

def is_negative_constraint(base_solution, u, v):
    return True if base_solution.has_relation(u, v) < 0 else False

incremental_update_rules = [
    dynamic_backpropagation_rule_I,
    dynamic_backpropagation_rule_II
]
