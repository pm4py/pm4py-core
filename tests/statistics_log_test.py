import unittest
import os


class StatisticsLogTest(unittest.TestCase):
    def get_log(self):
        from pm4py.objects.log.importer.xes import importer
        log = importer.apply(os.path.join("input_data", "roadtraffic100traces.xes"))
        return log

    def test_get_attributes(self):
        from pm4py.statistics.attributes.log import get
        log = self.get_log()
        get.get_attribute_values(log, "concept:name")
        get.get_kde_date_attribute(log, "time:timestamp")
        get.get_kde_numeric_attribute(log, "amount")

    def test_select_attributes(self):
        from pm4py.statistics.attributes.log import select
        log = self.get_log()
        select.get_trace_attribute_values(log, "concept:name")
        select.select_attributes_from_log_for_tree(log)

    def test_end_activities(self):
        from pm4py.statistics.end_activities.log import get
        log = self.get_log()
        get.get_end_activities(log)

    def test_start_activities(self):
        from pm4py.statistics.start_activities.log import get
        log = self.get_log()
        get.get_start_activities(log)

    def test_case_arrival(self):
        from pm4py.statistics.traces.generic.log import case_arrival
        log = self.get_log()
        case_arrival.get_case_arrival_avg(log)
        case_arrival.get_case_dispersion_avg(log)

    def test_case_statistics(self):
        from pm4py.statistics.traces.generic.log import case_statistics
        log = self.get_log()
        case_statistics.get_kde_caseduration(log)
        case_statistics.get_events(log, "N77802")
        case_statistics.get_variant_statistics(log)
        case_statistics.get_cases_description(log)
        case_statistics.get_all_casedurations(log)
        case_statistics.get_first_quartile_caseduration(log)
        case_statistics.get_median_caseduration(log)

    def test_variants(self):
        from pm4py.statistics.variants.log import get
        log = self.get_log()
        get.get_variants(log)
        get.get_variants_along_with_case_durations(log)
        get.get_variants_from_log_trace_idx(log)



if __name__ == "__main__":
    unittest.main()
