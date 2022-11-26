from typing import List, Dict


class Role(object):
    activities: List[str]
    originator_importance = Dict[str, float]

    def __init__(self, activities: List[str], originator_importance: Dict[str, float]):
        self.activities = activities
        self.originator_importance = originator_importance

    def __repr__(self):
        return "Activities: " + str(self.activities) + " Originators importance " + str(self.originator_importance)

    def __str__(self):
        return "Activities: " + str(self.activities) + " Originators importance " + str(self.originator_importance)
