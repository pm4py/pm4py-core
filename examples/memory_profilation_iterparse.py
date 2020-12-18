from pm4py.objects.log.importer.xes import importer as xes_importer
import memory_profiler
import time
import os

log_path = os.path.join("..", "tests", "input_data", "receipt.xes")


def nothing():
    time.sleep(3)


def import_memory_efficient():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.ITERPARSE_MEM_COMPRESSED)


def import_classic():
    log = xes_importer.apply(log_path, variant=xes_importer.Variants.ITERPARSE)


def execute_script():
    memory_usage = memory_profiler.memory_usage(nothing)
    nothing_usage = max(memory_usage)
    aa = time.time()
    memory_usage_iterparse_efficient = memory_profiler.memory_usage(import_memory_efficient)
    bb = time.time()
    print(log_path, "iterparse memory efficient time", bb-aa)
    print(log_path, "iterparse memory efficient memory occupation", max(memory_usage_iterparse_efficient) - nothing_usage)
    aa = time.time()
    memory_usage_iterparse_classic = memory_profiler.memory_usage(import_classic)
    bb = time.time()
    print(log_path, "iterparse classic time", bb-aa)
    print(log_path, "iterparse classic memory occupation", max(memory_usage_iterparse_classic) - nothing_usage)


if __name__ == "__main__":
    execute_script()
