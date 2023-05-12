import os
import time

import memory_profiler

from pm4py.objects.log.importer.xes import importer as xes_importer

log_path = os.path.join("..", "tests", "input_data", "receipt.xes")


def nothing():
    time.sleep(3)


def import_memory_efficient():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.ITERPARSE_MEM_COMPRESSED)


def import_classic():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.ITERPARSE)


def import_line_by_line():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.LINE_BY_LINE)


def import_line_by_line_only_conceptname_and_timetimestamp():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.LINE_BY_LINE, parameters={
        xes_importer.Variants.LINE_BY_LINE.value.Parameters.SET_ATTRIBUTES_TO_READ: {"concept:name", "time:timestamp"}})


def import_line_by_line_only_conceptname():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.LINE_BY_LINE, parameters={
        xes_importer.Variants.LINE_BY_LINE.value.Parameters.SET_ATTRIBUTES_TO_READ: {"concept:name"}})


def execute_script():
    memory_usage = memory_profiler.memory_usage(nothing)
    nothing_usage = max(memory_usage)
    aa = time.time()
    memory_usage_iterparse_efficient = memory_profiler.memory_usage(import_memory_efficient)
    bb = time.time()
    print(log_path, "iterparse memory efficient time", bb - aa)
    print(log_path, "iterparse memory efficient memory occupation",
          max(memory_usage_iterparse_efficient) - nothing_usage)
    aa = time.time()
    memory_usage_iterparse_classic = memory_profiler.memory_usage(import_classic)
    bb = time.time()
    print(log_path, "iterparse classic time", bb - aa)
    print(log_path, "iterparse classic memory occupation", max(memory_usage_iterparse_classic) - nothing_usage)
    aa = time.time()
    memory_usage_line_by_line = memory_profiler.memory_usage(import_line_by_line)
    bb = time.time()
    print(log_path, "line by line time", bb - aa)
    print(log_path, "line by line memory occupation", max(memory_usage_line_by_line) - nothing_usage)
    aa = time.time()
    memory_usage_line_by_line_only_cn_and_tt = memory_profiler.memory_usage(
        import_line_by_line_only_conceptname_and_timetimestamp)
    bb = time.time()
    print(log_path, "line by line only cn and tt time", bb - aa)
    print(log_path, "line by line only cn and tt memory occupation",
          max(memory_usage_line_by_line_only_cn_and_tt) - nothing_usage)
    aa = time.time()
    memory_usage_line_by_line_only_cn = memory_profiler.memory_usage(
        import_line_by_line_only_conceptname)
    bb = time.time()
    print(log_path, "line by line only cn time", bb - aa)
    print(log_path, "line by line only cn memory occupation",
          max(memory_usage_line_by_line_only_cn) - nothing_usage)


if __name__ == "__main__":
    execute_script()
