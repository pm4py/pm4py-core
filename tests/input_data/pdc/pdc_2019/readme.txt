This folder contains the data set as was used for the Process
Discovery Contest of 2019 (PDC 2019). The data set contains 10
training logs, 10 corresponding test logs, and 10 corresponding
ground truth logs. The logs are all stored using the
IEEE XES file format (see either https://www.xes-standard.org/ or
https://ieeexplore.ieee.org/document/7740858), while the models are
workflow nets (a subclass of Petri nets) stored in the PNML file
format (see
https://www.iso.org/obp/ui/#iso:std:iso-iec:15909:-2:ed-1:v1:en).

In each ground truth log, the additional boolean “pdc:isPos” attribute
denotes whether the trace is positive (fits the model, true) or
negative (does not fit the model, false). 
