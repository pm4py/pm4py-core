import pm4py


def execute_script():
    log = pm4py.read_xes("../tests/input_data/helpdesk.xes.gz", return_legacy_log_object=True)

    # discovers the POWL model
    powl_model = pm4py.discover_powl(log)

    # prints the repr of the POWL model
    print(powl_model)

    # views the POWL model on the screen
    pm4py.view_powl(powl_model, format="svg")

    # converts the POWL model to a Petri net (which can be used for conformance checking)
    net, im, fm = pm4py.convert_to_petri_net(powl_model)
    pm4py.view_petri_net(net, im, fm, format="svg")


if __name__ == "__main__":
    execute_script()
