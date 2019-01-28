from pm4py.algo.discovery.dfg.utils.dfg_utils import add_to_most_probable_component
from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act
from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree_imdfa import Subtree


class SubtreeB(Subtree):
    def check_if_comp_is_completely_unconnected(self, conn1, conn2):
        """
        Checks if two connected components are completely unconnected each other

        Parameters
        -------------
        conn1
            First connected component
        conn2
            Second connected component

        Returns
        -------------
        boolean
            Boolean value that tells if the two connected components are completely unconnected
        """
        for act1 in conn1:
            for act2 in conn2:
                if ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                        act1 in self.ingoing and act2 in self.ingoing[act1])):
                    return False
        return True

    def check_par_cut(self, conn_components):
        """
        Checks if in a parallel cut all relations are present

        Parameters
        -----------
        conn_components
            Connected components
        """
        i = 0
        while i < len(conn_components):
            conn1 = conn_components[i]
            j = i + 1
            while j < len(conn_components):
                conn2 = conn_components[j]
                for act1 in conn1:
                    for act2 in conn2:
                        if not ((act1 in self.outgoing and act2 in self.outgoing[act1]) and (
                                act1 in self.ingoing and act2 in self.ingoing[act1])):
                            if self.check_if_comp_is_completely_unconnected(conn1, conn2):
                                conn_components[i] = list(set(conn_components[i] + conn_components[j]))
                                del conn_components[j]
                                continue
                            else:
                                return False
                j = j + 1
            i = i + 1
        return True

    def detect_cut(self, second_iteration=False):
        """
        Detect generally a cut in the graph (applying all the algorithms)
        """
        if self.dfg:
            # print("\n\n")
            par_cut = self.detect_parallel_cut()
            conc_cut = self.detect_concurrent_cut()
            seq_cut = self.detect_sequential_cut()
            loop_cut = self.detect_loop_cut()

            if conc_cut[0]:
                for comp in conc_cut[1]:
                    new_dfg = filter_dfg_on_act(self.dfg, comp)
                    self.detected_cut = "concurrent"
                    self.children.append(SubtreeB(new_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                                  noise_threshold=self.noise_threshold))
            else:
                if seq_cut[0]:
                    self.detected_cut = "sequential"
                    for child in seq_cut[1]:
                        dfg_child = filter_dfg_on_act(self.dfg, child)
                        self.children.append(
                            SubtreeB(dfg_child, self.initial_dfg, child, self.counts, self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold))
                else:
                    if par_cut[0]:
                        union_acti_comp = set()
                        for comp in par_cut[1]:
                            union_acti_comp = union_acti_comp.union(comp)
                        diff_acti_comp = set(self.activities).difference(union_acti_comp)

                        for act in diff_acti_comp:
                            par_cut[1] = add_to_most_probable_component(par_cut[1], act, self.ingoing, self.outgoing)

                        for comp in par_cut[1]:
                            new_dfg = filter_dfg_on_act(self.dfg, comp)
                            self.detected_cut = "parallel"
                            self.children.append(
                                SubtreeB(new_dfg, self.initial_dfg, comp, self.counts, self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold))
                    else:
                        if loop_cut[0]:
                            self.detected_cut = "loopCut"
                            for child in loop_cut[1]:
                                dfg_child = filter_dfg_on_act(self.dfg, child)
                                self.children.append(
                                    SubtreeB(dfg_child, self.initial_dfg, child, self.counts, self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold))
                        else:
                            if self.noise_threshold > 0:
                                if not second_iteration:
                                    self.initialize_tree(self.dfg, self.initial_dfg, None, second_iteration=True)
                            else:
                                pass
                            self.detected_cut = "flower"
        else:
            self.detected_cut = "base_concurrent"
