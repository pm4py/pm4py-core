import os
import time
import pandas as pd
import pm4py

from math import sqrt
from pathlib import Path

from pm4py.algo.discovery.dcr_discover.algorithm import Variants
from pm4py.util.benchmarking import *
from pm4py.algo.evaluation.simplicity.variants import dcr_relations as dcr_simplicity
from pm4py.algo.evaluation.confusion_matrix.algorithm import fitness
from pm4py.objects.dcr import semantics_obj as dcr_semantics


def pdcFscore(tp, fp, tn, fn):
    try:
        posAcc = tp / (tp + fn)
        negAcc = tn / (tn + fp)
        res = 2 * posAcc * negAcc / (posAcc + negAcc)
        return res
    except:
        return 0


def fscore(tp, fp, tn, fn):
    try:
        recall = tp / (tp + fn)
        prec = tp / (tp + fp)
        res = 2 * recall * prec / (recall + prec)
        return res
    except:
        return 0


def balancedAccuracy(tp, fp, tn, fn):
    try:
        posAcc = tp / (tp + fn)
        negAcc = tn / (tn + fp)
        res = (posAcc + negAcc) / 2
        return res
    except:
        return 0


def mcc(tp, fp, tn, fn):
    try:
        num = tp * tn - fp * fn
        tmp = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        denom = sqrt(tmp)
        res = num / denom
        return res
    except:
        return 0


def train_dcr_model(train, config):
    dcr_model, _ = alg.apply(train, **config)
    return dcr_model


def score_one_model(dcr_model, ground_truth_log):
    gt = ground_truth_log
    gt_cases = pm4py.convert_to_dataframe(gt).groupby('case:concept:name').first()['case:pdc:isPos']
    # test_log = pm4py.convert_to_dataframe(test)
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for trace in gt:  # the trace is without subprocesses
        gt_is_pos = gt_cases[trace.attributes['concept:name']]
        dcr = deepcopy(dcr_model)
        semantics = dcr_semantics.DcrSemantics(dcr, cmd_print=False)
        can_execute = True
        events_so_far = []
        for event in trace:
            # How to project an execution in a subprocess dcr from an event log without them
            (executed, _) = semantics.execute(event['concept:name'])  # the graph is with subprocesses
            events_so_far.append(event['concept:name'])
            if executed is False:
                # if gt_is_pos:
                # print(f"[!] Failing at: {event['concept:name']}")
                # print(f'[Events so far] {events_so_far}')
                can_execute = False
                break
        accepting = semantics.is_accepting()
        test_is_pos = False
        if can_execute and accepting:
            test_is_pos = True
        if test_is_pos:
            if gt_is_pos:
                tp += 1
            else:
                fp += 1
        else:
            if gt_is_pos:
                fn += 1
            else:
                tn += 1
    print(f'tp: {tp}| fp: {fp} | tn: {tn} | fn: {fn}')
    return tp, fp, tn, fn


def compare_two_models(dcr_model_1, dcr_model_2, ground_truth_log):
    gt = ground_truth_log
    gt_df = pm4py.convert_to_dataframe(ground_truth_log)
    for trace in gt:  # the trace is without subprocesses
        dcr_1 = deepcopy(dcr_model_1)
        dcr_2 = deepcopy(dcr_model_2)
        semantics_1 = dcr_semantics.DcrSemantics(dcr_1, cmd_print=False)
        semantics_2 = dcr_semantics.DcrSemantics(dcr_2, cmd_print=False)
        events_so_far = []
        no_of_events_until_fail = 0
        dif_in_exec = 0
        count = True
        for event in trace:
            # How to project an execution in a subprocess dcr from an event log without them
            (executed_1, _) = semantics_1.execute(event['concept:name'])  # the graph is with subprocesses
            (executed_2, _) = semantics_2.execute(event['concept:name'])
            if count:
                events_so_far.append(event['concept:name'])
                no_of_events_until_fail += 1
            if executed_1 != executed_2:  # execution is different
                count = False
                dif_in_exec += 1
                if executed_1 is False:  # first model failed
                    print(f'[x] model 1 failed on event: {event["concept:name"]}')
                elif executed_1 is True:  # second model failed
                    print(f'[x] model 2 failed on event: {event["concept:name"]}')
            elif executed_1 is False:
                pass
        accepting_1 = semantics_1.is_accepting()
        accepting_2 = semantics_2.is_accepting()
        failed = False
        if accepting_1 != accepting_2:  # acceptance state at the end is different
            failed = True
            if accepting_1 is False:  # first model failed
                print(f'[x] Acceptance criteria not met on model 1')
            elif accepting_1 is True:  # second model failed
                print(f'[x] Acceptance criteria not met on model 2')
            print(f'[x] Failed acceptance criteria!')
        if dif_in_exec > 0:
            failed = True
            print(f'[x] Failed after {no_of_events_until_fail} event executions!')
        if failed:
            cid = trace.attributes["concept:name"]
            print(f'[x] Failed on trace: {cid}')
            print(events_so_far)
            print(gt_df[gt_df['case:concept:name'] == cid]['concept:name'].tolist())


def score_everything(
        base_dir='/home/vco/Datasets',
        folders=None,
        special_folders=None):
    if folders is None:
        folders = ['PDC19', 'PDC20', 'PDC21', 'PDC22']
    if special_folders is None:
        special_folders = ['PDC21', 'PDC22']
    sub_folders = ['Ground Truth Logs', 'Test Logs', 'Training Logs']
    # now just take all .xes files and make sure they match across folders
    temp_results = []
    for folder in folders:
        print(f'[i] Started for {folder}')
        for log_name in os.listdir(os.path.join(base_dir, folder, sub_folders[0])):
            print(f'[i] Log {log_name}')
            gt = pm4py.read_xes(os.path.join(base_dir, folder, sub_folders[0], log_name), return_legacy_log_object=True,
                                show_progress_bar=False)
            # test = pm4py.read_xes(os.path.join(base_dir,folder,sub_folders[1],log_name),return_legacy_log_object=True)

            if folder in special_folders:
                specific_log = f'{Path(log_name).stem}{0}.xes'
                train = pm4py.read_xes(os.path.join(base_dir, folder, sub_folders[2], specific_log),
                                       return_legacy_log_object=True, show_progress_bar=False)
            else:
                train = pm4py.read_xes(os.path.join(base_dir, folder, sub_folders[2], log_name),
                                       return_legacy_log_object=True, show_progress_bar=False)
            # run the basic DisCoveR, Sp-DisCoveR and Sp-DisCoveR without in between relations
            # run basic
            config = {
                'timed': False,
                'pending': False,
                'variant': Variants.DCR_BASIC
            }
            start_time = time.time()
            dcr_basic = train_dcr_model(train, config)
            elapsed = time.time() - start_time
            sim = dcr_simplicity.get_simplicity(dcr_basic)
            fit = fitness(train, dcr_basic)
            tp, fp, tn, fn = score_one_model(dcr_basic, gt)
            pdc_f_score = pdcFscore(tp, fp, tn, fn)
            f_score = fscore(tp, fp, tn, fn)
            b_acc = balancedAccuracy(tp, fp, tn, fn)
            m_c_c = mcc(tp, fp, tn, fn)
            temp_results.append({
                'PDC Year': folder,
                'Log name': log_name,
                'Algorithm': 'DisCoveR',
                'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,
                'Fscore (PDC)': pdc_f_score,
                'Fscore': f_score,
                'balancedAccuracy': b_acc,
                'mcc': m_c_c,
                'Fitness': fit[0] / fit[1],  # fitness is on training
                'Simplicity': sim[0],
                'Subprocesses': 0,
                'Events': len(dcr_basic['events']),
                'Runtime': elapsed
            })

            # run subprocess standard
            config = {
                'inBetweenRels': True,
                'timed': False,
                'pending': True,
                'variant': Variants.DCR_SUBPROCESS_ME,
            }
            start_time = time.time()
            dcr_subprocess_standard = train_dcr_model(train, config)
            elapsed = time.time() - start_time

            sim = dcr_simplicity.get_simplicity(dcr_subprocess_standard)
            fit = fitness(train, dcr_subprocess_standard)
            tp, fp, tn, fn = score_one_model(dcr_subprocess_standard, gt)
            pdc_f_score = pdcFscore(tp, fp, tn, fn)
            f_score = fscore(tp, fp, tn, fn)
            b_acc = balancedAccuracy(tp, fp, tn, fn)
            m_c_c = mcc(tp, fp, tn, fn)
            temp_results.append({
                'PDC Year': folder,
                'Log name': log_name,
                'Algorithm': 'Sp-DisCoveR',
                'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,
                'Fscore (PDC)': pdc_f_score,
                'Fscore': f_score,
                'balancedAccuracy': b_acc,
                'mcc': m_c_c,
                'Fitness': fit[0] / fit[1],  # fitness is on training
                'Simplicity': sim[0],
                'Subprocesses': len(dcr_subprocess_standard['subprocesses']),
                'Events': len(dcr_subprocess_standard['events']),
                'Runtime': elapsed
            })

            # run subprocess no i2e e2i
            config = {
                'inBetweenRels': False,
                'timed': False,
                'pending': True,
                'variant': Variants.DCR_SUBPROCESS_ME,
            }
            start_time = time.time()
            dcr_subprocess_no_in_between = train_dcr_model(train, config)
            elapsed = time.time() - start_time

            sim = dcr_simplicity.get_simplicity(dcr_subprocess_no_in_between)
            fit = fitness(train, dcr_subprocess_no_in_between)
            tp, fp, tn, fn = score_one_model(dcr_subprocess_no_in_between, gt)
            pdc_f_score = pdcFscore(tp, fp, tn, fn)
            f_score = fscore(tp, fp, tn, fn)
            b_acc = balancedAccuracy(tp, fp, tn, fn)
            m_c_c = mcc(tp, fp, tn, fn)
            temp_results.append({
                'PDC Year': folder,
                'Log name': log_name,
                'Algorithm': 'Sp-DisCoveR_no_i2e_e2i',
                'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,
                'Fscore (PDC)': pdc_f_score,
                'Fscore': f_score,
                'balancedAccuracy': b_acc,
                'mcc': m_c_c,
                'Fitness': fit[0] / fit[1],  # fitness is on training
                'Simplicity': sim[0],
                'Subprocesses': len(dcr_subprocess_no_in_between['subprocesses']),
                'Events': len(dcr_subprocess_no_in_between['events']),
                'Runtime': elapsed
            })
        print(f'[i] Done for {folder}')
    results = pd.DataFrame(
        columns=['PDC Year', 'Log name', 'Algorithm', 'TP', 'FP', 'TN', 'FN', 'Fscore (PDC)', 'Fscore',
                 'balancedAccuracy', 'mcc', 'Fitness', 'Simplicity', 'Subprocesses', 'Events', 'Runtime'],
        data=temp_results)
    results.to_csv(path_or_buf='/home/vco/Projects/pm4py-dcr/models/results.csv', index=False)
    return results

    # train on the training logs
    # get the isPos for each trace in the Ground Truth log
    # compare the isPos with the prediction on the test for some stupid reason the gt == test plus the isPos tag
    # do aggregated results too
