# Subprocess mining

0: ER Registration
1: Leucocytes
2: CRP
3: LacticAcid
4: ER Triage
5: ER Sepsis Triage
6: IV Liquid
7: IV Antibiotics
8: Admission NC
9: Release A
10: Return ER
11: Admission IC
12: Release B
13: Release C
14: Release D
15: Release E
--------------------------------------------------------------
0: {1, 2, 3, 4, 5, 6, 7}
1: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
2: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
3: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
4: {0, 1, 2, 3, 4, 5, 6, 7, 8}
5: {0, 1, 2, 3, 4, 6, 8, 11}
6: {0, 1, 2, 3, 4, 5, 7, 8, 11}
7: {0, 1, 2, 3, 4, 5, 6, 8, 11}
8: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12}
9: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
10: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 14, 15}
11: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
12: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
13: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
14: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
15: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}

## Sub-process candidates with themselves as predecessors
{'Release D', 'Release A', 'Admission IC', 'Release C', 'Release B', 'Release E'}
{'Admission NC'}
{'LacticAcid', 'CRP', 'Leucocytes'}
{'ER Registration'}
{'ER Sepsis Triage'}
{'ER Triage'}
{'IV Antibiotics'}
{'IV Liquid'}
{'Return ER'}
---------------------------------------------------------------
0: {1, 2, 3, 4, 5, 6, 7}
1: {0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}
2: {0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11}
3: {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11}
4: {0, 1, 2, 3, 5, 6, 7, 8}
5: {0, 1, 2, 3, 4, 6, 8, 11}
6: {0, 1, 2, 3, 4, 5, 7, 8, 11}
7: {0, 1, 2, 3, 4, 5, 6, 8, 11}
8: {0, 1, 2, 3, 4, 5, 6, 7, 11, 12}
9: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
10: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 14, 15}
11: {0, 1, 2, 3, 4, 5, 6, 7, 8}
12: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
13: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
14: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}
15: {0, 1, 2, 3, 4, 5, 6, 7, 8, 11}

## Sub-process candidates without themselves as predecessors
{'Admission IC'}
{'Admission NC'}
{'CRP'}
{'ER Registration'}
{'ER Sepsis Triage'}
{'ER Triage'}
{'IV Antibiotics'}
{'IV Liquid'}
{'LacticAcid'}
{'Leucocytes'}
{'Release D', 'Release A', 'Release C', 'Release B', 'Release E'}
{'Return ER'}

### Arguments:

Blocks of mutual exclusion
Blocks with common connections

To find these we use the predecessors because we can have optimizations

We use the predecessors where we remove the event from the set if it is a predecessor to itself.
We argue why this is the preferred way. Why is this better? Why is keeping the event as its own predecessor
not a good way to do it?

## After candidate choice
- mine again
  - inside the subprocess: same order
    - a dcr graph - with its own acceptance criteria
  - outside the subprocess
    - only replace the subprocess events with the new subprocess when
    the subprocess fires (is in an accepting state)
      - you do this by replaying the log
    - mine the subprocess replaced log
- accepting inside the subprocess and in relation to the log: then you add
the subprocess in the replaced log

- the initially pending mining

- Mine on other logs:
  - Sepsis: talk on without vs subprocess
  - BPIC 2017
  - Road Traffic
- Related work
  - Simplifying models
  - Probabilistic Declare
  - PIM

# Most likely ordering of events:

## Untimed
Based on mean/median/modes/box-and-whiskers-plot position in the log

## Timed 
Based on the timing distribution mined from the log.
Following the condition and response definitions and then either:
Sampling from the fitted distributions or just taking the mean.
