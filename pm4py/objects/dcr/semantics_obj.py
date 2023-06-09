from copy import deepcopy
from datetime import timedelta

rels = ['conditionsFor', 'responseTo', 'includesTo', 'excludesTo']


class DcrSemantics(object):

    def __init__(self, dcr) -> None:
        self.dcr = dcr
        self.dict_exe = self.__create_max_executed_time_dict()
        self.parents_dict = {}
        all_events = set(dcr['events'])
        if 'subprocesses' in dcr.keys():
            self.sp_events = set(dcr['subprocesses'].keys())
            self.atomic_events = all_events.difference(self.sp_events)
            in_sp_events = set()
            for k, v in dcr['subprocesses'].items():
                in_sp_events = in_sp_events.union(v)
                for event in v:
                    self.parents_dict[event] = k
            self.tl_events = all_events.difference(in_sp_events)
            self.just_events = self.tl_events.difference(self.sp_events)
        else:
            self.sp_events = set()
            self.atomic_events = all_events
            self.tl_events = all_events
            self.just_events = all_events

    def is_accepting(self):
        pend_incl = self.dcr['marking']['pending'].intersection(self.dcr['marking']['included'])
        tle_pend_incl = pend_incl.intersection(self.tl_events)
        return len(tle_pend_incl) == 0

    def execute(self, e, cmd_print=False):
        if isinstance(e, timedelta):
            return self.time_step(e)
        elif e in self.dcr['events']:
            if self.is_enabled(e):
                self.__weak_execute(e)
                ancs = self.__get_ancestors(e)
                for anc in ancs:
                    if self.is_enabled(anc):
                        self.__weak_execute(anc)
                    else:
                        return False
                return True
            else:
                print(f'[!] Event {e} not enabled!') if cmd_print else None
                return False
        else:
            print(f'[!] Event {e} does not exist!') if cmd_print else None
            return False

    def enabled_atomic_events(self):
        return self.enabled().intersection(self.atomic_events)

    def enabled_tl_events(self):
        return self.enabled().intersection(self.tl_events)

    def enabled_sp_events(self):
        return self.enabled().intersection(self.sp_events)

    def is_enabled(self, e):
        return e in self.enabled()

    def enabled(self):
        res = deepcopy(self.dcr['marking']['included'])
        for e in self.dcr['conditionsFor']:
            if e in res:
                for e_prime in self.dcr['conditionsFor'][e]:
                    if e_prime in self.dcr['marking']['included'] and e_prime not in self.dcr['marking']['executed']:
                        res.discard(e)
                        if e in self.parents_dict.keys():
                            res.discard(self.parents_dict[e])

        for e in self.dcr['conditionsForDelays']:
            if e in res:
                for (e_prime, k) in self.dcr['conditionsForDelays'][e].items():
                    if e_prime in self.dcr['marking']['included'] and e_prime not in self.dcr['marking']['executed']:
                        res.discard(e)
                    elif e_prime in self.dcr['marking']['included'] and e_prime in self.dcr['marking']['executed']:
                        if self.dcr['marking']['executedTime'][e_prime] < k:
                            res.discard(e)
                            if e in self.parents_dict.keys():
                                res.discard(self.parents_dict[e])

        for e in self.dcr['milestonesFor']:
            if e in res:
                for e_prime in self.dcr['milestonesFor'][e]:
                    if e_prime in self.dcr['marking']['included'] and e_prime in self.dcr['marking']['pending']:
                        res.discard(e)
                        if e in self.parents_dict.keys():
                            res.discard(self.parents_dict[e])

        enabled_sps = self.sp_events.intersection(res)
        for s in self.sp_events.difference(enabled_sps):
            res = res.difference(self.dcr['subprocesses'][s])
        return res

    def find_next_deadline(self):
        nextDeadline = None
        for e in self.dcr['marking']['pendingDeadline']:
            if (nextDeadline is None) and (e not in self.dcr['marking']['included']):
                continue
            if (nextDeadline is None and e in self.dcr['marking']['included']) or (
                    self.dcr['marking']['pendingDeadline'][e] < nextDeadline and e in self.dcr['marking']['included']):
                nextDeadline = self.dcr['marking']['pendingDeadline'][e]
        return nextDeadline

    def find_next_delay(self):
        nextDelay = None
        for e in self.dcr['conditionsForDelays']:
            for (e_prime, k) in self.dcr['conditionsForDelays'][e].items():
                if e_prime in self.dcr['marking']['executed'] and e_prime in self.dcr['marking']['included']:
                    delay = k - self.dcr['marking']['executedTime'][e_prime]
                    if delay > timedelta(0) and (nextDelay is None or delay < nextDelay):
                        nextDelay = delay
        return nextDelay

    def time_step(self, time):
        deadline = self.find_next_deadline()
        if deadline is None or deadline - time >= timedelta(0):
            for e in self.dcr['marking']['pendingDeadline']:
                self.dcr['marking']['pendingDeadline'][e] = max(self.dcr['marking']['pendingDeadline'][e] - time, timedelta(0))
            for e in self.dcr['marking']['executed']:
                self.dcr['marking']['executedTime'][e] = min(self.dcr['marking']['executedTime'][e] + time,
                                                             self.dict_exe[e])
            return (True, time)
        else:
            print(f'[!] The time step is not allowed, you are gonna miss a deadline in {deadline}')
            return (False, time)

    def find_all_ancestors(self):
        ancestors_dict = {}
        # for each event find the ancestors
        for e in self.dcr['events']:
            ancestors_dict[e] = self.__get_ancestors(e)
        return ancestors_dict

    def __get_ancestors(self, e, ancestors=None):
        # first loop set it to an empty set
        if ancestors is None:
            ancestors = set()
        # for each subprocess
        if 'subprocesses' in self.dcr.keys():
            for k, v in self.dcr['subprocesses'].items():
                if e in v:
                    # if the event is in the subprocess add that key as its ancestor
                    ancestors.add(k)
                    # if the key is a top level event we are done
                    if k in self.tl_events:
                        break
                    else:
                        # if the event is not a top level event then we go into the key of that subprocess and repeat
                        ancestors = ancestors.union(self.__get_ancestors(k, ancestors))
        return ancestors

    def __is_effectively_included(self, e, ancestors_dict):
        return ancestors_dict[e].issubset(self.dcr['marking']['included'])

    def __get_effectively_pending(self, e, ancestors_dict):
        return ancestors_dict[e].issubset(self.dcr['marking']['pending'])

    def __execute(self, e, cmd_print=False):
        if isinstance(e, timedelta):
            return self.time_step(e)
        elif e in self.dcr['events']:
            if self.is_enabled(e):
                self.__weak_execute(e)
                return (True, timedelta(0))
            else:
                print(f'[!] Event {e} not enabled!') if cmd_print else None
                return (False, timedelta(0))
        else:
            print(f'[!] Event {e} does not exist!') if cmd_print else None
            return (False, timedelta(0))

    def __create_max_executed_time_dict(self):
        d = {}
        for e in self.dcr['events']:
            d[e] = self.__max_executed_time(e)
        return d

    def __max_executed_time(self, event):
        maxDelay = timedelta(0)
        for e in self.dcr['conditionsForDelays']:
            for (e_prime, k) in self.dcr['conditionsForDelays'][e].items():
                if e_prime == event:
                    if k > maxDelay:
                        maxDelay = k
        return maxDelay

    def __is_accepting(self):
        pend_incl = self.dcr['marking']['pending'].intersection(self.dcr['marking']['included'])
        return len(pend_incl) == 0

    def __weak_execute(self, e):
        '''
        Executes events even if not enabled. This will break the condition and/or milestone
        :param e:
        :param dcr:
        :return:
        '''
        self.dcr['marking']['pending'].discard(e)
        self.dcr['marking']['executed'].add(e)
        self.dcr['marking']['executedTime'][e] = timedelta(0)

        if e in self.dcr['marking']['pendingDeadline']:
            self.dcr['marking']['pendingDeadline'].pop(e)
        if e in self.dcr['excludesTo']:
            for e_prime in self.dcr['excludesTo'][e]:
                self.dcr['marking']['included'].discard(e_prime)
        if e in self.dcr['includesTo']:
            for e_prime in self.dcr['includesTo'][e]:
                self.dcr['marking']['included'].add(e_prime)
        if e in self.dcr['responseTo']:
            for e_prime in self.dcr['responseTo'][e]:
                self.dcr['marking']['pending'].add(e_prime)
        if e in self.dcr['responseToDeadlines']:
            for (e_prime, k) in self.dcr['responseToDeadlines'][e].items():
                self.dcr['marking']['pendingDeadline'][e_prime] = k
                self.dcr['marking']['pending'].add(e_prime)
