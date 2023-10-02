# extension to basic DCR graph to include events

from pm4py.objects.dcr.obj import DCR_Graph


class RoleDCR_Graph(DCR_Graph):
    def __init__(self, template, log):
        super().__init__(template, log)
        self.__principals = template['principals']
        self.__roles = template['roles']
        self.__rolesAssignment = template['roleAssignment']

    @property
    def principals(self):
        return self.__principals

    @property
    def roles(self):
        return self.__roles

    @property
    def roleAssignment(self):
        return self.__rolesAssignment
