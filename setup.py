import runpy
from os.path import dirname, join
from pathlib import Path
from setuptools import setup


# Import only the metadata of the pm4py to use in the setup. We cannot import it directly because
# then we need to import packages that are about to be installed by the setup itself.
meta_path = Path(__file__).parent.absolute() / "pm4py" / "meta.py"
meta = runpy.run_path(meta_path)


def read_file(filename):
    with open(join(dirname(__file__), filename)) as f:
        return f.read()


setup(
    name=meta['__name__'],
    version=meta['__version__'],
    description=meta['__doc__'].strip(),
    long_description=read_file('README.md'),
    author=meta['__author__'],
    author_email=meta['__author_email__'],
    py_modules=[meta['__name__']],
    include_package_data=True,
    packages=['pm4py', 'pm4py.algo', 'pm4py.algo.discovery', 'pm4py.algo.discovery.dfg',
              'pm4py.algo.discovery.dfg.utils', 'pm4py.algo.discovery.dfg.adapters',
              'pm4py.algo.discovery.dfg.adapters.pandas', 'pm4py.algo.discovery.dfg.variants',
              'pm4py.algo.discovery.alpha', 'pm4py.algo.discovery.alpha.utils', 'pm4py.algo.discovery.alpha.variants',
              'pm4py.algo.discovery.alpha.data_structures', 'pm4py.algo.discovery.causal',
              'pm4py.algo.discovery.causal.variants', 'pm4py.algo.discovery.inductive',
              'pm4py.algo.discovery.inductive.util', 'pm4py.algo.discovery.inductive.variants',
              'pm4py.algo.discovery.inductive.variants.im', 'pm4py.algo.discovery.inductive.variants.im.util',
              'pm4py.algo.discovery.inductive.variants.im.data_structures',
              'pm4py.algo.discovery.inductive.variants.im_d', 'pm4py.algo.discovery.inductive.variants.im_d.util',
              'pm4py.algo.discovery.inductive.variants.im_d.data_structures',
              'pm4py.algo.discovery.inductive.variants.im_f',
              'pm4py.algo.discovery.inductive.variants.im_f.data_structures', 'pm4py.algo.discovery.footprints',
              'pm4py.algo.discovery.footprints.dfg', 'pm4py.algo.discovery.footprints.dfg.variants',
              'pm4py.algo.discovery.footprints.log', 'pm4py.algo.discovery.footprints.log.variants',
              'pm4py.algo.discovery.footprints.tree', 'pm4py.algo.discovery.footprints.tree.variants',
              'pm4py.algo.discovery.footprints.petri', 'pm4py.algo.discovery.footprints.petri.variants',
              'pm4py.algo.discovery.heuristics', 'pm4py.algo.discovery.heuristics.variants',
              'pm4py.algo.discovery.log_skeleton', 'pm4py.algo.discovery.log_skeleton.variants',
              'pm4py.algo.discovery.temporal_profile', 'pm4py.algo.discovery.temporal_profile.variants',
              'pm4py.algo.discovery.transition_system', 'pm4py.algo.discovery.transition_system.variants',
              'pm4py.algo.discovery.correlation_mining', 'pm4py.algo.discovery.correlation_mining.variants',
              'pm4py.algo.filtering', 'pm4py.algo.filtering.dfg', 'pm4py.algo.filtering.log',
              'pm4py.algo.filtering.log.ltl', 'pm4py.algo.filtering.log.cases', 'pm4py.algo.filtering.log.paths',
              'pm4py.algo.filtering.log.variants', 'pm4py.algo.filtering.log.timestamp',
              'pm4py.algo.filtering.log.attributes', 'pm4py.algo.filtering.log.auto_filter',
              'pm4py.algo.filtering.log.end_activities', 'pm4py.algo.filtering.log.start_activities',
              'pm4py.algo.filtering.common', 'pm4py.algo.filtering.common.timestamp',
              'pm4py.algo.filtering.common.attributes', 'pm4py.algo.filtering.common.end_activities',
              'pm4py.algo.filtering.common.start_activities', 'pm4py.algo.filtering.pandas',
              'pm4py.algo.filtering.pandas.ltl', 'pm4py.algo.filtering.pandas.cases',
              'pm4py.algo.filtering.pandas.paths', 'pm4py.algo.filtering.pandas.variants',
              'pm4py.algo.filtering.pandas.timestamp', 'pm4py.algo.filtering.pandas.attributes',
              'pm4py.algo.filtering.pandas.auto_filter', 'pm4py.algo.filtering.pandas.end_activities',
              'pm4py.algo.filtering.pandas.start_activities', 'pm4py.algo.reduction', 'pm4py.algo.reduction.variants',
              'pm4py.algo.clustering', 'pm4py.algo.clustering.trace_attribute_driven',
              'pm4py.algo.clustering.trace_attribute_driven.dfg', 'pm4py.algo.clustering.trace_attribute_driven.util',
              'pm4py.algo.clustering.trace_attribute_driven.variants',
              'pm4py.algo.clustering.trace_attribute_driven.merge_log',
              'pm4py.algo.clustering.trace_attribute_driven.leven_dist',
              'pm4py.algo.clustering.trace_attribute_driven.linkage_method', 'pm4py.algo.conformance',
              'pm4py.algo.conformance.alignments', 'pm4py.algo.conformance.alignments.variants',
              'pm4py.algo.conformance.footprints', 'pm4py.algo.conformance.footprints.util',
              'pm4py.algo.conformance.footprints.variants', 'pm4py.algo.conformance.tokenreplay',
              'pm4py.algo.conformance.tokenreplay.variants', 'pm4py.algo.conformance.tokenreplay.diagnostics',
              'pm4py.algo.conformance.log_skeleton', 'pm4py.algo.conformance.log_skeleton.variants',
              'pm4py.algo.conformance.logs_alignments', 'pm4py.algo.conformance.logs_alignments.variants',
              'pm4py.algo.conformance.tree_alignments', 'pm4py.algo.conformance.tree_alignments.variants',
              'pm4py.algo.conformance.tree_alignments.variants.approximated', 'pm4py.algo.conformance.temporal_profile',
              'pm4py.algo.conformance.temporal_profile.variants', 'pm4py.algo.conformance.decomp_alignments',
              'pm4py.algo.conformance.decomp_alignments.variants', 'pm4py.algo.enhancement',
              'pm4py.algo.enhancement.sna', 'pm4py.algo.enhancement.sna.variants',
              'pm4py.algo.enhancement.sna.variants.log', 'pm4py.algo.enhancement.sna.variants.pandas',
              'pm4py.algo.enhancement.roles', 'pm4py.algo.enhancement.roles.common',
              'pm4py.algo.enhancement.roles.variants', 'pm4py.algo.enhancement.decision',
              'pm4py.algo.enhancement.comparison', 'pm4py.algo.enhancement.comparison.petrinet', 'pm4py.util',
              'pm4py.util.lp', 'pm4py.util.lp.util', 'pm4py.util.lp.variants', 'pm4py.util.dt_parsing',
              'pm4py.util.dt_parsing.variants', 'pm4py.objects', 'pm4py.objects.dfg', 'pm4py.objects.dfg.utils',
              'pm4py.objects.dfg.exporter', 'pm4py.objects.dfg.exporter.variants', 'pm4py.objects.dfg.importer',
              'pm4py.objects.dfg.importer.variants', 'pm4py.objects.dfg.filtering', 'pm4py.objects.dfg.retrieval',
              'pm4py.objects.log', 'pm4py.objects.log.util', 'pm4py.objects.log.exporter',
              'pm4py.objects.log.exporter.xes', 'pm4py.objects.log.exporter.xes.util',
              'pm4py.objects.log.exporter.xes.variants', 'pm4py.objects.log.importer', 'pm4py.objects.log.importer.xes',
              'pm4py.objects.log.importer.xes.variants', 'pm4py.objects.bpmn', 'pm4py.objects.bpmn.util',
              'pm4py.objects.bpmn.layout', 'pm4py.objects.bpmn.layout.variants', 'pm4py.objects.bpmn.exporter',
              'pm4py.objects.bpmn.exporter.variants', 'pm4py.objects.bpmn.importer',
              'pm4py.objects.bpmn.importer.variants', 'pm4py.objects.petri', 'pm4py.objects.petri.common',
              'pm4py.objects.petri.exporter', 'pm4py.objects.petri.exporter.variants', 'pm4py.objects.petri.importer',
              'pm4py.objects.petri.importer.variants', 'pm4py.objects.conversion', 'pm4py.objects.conversion.dfg',
              'pm4py.objects.conversion.dfg.variants', 'pm4py.objects.conversion.log',
              'pm4py.objects.conversion.log.variants', 'pm4py.objects.conversion.bpmn',
              'pm4py.objects.conversion.bpmn.variants', 'pm4py.objects.conversion.wf_net',
              'pm4py.objects.conversion.wf_net.variants', 'pm4py.objects.conversion.process_tree',
              'pm4py.objects.conversion.process_tree.variants', 'pm4py.objects.conversion.heuristics_net',
              'pm4py.objects.conversion.heuristics_net.variants', 'pm4py.objects.process_tree',
              'pm4py.objects.process_tree.exporter', 'pm4py.objects.process_tree.exporter.variants',
              'pm4py.objects.process_tree.importer', 'pm4py.objects.process_tree.importer.variants',
              'pm4py.objects.heuristics_net', 'pm4py.objects.random_variables', 'pm4py.objects.random_variables.normal',
              'pm4py.objects.random_variables.uniform', 'pm4py.objects.random_variables.constant0',
              'pm4py.objects.random_variables.exponential', 'pm4py.objects.stochastic_petri',
              'pm4py.objects.transition_system', 'pm4py.streaming', 'pm4py.streaming.algo',
              'pm4py.streaming.algo.discovery', 'pm4py.streaming.algo.discovery.dfg',
              'pm4py.streaming.algo.discovery.dfg.variants', 'pm4py.streaming.algo.conformance',
              'pm4py.streaming.algo.conformance.tbr', 'pm4py.streaming.algo.conformance.tbr.variants',
              'pm4py.streaming.algo.conformance.temporal', 'pm4py.streaming.algo.conformance.temporal.variants',
              'pm4py.streaming.algo.conformance.footprints', 'pm4py.streaming.algo.conformance.footprints.variants',
              'pm4py.streaming.util', 'pm4py.streaming.util.dictio', 'pm4py.streaming.util.dictio.versions',
              'pm4py.streaming.stream', 'pm4py.streaming.importer', 'pm4py.streaming.importer.csv',
              'pm4py.streaming.importer.csv.variants', 'pm4py.streaming.importer.xes',
              'pm4py.streaming.importer.xes.variants', 'pm4py.evaluation', 'pm4py.evaluation.wf_net',
              'pm4py.evaluation.wf_net.variants', 'pm4py.evaluation.precision', 'pm4py.evaluation.precision.variants',
              'pm4py.evaluation.soundness', 'pm4py.evaluation.soundness.woflan',
              'pm4py.evaluation.soundness.woflan.graphs', 'pm4py.evaluation.soundness.woflan.graphs.reachability_graph',
              'pm4py.evaluation.soundness.woflan.graphs.minimal_coverability_graph',
              'pm4py.evaluation.soundness.woflan.graphs.restricted_coverability_graph',
              'pm4py.evaluation.soundness.woflan.place_invariants',
              'pm4py.evaluation.soundness.woflan.not_well_handled_pairs', 'pm4py.evaluation.simplicity',
              'pm4py.evaluation.simplicity.variants', 'pm4py.evaluation.generalization',
              'pm4py.evaluation.generalization.variants', 'pm4py.evaluation.replay_fitness',
              'pm4py.evaluation.replay_fitness.variants', 'pm4py.evaluation.earth_mover_distance',
              'pm4py.evaluation.earth_mover_distance.variants', 'pm4py.simulation', 'pm4py.simulation.playout',
              'pm4py.simulation.playout.variants', 'pm4py.simulation.montecarlo', 'pm4py.simulation.montecarlo.utils',
              'pm4py.simulation.montecarlo.variants', 'pm4py.simulation.tree_playout',
              'pm4py.simulation.tree_playout.variants', 'pm4py.simulation.tree_generator',
              'pm4py.simulation.tree_generator.variants', 'pm4py.statistics', 'pm4py.statistics.util',
              'pm4py.statistics.traces', 'pm4py.statistics.traces.log', 'pm4py.statistics.traces.common',
              'pm4py.statistics.traces.pandas', 'pm4py.statistics.variants', 'pm4py.statistics.variants.log',
              'pm4py.statistics.variants.pandas', 'pm4py.statistics.attributes', 'pm4py.statistics.attributes.log',
              'pm4py.statistics.attributes.common', 'pm4py.statistics.attributes.pandas',
              'pm4py.statistics.passed_time', 'pm4py.statistics.passed_time.log',
              'pm4py.statistics.passed_time.log.variants', 'pm4py.statistics.passed_time.pandas',
              'pm4py.statistics.passed_time.pandas.variants', 'pm4py.statistics.sojourn_time',
              'pm4py.statistics.sojourn_time.log', 'pm4py.statistics.sojourn_time.pandas',
              'pm4py.statistics.end_activities', 'pm4py.statistics.end_activities.log',
              'pm4py.statistics.end_activities.common', 'pm4py.statistics.end_activities.pandas',
              'pm4py.statistics.start_activities', 'pm4py.statistics.start_activities.log',
              'pm4py.statistics.start_activities.common', 'pm4py.statistics.start_activities.pandas',
              'pm4py.statistics.eventually_follows', 'pm4py.statistics.eventually_follows.log',
              'pm4py.statistics.eventually_follows.pandas', 'pm4py.statistics.performance_spectrum',
              'pm4py.statistics.performance_spectrum.variants', 'pm4py.statistics.concurrent_activities',
              'pm4py.statistics.concurrent_activities.log', 'pm4py.statistics.concurrent_activities.pandas',
              'pm4py.visualization', 'pm4py.visualization.dfg', 'pm4py.visualization.dfg.variants',
              'pm4py.visualization.sna', 'pm4py.visualization.sna.variants', 'pm4py.visualization.bpmn',
              'pm4py.visualization.bpmn.variants', 'pm4py.visualization.common', 'pm4py.visualization.graphs',
              'pm4py.visualization.graphs.util', 'pm4py.visualization.graphs.variants', 'pm4py.visualization.petrinet',
              'pm4py.visualization.petrinet.util', 'pm4py.visualization.petrinet.common',
              'pm4py.visualization.petrinet.variants', 'pm4py.visualization.footprints',
              'pm4py.visualization.footprints.variants', 'pm4py.visualization.align_table',
              'pm4py.visualization.align_table.variants', 'pm4py.visualization.decisiontree',
              'pm4py.visualization.decisiontree.variants', 'pm4py.visualization.process_tree',
              'pm4py.visualization.process_tree.variants', 'pm4py.visualization.heuristics_net',
              'pm4py.visualization.heuristics_net.variants', 'pm4py.visualization.transition_system',
              'pm4py.visualization.transition_system.util', 'pm4py.visualization.transition_system.variants'],
    url='http://www.pm4py.org',
    license='GPL 3.0',
    install_requires=[
        'ciso8601; python_version < \'3.7\'',
        'cvxopt; python_version < \'3.9\'',
        'deprecation',
        'graphviz',
        'intervaltree',
        'jsonpickle',
        'lxml',
        'matplotlib',
        'networkx',
        'numpy!=1.19.4',
        'pandas',
        'pulp<=2.1',
        'pydotplus',
        'pytz',
        'pyvis',
        'scikit-learn',
        'scipy',
        'stringdist',
        'sympy',
        'tqdm'

    ],
    project_urls={
        'Documentation': 'http://www.pm4py.org',
        'Source': 'https://github.com/pm4py/pm4py-source',
        'Tracker': 'https://github.com/pm4py/pm4py-source/issues',
    }
)
