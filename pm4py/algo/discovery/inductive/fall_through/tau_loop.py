from pm4py.algo.discovery.inductive.fall_through.strict_tau_loop import StrictTauLoop
from pm4py.util.compression import util as comut
from pm4py.util.compression.dtypes import UCL


class TauLoop(StrictTauLoop):

    @classmethod
    def _get_projected_log(cls, log: UCL):
        start_activities = comut.get_start_activities(log)
        proj = []
        for t in log:
            x = 0
            for i in range(1, len(t)):
                if t[i] in start_activities:
                    proj.append(t[x:i])
                    x = i
            proj.append(t[x:len(t)])
        return proj
