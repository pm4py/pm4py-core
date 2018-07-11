import csv
import pm4py.log.instance as log_instance
from dateutil import parser as date_parser


class CSVImporter:

    def import_from_file(self, path, delimiter=',', check_data_types=True, apply_data_type_guessing=100):
        log = log_instance.EventLog({'origin': 'csv'})
        with open(path, 'r') as file:
            types = self.__derive_types(csv.reader(file, delimiter=delimiter),
                                        -1 if check_data_types is False else apply_data_type_guessing)
        with open(path, 'r') as file:
            type_parsers = {
                None: str,
                bool: bool,
                int: int,
                float: float,
                'date': date_parser.parse,
                str: str
            }
            reader = csv.reader(file, delimiter=delimiter)
            headers = next(reader)
            for row in reader:
                attr = {}
                for i, val in enumerate(row):
                    if check_data_types:
                        try:
                            attr[headers[i]] = type_parsers[types[i]](val)
                        except ValueError:
                            attr[headers[i]] = None
                    else:
                        attr[headers[i]] = val
                log.append(log_instance.Event(attr))
            return log

    def __derive_types(self, csv_reader, guess):
        headers = next(csv_reader)
        types = [None] * len(headers)
        supported_types = {
            None: self.__check_bool,
            bool: self.__check_bool,
            int: self.__check_int,
            float: self.__check_float,
            'date': self.__check_date,
            str: self.__check_str
        }
        j = 0
        for row in csv_reader:
            if not guess is None:
                if j > guess:
                    return types
            if set(types) == {str}:
                return types
            for i, val in enumerate(row):
                types[i] = supported_types[types[i]](val)
            j += 1
        return types

    def __check_bool(self, val):
        return bool if val == '1' or val == '0' or val.strip().lower() == 'true' or val.strip().lower == 'false' else self.__check_int(
            val)

    def __check_int(self, val):
        try:
            int(val)
            return int
        except ValueError:
            return self.__check_float(val)

    def __check_float(self, val):
        try:
            float(val)
            return float
        except ValueError:
            return self.__check_date(val)

    def __check_date(self, val):
        try:
            date_parser.parse(val)
            return 'date'
        except ValueError:
            return str

    def __check_str(self, val):
        pass
