import os
import subprocess
import sys
import textwrap
import unittest


class Pm4pyImportPackageTest(unittest.TestCase):
    def _run_from_package_directory(self, script):
        repository_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(script), repository_root],
            cwd=os.path.join(repository_root, "pm4py"),
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_import_statistics_from_package_directory(self):
        self._run_from_package_directory("""
            import sys
            original_path = sys.path.copy()
            import statistics
            from statistics import harmonic_mean, mean, median, stdev
            import pickle
            from pathlib import Path
            import sysconfig

            assert "pm4py" not in sys.modules
            assert sys.path == original_path
            assert Path(statistics.__file__).is_relative_to(sysconfig.get_path("stdlib"))
            assert not hasattr(statistics, "__path__")
            assert statistics is sys.modules["statistics"]
            assert mean([1, 2, 3]) == 2
            assert median([1, 2, 3, 4]) == 2.5
            assert stdev([1, 2, 3]) == 1
            assert harmonic_mean([1, 2]) == 4 / 3
            distribution = statistics.NormalDist(2, 3)
            assert pickle.loads(pickle.dumps(distribution)) == distribution
        """)

    def test_import_pm4py_from_package_directory(self):
        for imports in ("import pm4py\nimport statistics", "import statistics\nimport pm4py"):
            with self.subTest(imports=imports):
                script = "import sys\nsys.path.insert(0, sys.argv[1])\n" + imports + "\n"
                script += textwrap.dedent("""
                    import datetime
                    import importlib.util
                    from pathlib import Path

                    assert Path(pm4py.__file__).parent == Path.cwd()
                    assert Path(pm4py.statistics.__file__).parent == Path.cwd() / "statistics"
                    assert pm4py.statistics is not statistics
                    assert sys.modules["pm4py.statistics"] is pm4py.statistics
                    assert statistics.median([10, 20, 40]) == 20

                    if importlib.util.find_spec("polars"):
                        import polars as pl
                        from pm4py.statistics.traces.generic.polars import case_statistics

                        base = datetime.datetime(2024, 1, 1)
                        frame = pl.DataFrame({
                            "case:concept:name": ["a", "a", "b", "b", "c", "c", "d", "d"],
                            "time:timestamp": [
                                base + datetime.timedelta(seconds=value)
                                for value in (0, 10, 0, 20, 0, 40, 0, 80)
                            ],
                        }).lazy()
                        assert case_statistics.get_median_case_duration(frame) == 30
                        odd = frame.filter(pl.col("case:concept:name") != "d")
                        assert case_statistics.get_median_case_duration(odd) == 20
                        try:
                            case_statistics.get_median_case_duration(frame.limit(0))
                        except statistics.StatisticsError:
                            pass
                        else:
                            raise AssertionError("Empty durations must raise StatisticsError")
                """)
                self._run_from_package_directory(script)

    def test_importeverything(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        import pm4py
        log = pm4py.objects.log.importer.xes.importer.apply(
            os.path.join("input_data", "running-example.xes"))
        self.assertEqual(len(log), 6)


if __name__ == "__main__":
    unittest.main()
