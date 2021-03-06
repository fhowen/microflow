import Constants
import networkx as nx

class Compu:
    __slots__ = ['compuName', 'parentReducer', 'parentJob', 'compuID', \
                 'locationID', 'compuSize', 'startTime', 'finishTime', \
                 'remainSize', 'currentCps']
                 
    TotalCompuNum = 0

    def __init__(self, compu_name, parent_reducer):
        self.compuName = compu_name
        self.parentReducer = parent_reducer
        self.parentJob = self.parentReducer.parentJob
        self.compuID = Compu.TotalCompuNum
        Compu.TotalCompuNum += 1
    
    def set_attributes(self, location_id, compu_size):
        self.locationID = location_id
        self.compuSize = compu_size
        self.startTime = Constants.MAXTIME
        self.finishTime = Constants.MAXTIME
        self.remainSize = compu_size
        self.currentCps = 0

    def is_ready(self):
        #for p_node in nx.ancestors(self.parentReducer.dag, self):
        for p_node in self.parentReducer.dag.pred[self]:
            if p_node.remainSize <= Constants.ZERO:
                continue
            else:
                return False
        return True