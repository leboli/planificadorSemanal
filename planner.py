from entities import fixedActivity
from entities import dailyUtility
from entities import variableActivity

from pyomo.environ import *

class planner():

    def __init__(self, fixed_activities:list, variable_activities:list, number_of_ts:int):

        self.fixed_activities = fixed_activities
        self.variable_activities = variable_activities
        self.number_of_ts = number_of_ts
        self.model = ConcreteModel()



    def buildModel(self):
        print("Build model called.")

        # Create the concrete Pyomo model
        self.model = ConcreteModel()

        # Number of fixed and variable activities
        num_fixed = len(self.fixed_activities)
        num_variable = len(self.variable_activities)
        total_activities = num_fixed + num_variable

        activities = list(range(total_activities))  # IDs 0 to total_activities - 1
        time_slots = list(range(self.number_of_ts))  # Time slots (e.g. 0 to 167 for 168 hours)

        # Define sets in the model
        self.model.activities = Set(initialize=activities)
        self.model.time_slots = Set(initialize=time_slots)

        # Decision variable: x[a, t] = 1 if activity 'a' is assigned to time slot 't'
        self.model.x = Var(self.model.activities, self.model.time_slots, domain=Binary)

        # Fix x[a, t] = 1 for time slots assigned to fixed activities
        for index, fixed_activity in enumerate(self.fixed_activities):
            for t in fixed_activity.assigned_ts:
                self.model.x[index, t].fix(1)

        # Fix x[a, t] = 0 for time slots not allowed for variable activities
        var_offset = num_fixed
        for index, variable_activity in enumerate(self.variable_activities):
            for t in time_slots:
                if t not in variable_activity.allowed_ts:
                    self.model.x[var_offset + index, t].fix(0)

        # Restriction: Only one activity can be assigned to each time slot
        def one_activity_per_slot_rule(model, t):
            return sum(model.x[a, t] for a in model.activities) <= 1

        self.model.one_activity_per_slot = Constraint(self.model.time_slots, rule=one_activity_per_slot_rule)

        # ConstraintList is needed to dynamically add min/max slot constraints
        self.model.restricciones_min = ConstraintList()
        self.model.restricciones_max = ConstraintList()

        # Min/max number of slots assigned to each variable activity
        for index, variable_activity in enumerate(self.variable_activities):
            a_idx = var_offset + index
            self.model.restricciones_min.add(
                sum(self.model.x[a_idx, t] for t in time_slots) >= variable_activity.min_slots
            )
            self.model.restricciones_max.add(
                sum(self.model.x[a_idx, t] for t in time_slots) <= variable_activity.max_slots
            )

        # Auxiliary variables: h_adk[a, d, k] is the amount of time assigned to activity 'a'
        # on day 'd', in segment 'k' of the utility function
        self.model.h_adk = Var(
            range(num_variable),      # Index of variable activities
            range(7),                 # Days of the week (0 = Monday)
            range(self.max_segments), # Max number of segments across all activities
            domain=NonNegativeReals
        )

        for a_idx, variable_activity in enumerate(self.variable_activities):
            global_idx = len(self.fixed_activities) + a_idx
            min_len = variable_activity.min_block_len
            max_len = variable_activity.max_block_len

            for t in range(self.number_of_ts):
                if t + min_len <= self.number_of_ts:
                    self.model.fragmentation_restrictions.add(
                        sum(self.model.x[global_idx, t + j] for j in range(min_len)) >=
                        min_len * self.model.start_block[global_idx, t]
                    )
                if t + max_len <= self.number_of_ts:
                    self.model.fragmentation_restrictions.add(
                        sum(self.model.x[global_idx, t + j] for j in range(max_len + 1)) <=
                        max_len * self.model.start_block[global_idx, t]
                    )
            
        self.model.transition = Var(self.model.activities, self.model.activities, self.model.time_slots, domain=Binary)

        self.model.transition_def = ConstraintList()

        for t in range(1, self.number_of_ts):
            for a in self.model.activities:
                for b in self.model.activities:
                    if a != b:
                        self.model.transition_def.add(
                            self.model.transition[a, b, t] >= self.model.x[a, t-1] + self.model.x[b, t] - 1
                        )
        
        # Objective function: maximize total utility based on piecewise utility segments
        def objective_rule(model):
            total_utility = 0
            total_penalty = 0

            for a_idx, variable_activity in enumerate(self.variable_activities):
                for d in range(7):
                    segments = variable_activity.utility_segments[d]
                    for k, (start, end, util) in enumerate(segments):
                        h_adk = model.h_adk[a_idx, d, k]
                        total_utility += util * h_adk

            for a in model.activities:
                for b in model.activities:
                    if a != b:
                        for t in model.time_slots:
                            if (a, b) in self.penalties:
                                total_penalty += self.penalties[(a, b)] * model.transition[a, b, t]

            return total_utility - total_penalty

        self.model.obj = Objective(rule=objective_rule, sense=maximize)





        
    def solve():

        print("solve called.")
        return (123.45,{(1,30):1}) #(utility, dict of all x_{a,t})