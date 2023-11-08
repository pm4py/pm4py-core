'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
import importlib.util


def apply(input_path, validation_path, parameters=None):
    if not importlib.util.find_spec("lxml"):
        raise Exception("please install lxml in order to validate an XMLOCEL file.")

    import lxml.etree

    if parameters is None:
        parameters = {}

    xml_file = lxml.etree.parse(input_path)
    xml_validator = lxml.etree.XMLSchema(file=validation_path)
    is_valid = xml_validator.validate(xml_file)
    return is_valid
