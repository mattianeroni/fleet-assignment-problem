import collections


class Fleet:
    def __init__(self, id, maxshare, maxcapacity, maxvolume, minvolume):
        self.id = id
        self.maxshare = maxshare
        self.maxcapacity = maxcapacity
        self.maxvolume = maxvolume
        self.minvolume = minvolume
        # Attributes used by the algorithm
        self.customers = collections.deque()
        self.capacity_level = 0
        self.volume_level = 0
