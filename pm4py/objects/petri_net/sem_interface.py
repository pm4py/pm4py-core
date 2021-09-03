class Semantics(object):
    def is_enabled(self, t, pn, m, **kwargs):
        pass

    def execute(self, t, pn, m, **kwargs):
        pass

    def weak_execute(self, t, pn, m, **kwargs):
        pass

    def enabled_transitions(self, pn, m, **kwargs):
        pass
