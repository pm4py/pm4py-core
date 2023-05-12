Release Notes
=============


pm4py 2.7.0 - Release Notes
---------------------------

The major changes in pm4py 2.7.0 are as follows:

1. We added an initial integration to ChatGPT

2. We added some connectors for workstation-supported processes (Outlook mail and calendar; web browsers).


pm4py 2.6.0 - Release Notes
---------------------------

The major changes in pm4py 2.6.0 are as follows:

1. We added the ILP Miner as process discovery algorithm

2. We added two log filters: "timestamp grouping" and "consecutive activities"

3. We added the insertion of the case arrival/finish rate and of the waiting/service/sojourn times
in the simplified interface

4. We added a baseline clustering algorithm, based on the pre-existing feature extraction

5. We added the extraction of the "target vector" from event logs for machine learning purposes


pm4py 2.5.0 - Release Notes
---------------------------

The major changes in pm4py 2.5.0 are as follows:

1. We added the Cardoso and extended Cardoso simplicity metrics to pm4py

2. We added discovery of Stochastic Arc Weight nets based on OCEL logs.

3. We added Murata-based Petri net simplification to the simplified interface (implicit place removal)   


pm4py 2.4.0 - Release Notes
---------------------------

Today, we released pm4py 2.4.0.
We have adopted our release policy slightly, i.e., as of now, the pm4py versioning follows the MAJOR.MINOR.FIX pattern.
We will also report all MAJOR and MINOR releases in the release notes.

As today's release is a minor release, we report on the main changes here.

1. We added the Murata algorithm (Berthelot implementation) to remove the structurally redundant places, which is now available in the simplified interface.

2. We added the reduction of invisible transitions in Petri nets to the simplified interface.

3. We added support for calcuating stochastic languages of process models

4. We adde support for calculating EMD between two stochastic languages 

5. we added a visualization of alignments in simplified interface

6. We added visualization of footprint table in simplified interface

7. We added a conversion of Petri net objects to networkX DiGraphs

8. We added support for stochastic Petri nets

9. We added support for stochastic arc-weight nets (the paper describing this class of nets is submitted to the Petri nets 2023 conference)

pm4py 2.3.0 - Release Notes
---------------------------
Finally, pm4py 2.3.0 has arrived!
The 2.3.0 release contains various significant updates and improvements concerning its predecessors. 
The release consists of approximately 550 commits and 47.000 LoC!
The main changes are as follows:

1. *Flexible parameter passing in the simplified method invocation*, e.g., :meth:`pm4py.discovery.discover_petri_net_inductive`; 
For example, in ```pm4py``` 2.2.X, the columns used in process discovery were fixed (i.e., case:concept:name, concept:name, time:timestamp). Hence, changing the perspective implied changing column headers.
In pm4py 2.3.X, the columns used in process discovery are now part of the function arguments.
A simple comparison:
  * Discovering a Petri net in pm4py 2.2.X:
  ``pm4py.discover_petri_net_inductive(dataframe, noise_threshold=0.2)``

  * Discovering a Petri net in pm4py 2.3.X:
  ``pm4py.discover_petri_net_inductive(dataframe, noise_threshold=0.2, activity_key="activity", timestamp_key="timestamp", case_id_key="case")``

2. *Dataframes are primary citizens*; 
pm4py used to support both Pandas ``Dataframes`` and our custom-defined event log object. We have decided to adapt all algorithms to work on Dataframes. As such, event data is expected to be represented as a Dataframe in pm4py (i.e., we are dropping the explicit use of our custom event log object). There are two main reasons for this design decision:
  1. *Performance*; Generally, Pandas Dataframes are performing significantly better on most operations compared to our custom event log object
  2. *Practice*; Most real event data is of tabular form.

Of course, pm4py still supports importing .xes files. However, when importing an event log using :meth:`pm4py.read.read_xes`, the object is directly converted into a Dataframe.
A general drawback of this design decision is that pm4py no longer appropriately supports nested objects (generally supported by the .xes standard). However, as indicated in point b), such nested objects are rarely used in practice.
 
3. *Typing Information in the simplified interface*; 
All methods in the simplified interface are guaranteed to have typing information on their input and output objects.

4. *Variant Representation*; 
In pm4py 2.3.X, trace variants are represented as a tuple of Strings (representing activity names) instead of a String where a ‘,’ symbol indicates activity separation. For example, a variant of the form <A,B,C> is now represented as a tuple (‘A’,’B’,’C’) and was previously represented as ‘A,B,C’. This fix allows activity names to contain a ‘,’ symbol.

5. *Inductive Miner Revised*;
We have re-implemented and restructured the code of the inductive miner. The new version is closer to the reference implementation in ProM and is more performant than the previous version.

6. *Business Hours Revised*; 
The business hours functionality in pm4py has been revised completely. In pm4py 2.2.X, one could only specify the working days and hours, which were fixed. In pm4py 2.3.X, one can define week-day-based activity slots (e.g., to model breaks). One slot, i.e., one tuple consists of one start and one end time given in seconds since week start, e.g. [(7 * 60 * 60, 17 * 60 * 60), ((24 + 7) * 60 * 60, (24 + 12) * 60 * 60), ((24 + 13) * 60 * 60, (24 + 17) * 60 * 60),] meaning that business hours are Mondays 07:00 - 17:00 and Tuesdays 07:00 - 12:00 and 13:00 - 17:00

7. *Auto-Generated Docs*; 
As you may have noticed, this website serves as the new documentation hub for pm4py. It contains all previously available information on the project website related to ‘installation’ and ‘getting started’. For the simplified interface, we have merged the general documentation with the API docs to improve the overall understanding of working with pm4py. The docs are now generated directly from the pm4py source. Hence, feel free to share a pull request if you find any issues.


Happy #processmining!

The #pm4py development team.
