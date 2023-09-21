import pm4py

from copy import deepcopy
from pm4py.algo.discovery.dcr_discover import algorithm as alg
from pm4py.objects.dcr.exporter import exporter as dcr_exporter


def run_discover_config(event_log_file, variant, result_file_prefix, dcr_title, config=None):
    if config is None:
        config = {
            'findAdditionalConditions': True,
            'inBetweenRels': True,
            'timed': False,
            'discardSelfInPredecessors': True,
            'usePredecessors': False
        }
    t = ''
    if config['timed'] == True:
        t = 'T'
    print(f'[i] Started with config: {config}')
    rfp = result_file_prefix
    event_log = pm4py.read_xes(event_log_file, return_legacy_log_object=True)
    print('[i] Mining a DCR Model with DisCoveR!')
    export_path = f'models/{rfp}.xml'
    la = None
    sp_log = None
    if variant == alg.DCR_BASIC:
        dcr_model, la = alg.apply(event_log, alg.DCR_BASIC, **config)
    else:
        dcr_model, sp_log = alg.apply(event_log, alg.DCR_SUBPROCESS, **config)
    dcr_exporter.apply(dcr_graph=dcr_model,
                       path=export_path,
                       variant=dcr_exporter.XML_SIMPLE,
                       dcr_title=dcr_title,
                       dcr_description=dcr_title)
    print(f'[!] Model saved in {export_path}')
    return dcr_model, la if la is not None else sp_log


def benchmark_subprocess_no_i2e_e2i(event_log_file, result_file_prefix, dcr_title, config=None):
    if config is None:
        config = {
            'findAdditionalConditions': True,
            'inBetweenRels': False,
            'timed': False,
            'discardSelfInPredecessors': True,
            'usePredecessors': False
        }
    t = ''
    if config['timed'] == True:
        t = 'T'
    print(f'[i] Started with config: {config}')
    rfp = result_file_prefix
    event_log = pm4py.read_xes(event_log_file, return_legacy_log_object=True)
    print('[i] Mining with SpT-DisCoveR - (ME) no i2e or e2i!')
    export_path = f'models/{rfp}_Sp{t}_no_i2e_e2i.xml'
    config2 = deepcopy(config)
    config2['inBetweenRels'] = False
    sp_no_i2e_e2i_dcr, sp_no_i2e_e2i_log = alg.apply(event_log, alg.DCR_SUBPROCESS, **config)
    dcr_exporter.apply(dcr_graph=sp_no_i2e_e2i_dcr,
                       path=export_path,
                       variant=dcr_exporter.XML_SIMPLE,
                       dcr_title=dcr_title,
                       dcr_description=f"Sp{t}-no i2e oe e21")
    print(f'[!] Model saved in {export_path}')
    return sp_no_i2e_e2i_dcr, sp_no_i2e_e2i_log


def benchmark_event_log_from_configs(event_log_file, result_file_prefix, dcr_title, configs=[]):
    """
    example of configs:
        configs = [{
            'inBetweenRels': True,
            'timed': True,
            'variant': DCR_SUBPROCESS_ME
        }]
    """
    if isinstance(event_log_file, pm4py.objects.log.obj.EventLog):
        event_log = event_log_file
    else:
        event_log = pm4py.read_xes(event_log_file, return_legacy_log_object=True)
    rfp = result_file_prefix
    i = 0
    res = []
    for config in configs:
        print(f'[i] Started with config: {config}')
        el = deepcopy(event_log)
        t = ''
        if config['timed'] == True:
            t = 'T'
        export_path = f'models/{rfp}_{t}_config{i}.xml'
        dcr, log = alg.apply(el, **config)
        dcr_exporter.apply(dcr_graph=dcr,
                           path=export_path,
                           variant=dcr_exporter.XML_SIMPLE,
                           dcr_title=dcr_title,
                           dcr_description=dcr_title)
        i = i + 1
        res.append(dcr)
        print(f'[!] Model saved in {export_path}')
    return res


def benchmark_event_log(event_log_file, result_file_prefix, dcr_title, config=None):
    if config is None:
        config = {
            'findAdditionalConditions': True,
            'inBetweenRels': True,
            'timed': True,
            'discardSelfInPredecessors': True,
            'usePredecessors': False
        }
    t = ''
    if config['timed'] == True:
        t = 'T'
    print(f'[i] Started with config: {config}')
    rfp = result_file_prefix
    event_log = pm4py.read_xes(event_log_file, return_legacy_log_object=True)
    reference_event_log = deepcopy(event_log)

    print('[i] Mining with DisCoveR!')
    export_path = f'models/{rfp}_{t}DisCoveR.xml'
    reference_dcr, la = alg.apply(reference_event_log, alg.DCR_BASIC, **config)
    dcr_exporter.apply(dcr_graph=reference_dcr,
                       path=export_path,
                       variant=dcr_exporter.XML_SIMPLE,
                       dcr_title=dcr_title,
                       dcr_description=f"Basic {t}DisCoveR")
    print(f'[!] Model saved in {export_path}')

    print('[i] Mining with SpT-DisCoveR - mutual exclusion (ME)!')
    export_path = f'models/{rfp}_Sp{t}.xml'
    spme_dcr, spme_log = alg.apply(event_log, alg.DCR_SUBPROCESS, **config)
    dcr_exporter.apply(dcr_graph=spme_dcr,
                       path=export_path,
                       variant=dcr_exporter.XML_SIMPLE,
                       dcr_title=dcr_title,
                       dcr_description=f"Sp{t}-ME")
    print(f'[!] Model saved in {export_path}')

    if config['usePredecessors']:
        print('[i] Mining with SpT-DisCoveR - predecessors!')
        export_path = f'models/{rfp}_Sp{t}_preds.xml'
        sp_dcr, sp_log = alg.apply(event_log, alg.DCR_SUBPROCESS, **config)
        dcr_exporter.apply(dcr_graph=sp_dcr,
                           path=export_path,
                           variant=dcr_exporter.XML_SIMPLE,
                           dcr_title=dcr_title,
                           dcr_description=f"Sp{t}")
        print(f'[!] Model saved in {export_path}')
        print('[i] Done!')
        return reference_dcr, reference_event_log, spme_dcr, spme_log, sp_dcr, sp_log
    else:
        return reference_dcr, reference_event_log, spme_dcr, spme_log
