class ProcessTree(object):
    def __init__(self):
        """
        Constructor
        """
        # reset variables
        self.operator = 0
        self.children = 0
        self.current_lev_elems = 0
        self.flower = False
        self.base_case = False

        self.operator = ""
        self.children = []
        self.current_lev_elems = []

    def __repr__(self):
        ret_list = ["ProcessTree: "]
        ret_list.append(self.operator + "(")
        els_count = 0
        if not self.base_case:
            for child in self.children:
                if els_count > 0:
                    ret_list.append(",")
                ret_list.append(repr(child))
                els_count = els_count + 1
        for trans in self.current_lev_elems:
            if els_count > 0:
                ret_list.append(",")
            ret_list.append(repr(trans))
        if self.base_case and self.flower:
            ret_list.append(")")
        ret_list.append(")")
        return "".join(ret_list)

    def add_transition(self, name, label):
        proceed_to_add = True
        if label is None:
            if "skip" in name:
                added_skip_trans = [x for x in self.current_lev_elems if "skip" in x.name]
                if added_skip_trans:
                    proceed_to_add = False
            if "loop" in name:
                added_skip_trans = [x for x in self.current_lev_elems if "loop" in x.name]
                if added_skip_trans:
                    proceed_to_add = False
        if proceed_to_add:
            self.current_lev_elems.append(PT_Transition(name, label))

class PT_Transition(object):
    def __init__(self, name, label):
        self.name = name
        self.label = label

    def __repr__(self):
        if self.label is not None:
            return self.label
        return self.name