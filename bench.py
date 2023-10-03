import time
import cProfile
import functools

from collections import deque

import pm4py


# Take from somewhere on stack overflow
def time_callback(callback):
    start_time = time.perf_counter()
    value = callback()
    end_time = time.perf_counter()
    run_time = end_time - start_time
    return value, run_time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return time_callback(lambda: func(*args, **kwargs))

    return wrapper


def main():
    profile = False

    models = ['M1', 'M2', 'M7', 'ML2', 'ML4']
    for model in models:
        if profile:
            with cProfile.Profile() as pr:
                benchmark_for_model(model)
                pr.print_stats(sort='tottime')
        else:
            benchmark_for_model(model)


def benchmark_for_model(model_name: str):
    file_name = f'{model_name}.pnml'
    net, im, _ = pm4py.read_pnml(file_name)
    semantics = pm4py.objects.petri_net.semantics.ClassicSemantics()
    semantics = pm4py.objects.petri_net.compiled_semantics.CompiledClassicSemantics(net)

    visited_markings, total_time = do_run_benchmark(net, im, semantics)
    print(model_name, len(visited_markings), total_time, sep='\t')


@timer
def do_run_benchmark(net, im, semantics):
    to_visit = deque([im])
    seen_markings = set(im)

    while len(to_visit) != 0:
        current_marking = to_visit.popleft()

        for enabled_transition in semantics.enabled_transitions(net, current_marking):
            next_marking = semantics.weak_execute(enabled_transition, net, current_marking)
            if next_marking not in seen_markings:
                to_visit.append(next_marking)
                seen_markings.add(next_marking)

    return seen_markings


if __name__ == '__main__':
    main()
