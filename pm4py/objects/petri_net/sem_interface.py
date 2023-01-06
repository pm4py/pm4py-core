import deprecation

class Semantics(object):
    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.is_enabled() instead")
    def is_enabled(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
    def execute(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed, use PetriNetSemantics.fire() instead")
    def weak_execute(self, t, pn, m, **kwargs):
        pass

    @deprecation.deprecated("2.3.0", "3.0.0", details="this method will be removed")
    def enabled_transitions(self, pn, m, **kwargs):
        pass
