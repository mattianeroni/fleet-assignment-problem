class Customer:
    def __init__(self, id, demand):
        self.id = id
        self.demand = demand
        self.assigned = False
        self.assigned_qty = 0
