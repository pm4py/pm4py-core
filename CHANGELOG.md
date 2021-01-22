# PM4Py Changelog

## PM4PY 2.1.4.1 (2021.01.22)

### Fixed
* 1231f518
  * strip text read from nodes in bpmn importing
* 0bc1b330
  * add type checking for bpmn conversion; i.e., if the input
  is already bpmn, it is returned.
* ea0c7e54
  * fix consistency in obtaining the case arrival statistics in 
    ```pmpy.statistics.traces.log.case_arrival```; was median, changed to mean.
    also see: https://github.com/pm4py/pm4py-core/issues/200
### Removed

### Deprecated

### Changed
* 51be0910
  * set ```stream_postprocessing``` default value back to ```False``` for
  ``dataframe`` to ```stream``` conversion. Columns containing ```None``` values
    are no longer filtered by default (compliant with ```pm4py<=2.1.2```).
    also see: https://github.com/pm4py/pm4py-core/issues/199 
* 8976ad45
  * drop the explicit dependency on ```numpy 1.19.3```
  * add explicit dependency ```pulp<=2.1```
* 1231f518
  * support ```sequenceflow``` operator node in bpmn file import
* 62618eeb
  * explicitly blacklist version 1.9.4 of ```numpy``` in the requirements.txt file.

### Added

### Other

---

## PM4PY 2.1.4 (2021.01.18)

### Fixed
* 35f2278a; 89c5f13b; 6a3579bc; 65fc182b; fa4448a6; c4e44311
    c456c681; 6c6d96cc; e3770281; f091c43e; 6a20cf17; 69eb1ae7; ca780326; 36cb3963
    e4f3b16f; c9f80d1f; 94c5a6e0; a713ef3d:
  * add fall-back to time-range filter if incorrect argument is passed
  * fix the copying of the 'meta attributes' of the filtered event log for the start activities filter
  * fix the copying of the 'meta attributes' of the filtered event log for the end activities filter
  * fix the copying of the 'meta attributes' of the filtered event log for the attributes filter
  * fix the copying of the 'meta attributes' of the filtered event log for the variants filter
  * fix the copying of the 'meta attributes' of the filtered event log for the directly follows filter
  * fix the copying of the 'meta attributes' for event logs in the ltl checker
  * fix the copying of the 'meta attributes' for event logs in the timestamp filter
* ffe29353:
  * create event log object before starting the parsing of XML file (in ITERPARSE_MEM_COMPRESSED)

### Removed

### Deprecated

### Changed
* 8f2d899a
  * allow to specify a cap on the number of times we visit the same marking in the extensive playout
  * allow to return the firing sequences of extensive playout instead of an event log
* b707377b
  * allow to return the firing sequences of basic/stochastic playout instead of an event log
* 9782f522
  * extended exception management in streaming algorithm interface: release locks if exception happen   
* 0a741566
  * support importing of bpmn files that do not describe a name for gateways
* 583825d8
  * refactored variant-based filtering: added top-K and coverage percentage
* ba073f54
  * extended DFG filtering
* 8ebda3b1
  * exploit variants in the extensive footprints conformance checking
* dc754c78
  * change range(s) of timestamp filters to be inclusive (<=) rather than exclusive (<)

### Added

### Other

---

## PM4PY 2.1.3.2 (2021.01.08)

### Fixed
* b5cb7f0d; f1c0f037; 960d40e9 
  * fix naming consistency in the filtering interface of pm4py.

### Removed

### Deprecated

### Changed

### Added

### Other

---

## PM4PY 2.1.3.1 (2021.01.07)

### Fixed
* f9f894ed
  * create an iterable that permits, theoretically, to iterate over the infinity of traces admitted by a DFG
  * the main ```apply()``` calls the iterable and stops with the usual criterias
  * the ```apply()``` can also return the variants of the log

### Removed

### Deprecated

### Changed
* 1c3666b7
  * minor refactoring of the filtering simplified pm4py interface

### Added
* 8b5dee65
  * add lambda-based filtering and sorting to simplified pm4py interface

### Other

---

## PM4PY 2.1.3 (2021.01.04)

### Fixed
* 388348f2
  * bugfix ```remove_flow``` BPMN function
* 3bd4fe0a
  * bug fix - DFG visualization needs deepcopy, otherwise it can remove element from the underlying DFG
* 92fde8cf
  *  bug fix in Petri net playout in stop criterion
* 882468e1
  * compatibility with pulp version 1.6.x
   
### Removed

### Deprecated

### Changed
* 41ed5720
  * deepcopy of inputs:  since the dictionaries/sets are modified, a "deepcopy" is the best option to ensure data
    integrity.
  * ```keep_all_activities``` parameter in paths filter: decides if all the activities (also the ones connected by the low
    occurrences edges) should be kept, or only the ones appearing in the edges with more occurrences (default).
* 63ccc055
  * IM and IMf: removed dependency on ```pm4py.algo.filtering``` package
* 8a5788fa
  * more advanced to bpmn conversion in the simplified interface
* 66e0c074
  * refactoring conversion parameters log->stream and improved stream compression
* 73054b04
  * improved performance of the line-by-line xes importer
  * increased XES-standard conformity
* e6136ce5
  * improved performance of the xes exporters
  * increased XES-standard conformity
  * progress bar for exporting enabled
* 3b692b33
  * added parameter to enable/disable progress bar in importing in ITERPARSE
  * compression from file - XES compression moved from general entrypoint to single variant   
* 68ff7d00
  * more efficient importing of .xes.gz files
* 4aad427e; 67a42d23
  * get predecessors and successors of a dfg node (in dfg utils)
* 0888ab26
  * added minimum trace length in process tree extensive playout

### Added
* 6a946fbd
  * allow to compute alignments directly on the dfg using dijkstra
* 50722bb8
  * DFG playout including Markovian probability of traces

### Other

---

## PM4PY 2.1.2 (2020.12.18)

### Fixed
* 2fb0b807
  * support nodes with the same label in BPMN layout algorithm 
  
### Removed

### Deprecated

### Changed
* 96a7681c
  * significant memory footprint reduction for iterparse-based event log importing
* 8270a46e
  * significantly faster 'line-by-line' xes exporter
* aae4be33
  * advanced DFG filtering in (activities percentage, paths percentage) ensuring reachability from start and end
* d38f4c97
  * number of occurrences as a start or end activity is visualized in the DFG visualization

### Added
* 97cc315c
  * add (de)serialization functionality for PM4Py objects

### Other

---

## PM4PY 2.1.1 (2020.12.07)

### Fixed

### Removed

### Deprecated

### Changed
* 43e7ce9e
  * full conversion of WF-nets to BPMN models

### Added
* 029d30f5
  * add visualizing and exporting BPMN models
* f76dd379
  * added conversion to simplified interface   
### Other

---

## PM4PY 2.1.0.2 (2020.11.29)

### Fixed

### Removed

### Deprecated

### Changed

### Added

### Other
* f18c3e17
  * downgrading ```numpy``` to 1.19.3 for Windows 10 2004 compatibility problems
  * skip blocking ```scikit-learn``` installation for Python 3.9

---

## PM4PY 2.1.0.1 (2020.11.26)

### Fixed
* f6cdf1a9
  * hotfix problem in XES importer reading of parameters
   
### Removed

### Deprecated

### Changed

### Added

### Other

---

## PM4PY 2.1.0 (2020.11.24)

### Fixed
* a0a7fd09
  * bug fix in the inductive miner: sequence cuts were to maximal, leading to underfitting models (involving too many skips)
* 5b32725a
  * fix use of deepcopy in event log conversion
* 33103b5c
  * fix get-variants behavior for event log / df (yielded different results)
   
### Removed

### Deprecated
* 0138f93d
  * deprecated ```pm4py.write_csv()```; conversion and subsequent pandas export should be used.
   
### Changed
* 3b8fcd4a
  * apply invisible transition reduction on Petri nets obtained by Heursistic Miner

### Added
* 6afd8ab9
  * support for importing/exporting BPMN files;
  * supported elements: tasks, xor, and, or gateways
  * conversion of BPMN to WF-net
  * conversion of Process Tree to BPMN
* 848a1610
  * conversion of dataframes to event streams / event logs now detects the use of XES Extensions
* 8874f7b4
  * add statistics on concurrent activities
  * discover eventually follows relations with concurrent activities

### Other

---

## PM4PY 2.0.1 (2020.11.13)

### Fixed
* 4c115dbb
  * fix bug in hash function of traces
* 0dd8f28e
  * fix bug in the alpha+ algorithm (was adding artificial start/end to the underlying event log)   
   
### Removed

### Deprecated
   
### Changed
* commit c51b1f02
  * parametrizing size of the thread pool in streaming package

### Added
* 8e07d847
  * add (unbounded) dfg discovery on an event stream
* 16e3f7f5
  * integration of the wf-net to process tree algorithm described in https://doi.org/10.3390/a13110279   
* 1a26f678
  * allow creation of 'live' streaming objects directly from xes and csv files
* b08564ed
  * start minor support for interval-based process models
* 36cb7130
  * added support for generic dictionaries in streaming conformance checking
 
  
### Other
* 81579e19e
  * relaxing the importing of some dependencies (pandas, pulp, graphviz, intervaltree)
    to make a basic set of functionalities of PM4Py work even without those dependencies
* ed45eafc
  *  fixing circular dependencies issues and added partial compatibility with Python 3.4

---

## PM4PY 2.0.0 (2020.10.14)

### Fixed
* 1a8f9281
  * bug fix in ```pandas``` case size filter

### Removed
* 7a89d4dd
  * remove deprecated factories

### Deprecated
   
### Changed
* 62801513
  * improved performance of token-based replay with duplicate labels
   
### Added
* f408a181
  * add streaming token-based replay and footprint-based comparison
* fde08b03
  * output conformance checking diagnostics in a dataframe
   
### Other
* a9c5aa34
  * compatibility with Python 3.9 (limited to windows)
   
---

## PM4PY 1.5.2.2 (2020.09.29)

### Fixed
* 2d4a8b67e25164838030dca709816918ddbf9279
  * fixed dependencies on factories. fixed some release notes. fixed some deprecations.

### Removed

### Deprecated
   
### Changed

### Added 
* 0d75241676a736919952e5c9ab96ab2be4c71046
  * added utility for trace attributes filtering   

### Other
* d8433ac1bbb57082b19b3b97bc726b353096c76e
  * better specification of 'stable' requirements

---

## PM4PY 1.5.2.1 (2020.09.25)

### Fixed
a6fde4ccfdf0465d8919d3c72d4400bce8d4ab0e
  * fixed some deprecation warnings for external libraries
   
### Removed

### Deprecated
   
### Changed

### Added 
* a5befe62f84af0f3dbe734c713cc8c2c1fc22a04
  * added WOFLAN to the simplified interface
   
### Other

---

## PM4PY 1.5.2 (2020.09.24)

### Fixed
* 7bf3aea0b4638f6eceaa192ec37e17370e47f560
  * fixing a parameter issue on stochastic playout
   
### Removed

### Deprecated
   
### Changed

### Added 
* 13cd96da7fe22427839f1b21dd38a5ac8ff8c231
  * provide alternative visualizations through Matplotlib of the main visualizations
* e7e3dfa11264a7e737ca7b65165eb7f719817f59
  * add utility to remove an arc 
   
### Other
* c42bad174247eb13134e0cb4acb0703c301aa869
  * fixed  compatibility with Python 3.5

---

## PM4PY 1.5.1 (2020.09.15)

### Fixed

### Removed
* 9e926a5d1a373d124a041c72f909eb34083f4649
  * removed the old soundness check

### Deprecated
   
### Changed
* 526342e3e96c7386dc7451ac0d9ec74c76b86b4f
  * performance improvement of the 'less memory' alignment variant
* 83c71eaaa9bb4ee55e2f773dd3fc9704c6324704
  * generalization of the heuristics miner visualization
* 7e7d9ba9e9b4f94d9801f5c8df3c5e4b3afd5971
  * improved speed of event log sampling
* 11d06ba2a44fd7d0a83e439b6615befad5e3c4ba
  * faster process tree playout (recursive, ignoring PT statespace)   
* ce3a8609013bd7f5890b52cb44e155b57b2fc1c0
  * allow adding (arbitrary) data to transition system

### Added 
 
### Other

---

## PM4PY 1.5.0 (2020.08.31)

### Fixed
* 30b9059fac3d59abac1c973637bd66388d7dd6db
  * bug fix in parameter parsing of log conversions
### Removed

### Deprecated
   
### Changed
* 3c9ed4b5e1860e2494d3b68668e3e1021ee59585
  * apply invisible transition reduction in process tree to Petri net transformation
* 26ac905fed4703724805f8fb1b5daa21475df147
  * minor optimizations in process tree alignment approximation algorithm
* c5b5ffdd51cd832be14d3078948e29f88f6c2673
  * add time-out parameter to decomposed alignment calculation
* 4a5fb9ff5ab395529062ce92747b9624a1799b0e
  * add bipartite graph matching for correlation mining to obtain exact matching results   
* acc46269040a3b60bdcc6f5afe9ea55ddb5549e1
  * minor performance improvement of process tree playout
* 5dd0fe17d5a07a2096afc647306a5673d86508ba
  * apply trace-level directly on pandas data frames
* 4c35335da6a6d4419b68a49af3cbd358eca8881d
  * add 'COUNT' functionality for log/dfg statistics, e.g., in how many cases does act 'A' appear?

### Added 
* 3bb5125f1849985ec9e2ba7962a287a25ede8e43
  * new implementation of the (classical) Inductive Miner, based on the PhD thesis of Sander Leemans.
   The implementation covers the following fall through functions:
     * empty trace
     * strict tau loop
     * tau loop
     * activity once per trace
     * activity concurrent
     * flower loop
* 1639d7a17660b4641a58cb435f7061d4168ce422
  * implemention of 'WOFLAN', based on the PhD thesis of Eric (H.M.W.) Verbeek.
   
### Other

---

## PM4PY 1.4.1.1 (2020.08.13)

### Fixed
* 76df914ad48b93a72127b0d79e5547669d3148db
  * fixed bug in less-memory alignments when im == fm

### Removed

### Deprecated
   
### Changed

### Added 
 
### Other

---

## PM4PY 1.4.1 (2020.08.10)

### Fixed

### Removed

### Deprecated
   
### Changed
* fc724c4c9e00a388b94efea50be46412c1351bc5
  * refactoring correlation miner
  * increased scalability of the correlation miner
* e18021f06e4431628a84b441acf136d44c9baed6
  * revision/enrichment of simplified API

### Added 
* 9cfd4183968118f488c95ab0bbd7e3e9b66ba355
  * alignments approximation on process trees (https://arxiv.org/pdf/2009.14094)
* f9a898da47367f86bf616a7bc8dc796be1b3e440
  * discovery of log skeleton from the list of variants  
 
### Other

---

## PM4PY 1.4.0 (2020.08.03)

### Fixed
* c5fa9dee9bf7e4eed56785eadc423b59214d3df0
  * compatibility with latest IPython API
* 616623b358d1e1a9aa789f43e2c8cf7670ee4d79
  * clean-up in linear solver functionality 
  * bug fix in usage of PulP result vector

### Removed

### Deprecated
   
### Changed
* 4616952ee5c184d35d26e986b298e1e586b38b3f
  * minor refactoring of the alignment code
* 3477e5345068018fa6aa91e04b6da4184e4d3c94
  * update of verions of package dependencies

### Added 
* cba7a2e574aa15709d0a2dda35f8a27da9200f42
  * [beta release] simplified 'pythonic' method invocation (see ```examples/simplified_interface.py```)   
* ade44e6d78551c454b477f36cbe3248a5d4e6c8b
  * added the 'correlation miner' to PM4Py (https://is.tm.tue.nl/staff/rdijkman/papers/Pourmirza2017.pdf)
* 9564b54a7111916c7bc3d6f1e4c56f3829978efe
  * add visualization of conformance checking results on process tree
* 988258a2c655d17201c5b1a7120d19ab5954dbe3
  * added 'extensive' playout for process trees (for footprint comparison)
   
### Other

---

## PM4PY 1.3.5.2 (2020.07.24)

### Fixed
* a31467a560b940a2cb426751e032b4ea79bbb29f
  * add cast to Event class in event conversion
* 0febe4eda5772685498da2d79d144effdf61ce20
  * fix in alpha miner; conflict check yielded self-loops in some cases
   

### Removed

### Deprecated
   
### Changed

### Added 
   
### Other

---

## PM4PY 1.3.5.1 (2020.07.22)

### Fixed
* 844459e366e77ebf88a8d01728064048d71a3e6f
  * remove ```pyemd``` from requirements as it requires a full C studio installation; can be installed and used *optionally*

### Removed

### Deprecated
   
### Changed

### Added 
   
### Other

---

## PM4PY 1.3.5 (2020.07.20)

### Fixed
* 6cdf4483548027420b0a54c681a3ecfd515ab8f3
  * bug fix for de/recomposition approach to handle duplicated labels
* 58149e7f085bbedb47e31d58d10e37d686e46a72
  * small fix in importing of parquet files
* b08675fe8c03207c4701d2eb8b91c234e3ddbe1b
  * fix in IMdf; the noise threshold was overridden before
* 772ea5d5af9ab2fa3a424b91670d81487ab2667b
  * minor fix for timestamps that end with symbol 'Z' (Zero timestamp)
* 1e13cbdb011dff175850c4c665283bf60e0db84c
  * fix Scipy dependency for tree generator

### Removed

### Deprecated
   
### Changed
* 921328cd06d8870ecaa601d53cfde30a6015aec7
  * parameterize simplicity metric to use a given 'K' for reference
* 8403093c3e18c1493f4fd72bc83914dadb03e4c2
  * change the color scheme for net comparison

### Added
* 143f60a0b4fb265ba5e9d997efddf8f8d66458c3
  * add support for process tree importing (.ptml files)
* 4b9132f2835f574d9e7e5af113e5fc96bd821ccf
  * add new A* version that encodes the states of the state-space differently (up to 10% memory reduction)   
* 93e6e84c4ea78afc562f4ba6cee42de8718eb4cb
  * add 'stochastic' playout, i.e., use token-based replay on a given log to guide the playout of a given Petri net
* 107797c5d1be1d742e6522a14231f4f9fce1cb38
  * add EMD-based process model evaluation ('Earth Mover's Distance' between log/model)
* 1e02596bc90b6fc22a8c89e80567bdddc2c8f1b7
  * add process tree based footprint computation   
   
### Other

---

## PM4PY 1.3.4 (2020.07.06)

### Fixed

### Removed

### Deprecated
   
### Changed
* f05ba60e2faa28b2f2e2d7ef65e0ac415ae298e8
  * improved memory performance of Dijkstra-based alignments, restriction of model-move scheduling is applied (only one of many is chosen)
* eaed442d10a5b4c9eead3966cef473e2c3f0d61b
  * improved efficiency of reachability graph computation

### Added
* a42d0f087c94cb9e7914532f7ae0228af3a7f9ce
  * add 'extensive' playout, which allows to generate all traces in the language of a model up-to a given length.
* eaed442d10a5b4c9eead3966cef473e2c3f0d61b
  * added footprint-based conformance checking
   
### Other
* b99da02411259897f1df52f9a9a62153228dab8a
  * ```PuLP<=2.1``` is forced (for now, due to excessive console output of v2.2.)
  * new version of ```Pyvis``` requires additional dependencies (Apache, BSD, MIT licenses), which are now specified

---

## PM4PY 1.3.3 (2020.06.22)

### Fixed
* 1278713e2209d7b1e2287afbd9d80097db028617
  * minor fixes in (to-be-deprecated) Parquet importer and exporter

### Removed

### Deprecated
   
### Changed
* 59630ed8456d9e7842e05fee4c53ff1a3d1389a0
  * improved memory performance of Dijkstra-based alignments

### Added

### Other

---

## PM4PY 1.3.2 (2020.06.08)

### Fixed

### Removed

### Deprecated
   
### Changed

### Added
* 98e6d6d6219cceeeb2421392e9981ec808d2a468 (Merge Request #89)
  * Support importing and exporting of '.dfg' files (similar to ProM 6.10)
* 7ca768b7fcd1eea468bcdb1c1e8c9397676b511a (Merge Request #90)
  * add a detailed list of all third-party dependencies (README.THIRD_PARTY.md)
* e0685638c6c0c171583108e23f752ebef70d033e (Merge Request 94)
  * new version of Dijkstra based alignment computation

### Other

---

## PM4PY 1.3.1 (2020.05.25)

### Fixed
* d51430106dea70473777c6868a3676c027faf607
  * fix paths filter for Pandas dataframe when dataframe is not sorted
   
### Removed
* c7a76e0aaffb5dbcad769b2fbc52fd8c03703769
  * cleanup of the petri net impoprter/exporter, i.e., stochastic/layout information is now stored in the 'properties' object of places/transitions/nets

### Deprecated
   
### Changed
* 00d7c405628033e8f383a845e61a84205f7bbc83
  * color scheme of the log-log comparison (pm4py.algo.enhancement.comparison.petrinet)
* e84c7dc88907b408b4caf97524dd69a378e1859e
  * update the README.md file
* 332de04112cf780cbc711553e34ca4b835ee8425
  * add parameters object to transient analysis call to dfg learner   
* f0976015c2b5b7384135855e75b36f69fb44a4db
  * add final marking to the basic playout of Petri nets
* e0d43c6dd5ee2492eabfd14c507b430088ec9cf0
  * allow prefixes in petri net attribute names (petri net importing)

### Added
* 095f35a3bf9f9c3bea0d518c72c76380f38b77b2
  * add support for (correctly) importing lists from .xes files 

### Other

---

## PM4PY 1.3.0 (2020.05.11)

### Fixed
* 112dc3fc56f0d5e3f3ae0c737a5b0b001be31ba5
  * typo in Petri net weight (reporter: dominiquesommers)
* 4a74ef159d03d3cf3ca43bd7c99f5f97da16baf8
  * problems in the evaluation of replay fitness of recomposed alignments
* 1f40a17dcade522d308b56a9f53b40c5b8a95dfc
  * cleaning circular dependencies. relaxing some absolutely strict dependencies for some border-line configurations.
* 9780ef609db7bbb24323d3584abc2338f24252d3 
  * copying of Event/Trace/EventStream/EventLog objects (reporter: M.Pegoraro)
* 51802f0828a6d207a5185c06a71bdb3a9faa1a46  
  * problem with sampling log (reporter: jacksbrajin)
* b1f16bf087691181adcf5616aa85e3e454a7169c
  * fixed problem with the discovery of 2-loops in the Heuristics Miner (reporter: czwilling)
* c96dcb16064ed156a1f48075445113bb5afc6264
  * fixed ```get_variants_acyclic()``` function in petri utils (authorship: M.Pegoraro)
   
### Removed

### Deprecated
* b4cea4be6fe6ff90f58c405f9f0acb4dbac973f4
  * factories are deprecated
   
### Changed
* b4cea4be6fe6ff90f58c405f9f0acb4dbac973f4
  * factories have been renamed 
   
### Added
* e8f250fec6781c088da8204923ad8817f1b5d689
  * decision point mining with alignments (for any scikit classification approach) is now integrated.
* 4ff811ab80b5df15e5ec1da082b4f76c72dcf684
  * trace attribute hierarchical clustering (MSc Thesis Yukun Cao; FIT/RWTH)
* 4fca12c1608818348bbd51e390140a8f7e79d7f6
  * alignments decomposition/recomposition
* f8d52aa69a3d720d45a93b35c79b4241bb8f7691
  * possibility to provide the final marking to the playout factory
* 9a5a64ea2941d69be07ee0e93b771c80f5820166
  * hash functions for event log objects
* 9f76d2e61dbc1cc74fccafac6f60d9ce69b7c791
  * added ```table_to_stream()``` auxiliary function in dataframe_utils   
   
### Other

---

## PM4PY 1.2.13 (2020.05.11)

### Fixed
* 531b767d85bb4c95996ae0c9644a958f75aad120
  * utilities of Petri nets (acyclic net variants (M. Pegoraro); strongly connected components by NX graph)
   
### Removed

### Deprecated

### Changed

### Added
* c9cebbfab9c82bf8edbe8851a000fd1b1f31f8be
  * ```properties``` object to all members of the Petri net class (including transitions/places/arcs)

### Other

---

## PM4PY 1.2.12 (2020.03.18)

### Fixed
* ef3b4b62fd186df46236a8af9aa890358dbcd1bc
  * problem in the generation of logs from process trees
* 548c57a6d2340dcaba7ef11464ebe193f8fb9c5c
  * filter by variants percentage
* c49a9c441feb65a74d5c5da774fdda79295665cc
  * problems of the token-based replay with the count of tokens at global and local level
* f554aec318717ee1fb7f81c4e0acbd6da7e7bc34 
  * continuous time Markov Chain steady-state analysis
* e05145de972944f211f2763656eb6e41aa64e0b5
  * revised process tree fold and tau reduce functions
* c3f66b8cb8667c2f204a1da899a216656386c2fa 
  * ignore comments in .pnml files
   
### Removed
* 31e1cd29437d6b183357bbc5c103131484d390b3
  * problematic dependencies ortools and pyarrow in the project (when installed, can be used, but no more required by default)

### Deprecated

### Changed

### Added
* f554aec318717ee1fb7f81c4e0acbd6da7e7bc34
  * converting a performance DFG to a Q-matrix for transient analysis
* cc766164f2397fe2cb33f8278372469e25cfecd6
  * business hours module supports full-days shifts (e.g. from 0 to 24)
* cc766164f2397fe2cb33f8278372469e25cfecd6
  * backwards state space exploration (supports duplicate transitions) for token-based replay
* 1b3c32916fe0ccbc4d3f73a44cc68e2ca83a810e
  * Visual log comparison on a Petri net by plasma coloring

### Other

---

## PM4PY 1.2.11 (2020.02.21)

### Fixed
* 6f320562a836cd949dbbe6ec7751f8f9514b01ec
  * parameter object for calling alignment code directly
* 471f414820c7b3f919aa97ccdc684d40cf132b3c
  * dependency problem with ORTools and PyArrow
* 157fadffd3b953c105e67f4909547f097d77ea0a
   * reduce inernal (cyclic) dependencies within PM4Py
* f38b6089b7eb6a4518a9c33e9775120874352657; af1328e2dad82f0a059e00942167a29cb918c85f; e8e1ab443f2dedb2cd348f35bc49eed412d66e1d
   * hash and equals function of process trees
* 229bd7ed78ea80aefbb6c7fcfa173edda682c1c7
   * refactoring of the Monte Carlo simulation.
     * extend the simulation to support arc weights that are provided by the replay (e.g. informed transition pickup)
     * extend the simulation to support more than one resource per place through semaphores
     * maximum execution time per simulation thread
     * general refactoring of the code
     * introduce logging information about the simulation
     * improving documentation
     * improving clarity of the code
* f5132302e06aa49f26ab3264bb3147d0660a11c0
  * performance of log generation from process trees
* 9e64f2635123aa5c3146fb2ad03863cbf93175df
  * fixed incongruency in variants statistics (was there for log, not for dataframes)
  * increased coverage of tests, and made some of them more lean
  * introduced some additional tests on the new functionalities
  * updated Dockerfile
  * updated setup with new packages
  * removed remainings of the SIMPLE algorithm in the tests folder
* 382162c648fb8e32b0145a6ff9427af8a7fb39fa
  * fixed parameters initialization to make it uniform for the rest of the project for all the versions of IMDF
  * added missing documentation in factory (was there only in the versions)
  * moved log conversions from factory to specific versions (since they are indeed version specific, if later we include the log version)
  * removed some useless calculations on the new DFG based versions (were there, but never used!)
  * introduced two new methods, apply_variants and apply_tree_variants, that are able to apply inductive miner from a list of variants
  * separated DEFAULT_VARIANT from DEFAULT_VARIANT_DFG (indeed, the first in future versions may become the log)
  * increased number of tests in the tests/ folder for inductive miner
 
### Removed
* 502c5d722d483c567f0e08c16da0bb4c87a94e36
  * remove the empty performance spectrum visualizer folder

### Deprecated

### Changed
* e8b030afd37559c93f79e1dd030fdc540aa62135 
  * provide fast-parquet library as an alternative to read/write parquet files.
   
### Added
* 557472bc78900d90beb0757279ef29b89aa410b1
  * integrate LogSkeleton for process discovery and conformance checking
* 90ba7bf1495fdac7ccef3112efa95687c46a5dd1
  * importing and exporting of Petri net weights

### Other

---       

## PM4PY 1.2.10 (2020.01.31)

### Fixed
* f571ec65ca544a9322b89cf96299d03da65de5a0
  * import DFG to PN
  * process tree parsing
* dca5cc602ba8381e5d4e265341dfc5a5292a80c0
  * problem with alignments when transitions have empty preset
* 68643cb109503e54787f98eb8f40650e37aa151e
  * process tree hashing
* 9d27f132d40638933be00f9d178e9a1167d36166
  * conversion between the log types

### Removed

### Deprecated

### Changed
* 945fd64e481c0fbf020da7f71cb1a7974ae9629c
  * make visualization deterministic for process trees, Petri nets and DFGs
* 15be58abb314c679ddf3b65fa6832c680768c413 
  * generic parsing of dates (removed strict dependency on ciso8601)
   
### Added

### Other

---

## PM4PY 1.2.9 (2020.01.24)

### Fixed
* be0a282be033765c9d1d7f1a7ba541a11c046834
  * matplotlib backend settings

### Removed

### Deprecated

### Changed
* ed42182f32eba37df71d9f466ad165036f8d1086
  * full support for numpy v1.18
* d1a418f8fa2513a469149383fe69df9a4e6fea06
  * full support pandas v1.0

### Added

### Other

---

## PM4PY 1.2.8 (2020.01.10)

### Fixed
* 6908a34c73c74c42aac3ddf31b964fcae680919e 
  * inductive miner sequence cut detection
* 881f1fa4e76b9e35c2d80ab7d241183b2d6871c0
  * 'Best effort fix' for graphviz based visualizations

### Removed

### Deprecated

### Changed

### Added

### Other

---

## PM4PY 1.2.7 (2019.12.20)

### Fixed
* programming error in the alignments code
* ```should_close``` for XOR node in PT generation
* ```execute_enabled``` for parallel and OR node in PT generation
* process tree children setter function

### Removed
* ```copy.copy``` for parent nodes of childs in log generation from process tree
* windows platform reuquirement for ortools/pyarrow

### Deprecated

### Changed
* recursion depth in token-based replay invisibles exploration
* consider only fitting traces in the Align-ETConformance count
* consider all the optimal alignments (as described in the paper) and not only the first one
* moving of utilities and making the search function using Dijkstra (since we are looking for fit paths) instead of A*
* LTL checker: making existing filters more performant (A eventually B eventually C)

### Added
* LTL checker: introducing A eventually B eventually C eventually D
* LTL checker: introducing time boundaries for each arc of the eventually follows relation

### Other
 
___

## PM4PY 1.2.6 (2019.11.29)

### Fixed
* bug fix in the 'escaping edges' based precision

### Removed

### Deprecated

### Changed

### Added
* Pyarrow serialization integration (supporting in-memory and to .pkl file serialization)

### Other
