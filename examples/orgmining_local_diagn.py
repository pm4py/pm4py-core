import pm4py
import os
from pm4py.algo.organizational_mining.local_diagnostics import algorithm as local_diagnostics


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    ld = local_diagnostics.apply_from_group_attribute(log, parameters={local_diagnostics.Parameters.GROUP_KEY: "org:group"})
    # GROUP RELATIVE FOCUS (on a given type of work) specifies how much a resource group performed this type of work
    # compared to the overall workload of the group. It can be used to measure how the workload of a resource group
    # is distributed over different types of work, i.e., work diversification of the group.
    print("\ngroup_relative_focus")
    print(ld["group_relative_focus"])
    # GROUP RELATIVE STAKE (in a given type of work) specifies how much this type of work was performed by a certain
    # resource group among all groups. It can be used to measure how the workload devoted to a certain type of work is
    # distributed over resource groups in an organizational model, i.e., work participation by different groups.
    print("\ngroup_relative_stake")
    print(ld["group_relative_stake"])
    # GROUP COVERAGE with respect to a given type of work specifies the proportion of members of a resource group that
    # performed this type of work.
    print("\ngroup_coverage")
    print(ld["group_coverage"])
    # GROUP MEMBER CONTRIBUTION of a member of a resource group with respect to the given type of work specifies how
    # much of this type of work by the group was performed by the member. It can be used to measure how the workload
    # of the entire group devoted to a certain type of work is distributed over the group members.
    print("\ngroup_member_contribution")
    print(ld["group_member_contribution"])


if __name__ == "__main__":
    execute_script()
