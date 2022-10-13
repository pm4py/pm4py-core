'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
caseIDKey = "Case ID"
activityKey = "Activity"
durationKey = "Complete Timestamp"


def getFollowersOfEventInTrace(event, trace):
    followers = list()
    if event not in trace:
        return followers
    eventIndex = trace.index(event)
    restTrace = trace[eventIndex + 1:]
    for e in restTrace:
        if e not in followers:
            followers.append(e)
    return followers


def getFollowsRelations(allEvents, traces):
    followsMatrix = {}
    alwaysCtr = 0
    sometimesCtr = len(allEvents) * len(allEvents)  # In the beginning, all relations are 'Sometimes'.
    neverCtr = 0

    for event in allEvents:
        alwaysFollows = allEvents.copy()
        neverFollows = allEvents.copy()

        for eClmn in allEvents:
            followsMatrix[(event, eClmn)] = 'S'

        for trace in traces:
            if event in trace:
                followers = getFollowersOfEventInTrace(event=event, trace=trace)
                for f in followers:
                    if f in neverFollows:
                        neverFollows.remove(f)

                for e in allEvents:
                    if e not in followers:
                        if e in alwaysFollows:
                            alwaysFollows.remove(e)

        for a in alwaysFollows:
            followsMatrix[(event, a)] = 'A'
            sometimesCtr -= 1
            alwaysCtr += 1

        for n in neverFollows:
            followsMatrix[(event, n)] = 'N'
            sometimesCtr -= 1
            neverCtr += 1

    return followsMatrix


def getPrecedesRelations(allEvents, traces):
    precedesMatrix = {}
    alwaysCtr = 0
    sometimesCtr = len(allEvents) * len(allEvents)  # In the beginning, all relations are 'Sometimes'.
    neverCtr = 0

    for event in allEvents:
        alwaysPrecedes = allEvents.copy()
        neverPrecedes = allEvents.copy()

        for eClmn in allEvents:  # eClmn -> event in respective column
            precedesMatrix[(event, eClmn)] = 'S'

        for trace in traces:
            if event in trace:
                predecessors = getPredecessorsOfEventInTrace(event=event, trace=trace)
                for p in predecessors:
                    if p in neverPrecedes:
                        neverPrecedes.remove(p)

                for e in allEvents:
                    if e not in predecessors:
                        if e in alwaysPrecedes:
                            alwaysPrecedes.remove(e)

        for a in alwaysPrecedes:
            precedesMatrix[(event, a)] = 'A'
            sometimesCtr -= 1
            alwaysCtr += 1

        for n in neverPrecedes:
            precedesMatrix[(event, n)] = 'N'
            sometimesCtr -= 1
            neverCtr += 1

    return precedesMatrix


def getPredecessorsOfEventInTrace(event, trace):
    predecessors = list()
    if event not in trace:
        return predecessors

    eventIndex = max(loc for loc, val in enumerate(trace) if val == event)
    restTrace = trace[:eventIndex]

    for e in restTrace:
        if e not in predecessors:
            predecessors.append(e)

    return predecessors


def getBARelations(traces, events):
    followsRelations = getFollowsRelations(allEvents=events, traces=traces)
    precedesRelations = getPrecedesRelations(allEvents=events, traces=traces)

    return followsRelations, precedesRelations


# checks whether a prefix conforms to the log overall Behavioral Appropriateness given by precedes and follows Relations
# return [true/false]
def getBAViolations(allEvents, followsRelations, precedesRelations, prefix, TRACE_END):
    violationsCtr = 0
    logEvents = allEvents.copy()
    logEvents.remove(TRACE_END)  # all events except for TRACE_END. used to look up 'always follows' relations
    localPrefix = list()  # prefix where TRACE_END is removed. used to obtain followers and predecessors of events contained
    prefixEvents = list()  # all events in the prefix (except for TRACE_END)
    for e in prefix:
        if e != TRACE_END:
            localPrefix.append(e)
            if e not in prefixEvents:
                prefixEvents.append(e)

    followersDict = dict()
    for event in prefixEvents:  # get followers for each event in the prefix and store them
        followersOfEvent = getFollowersOfEventInTrace(event=event, trace=localPrefix)
        followersDict[event] = followersOfEvent

    predecessorsDict = dict()
    for event in prefixEvents:  # get predecessors for each event in the prefix and store them
        predecessorsOfEvent = getPredecessorsOfEventInTrace(event=event, trace=localPrefix)
        predecessorsDict[event] = predecessorsOfEvent

    for e1 in prefixEvents:
        for follower in followersDict[e1]:  # check if 'never follows' relations are violated
            if followsRelations[(e1, follower)] == 'N':
                violationsCtr += 1

        for predecessor in predecessorsDict[e1]:  # check if 'never precedes' relations are violated
            if precedesRelations[(e1, predecessor)] == 'N':
                violationsCtr += 1

        for e2 in logEvents:  # to check if 'always follows' is violated, all events must be checked
            if TRACE_END in prefix:  # no TRACE_END in prefix -> event saving the always follows relation could follow sometime later
                if followsRelations[
                    (e1, e2)] == 'A':  # followsRelations[(e1, e2)] == 'A' -> if e1 in trace, e2 always follows
                    if e2 not in followersDict[e1]:
                        violationsCtr += 1

            if precedesRelations[
                (e1, e2)] == 'A':  # precedesRelations[(e1, e2)] == 'A' -> if e1 in trace, e2 always precedes
                if e2 not in predecessorsDict[
                    e1]:  # if e1 in trace and e2 does not precede right now it won't ever do -> no need to wait for TRACE_END
                    violationsCtr += 1

    return violationsCtr  # if no {always/sometimes} {follows/precedes} relation is violated, return 0
