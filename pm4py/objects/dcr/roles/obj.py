# extension to basic DCR graph to include events

from pm4py.objects.dcr.obj import DCR_Graph
class RoleDCR_Graph(DCR_Graph):
    def __init__(self, template):
        super().__init__(template)
        self.__principals = template['principals']
        self.__roles = template['roles']
        self.__roleAssignment = template['roleAssignment']

    @property
    def principals(self):
        return self.__principals

    @property
    def roles(self):
        return self.__roles

    @property
    def roleAssignment(self):
        return self.__roleAssignment