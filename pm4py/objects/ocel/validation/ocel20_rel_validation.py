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

from typing import Tuple, Collection


def const_1_existence_type_independent_tables(curs):
    query = """SELECT Count(*) FROM sqlite_master WHERE type = "table" AND tbl_name IN ("event_map_type", "object_map_type", "event", "object", "event_object", "object_object");"""
    curs.execute(query)
    res = curs.fetchone()
    return res[0] == 6


def const_2_existence_object_type_tables_map_obj_types(curs):
    query = """SELECT Count(*) FROM (SELECT a.ocel_type_map, b.tbl_name FROM (SELECT ocel_type_map FROM object_map_type) a LEFT OUTER JOIN (SELECT tbl_name FROM sqlite_master WHERE type = "table" AND tbl_name LIKE "object_%") b ON b.tbl_name = "object_" || a.ocel_type_map WHERE b.tbl_name IS NULL);"""
    curs.execute(query)
    res0 = curs.fetchone()

    query = """SELECT Count(*) FROM (SELECT a.ocel_type_map, b.tbl_name FROM (SELECT tbl_name FROM sqlite_master WHERE type = "table" AND tbl_name LIKE "object_%") b LEFT OUTER JOIN (SELECT ocel_type_map FROM object_map_type) a ON b.tbl_name = "object_" || a.ocel_type_map WHERE a.ocel_type_map IS NULL);"""
    curs.execute(query)
    res1 = curs.fetchone()

    return res0[0] == 0 and res1[0] == 2


def const_3_existence_event_type_tables_map_ev_types(curs):
    query = """SELECT Count(*) FROM (SELECT a.ocel_type_map, b.tbl_name FROM (SELECT ocel_type_map FROM event_map_type) a LEFT OUTER JOIN (SELECT tbl_name FROM sqlite_master WHERE type = "table" AND tbl_name LIKE "event_%") b ON b.tbl_name = "event_" || a.ocel_type_map WHERE b.tbl_name IS NULL);"""
    curs.execute(query)
    res0 = curs.fetchone()

    query = """SELECT Count(*) FROM (SELECT a.ocel_type_map, b.tbl_name FROM (SELECT tbl_name FROM sqlite_master WHERE type = "table" AND tbl_name LIKE "event_%") b LEFT OUTER JOIN (SELECT ocel_type_map FROM event_map_type) a ON b.tbl_name = "event_" || a.ocel_type_map WHERE a.ocel_type_map IS NULL);"""
    curs.execute(query)
    res1 = curs.fetchone()

    return res0[0] == 0 and res1[0] == 2


def const_4_ocel_type_column(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.tbl_name IN ("object_map_type", "event_map_type", "event", "object") AND m.type = "table" AND p.name = "ocel_type");"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 4


def const_5_ocel_type_map(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.tbl_name IN ("object_map_type", "event_map_type") AND m.type = "table" AND p.name = "ocel_type_map");"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 2


def const_6_ocel_id(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.tbl_name IN ("event", "object") AND m.type = "table" AND p.name = "ocel_id");"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 2


def const_7_ocel_qualifier(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.tbl_name IN ("event_object", "object_object") AND m.type = "table" AND p.name = "ocel_qualifier");"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 2


def const_8_event_object_fields(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.tbl_name = "event_object" AND m.type = "table" AND p.name IN ("ocel_event_id", "ocel_object_id"));"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 2


def const_9_object_object_fields(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.tbl_name = "object_object" AND m.type = "table" AND p.name IN ("ocel_source_id", "ocel_target_id"));"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 2


def const_10_existence_ocel_id_obj_type_spec_tables(curs):
    query = """SELECT m.tbl_name, Count(*) FROM sqlite_master m JOIN object_map_type ty on m.tbl_name = "object_" || ty.ocel_type_map JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND p.name = "ocel_id" GROUP BY m.tbl_name;"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[1] != 1:
            ret = False
            break

    return ret


def const_11_existence_ocel_id_ev_type_spec_tables(curs):
    query = """SELECT m.tbl_name, Count(*) FROM sqlite_master m JOIN event_map_type ty on m.tbl_name = "event_" || ty.ocel_type_map JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND p.name = "ocel_id" GROUP BY m.tbl_name;"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[1] != 1:
            ret = False
            break

    return ret


def const_12_existence_type_ocel_time_obj_type_spec_tables(curs):
    query = """SELECT m.tbl_name, Count(*) FROM sqlite_master m JOIN object_map_type ty on m.tbl_name = "object_" || ty.ocel_type_map JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND p.name = "ocel_time" AND p.type = "TIMESTAMP" GROUP BY m.tbl_name;"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[1] != 1:
            ret = False
            break

    return ret


def const_13_existence_type_ocel_time_ev_type_spec_tables(curs):
    query = """SELECT m.tbl_name, Count(*) FROM sqlite_master m JOIN event_map_type ty on m.tbl_name = "event_" || ty.ocel_type_map JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND p.name = "ocel_time" AND p.type = "TIMESTAMP" GROUP BY m.tbl_name;"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[1] != 1:
            ret = False
            break

    return ret


def const_14_primary_key_object_event_map_type_tables(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND m.tbl_name IN ("object_map_type", "event_map_type") AND p.name = "ocel_type" AND p.pk > 0);"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[0] != 2:
            ret = False
            break

    return ret


def const_15_primary_key_object_event_tables(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND m.tbl_name IN ("object", "event") AND p.name = "ocel_id" AND p.pk > 0);"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[0] != 2:
            ret = False
            break

    return ret


def const_16_primary_key_event_object_table(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND m.tbl_name = "event_object" AND p.name IN ("ocel_event_id", "ocel_object_id", "ocel_qualifier") AND p.pk > 0);"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[0] != 3:
            ret = False
            break

    return ret


def const_17_primary_key_object_object_table(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM sqlite_master m JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND m.tbl_name = "object_object" AND p.name IN ("ocel_source_id", "ocel_target_id", "ocel_qualifier") AND p.pk > 0);"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[0] != 3:
            ret = False
            break

    return ret


def const_18_primary_key_event_type_spec_tables(curs):
    query = """SELECT m.tbl_name, sum(p.pk) FROM sqlite_master m JOIN event_map_type ty on m.tbl_name = "event_" || ty.ocel_type_map JOIN pragma_table_info(m.tbl_name) p WHERE m.type = "table" AND p.name = "ocel_id" GROUP BY m.tbl_name;"""
    curs.execute(query)
    res = curs.fetchall()

    ret = True
    for el in res:
        if el[1] != 1:
            ret = False
            break

    return ret


def const_19_foreign_key_event(curs):
    query = """SELECT Count(*) FROM (SELECT * from pragma_foreign_key_list("event") p WHERE p."table" = "event_map_type" AND p."from" = "ocel_type" AND p."to" = "ocel_type");"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 1


def const_20_foreign_key_object(curs):
    query = """SELECT Count(*) FROM (SELECT * from pragma_foreign_key_list("object") p WHERE p."table" = "object_map_type" AND p."from" = "ocel_type" AND p."to" = "ocel_type");"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 1


def const_21_foreign_key_event_object(curs):
    query = """SELECT Count(*) FROM (SELECT * from pragma_foreign_key_list("event_object") p WHERE p."table" = "event" AND p."from" = "ocel_event_id" AND p."to" = "ocel_id");"""
    curs.execute(query)
    res0 = curs.fetchone()

    query = """SELECT Count(*) FROM (SELECT * from pragma_foreign_key_list("event_object") p WHERE p."table" = "object" AND p."from" = "ocel_object_id" AND p."to" = "ocel_id");"""
    curs.execute(query)
    res1 = curs.fetchone()

    return res0[0] == 1 and res1[0] == 1


def const_22_foreign_key_object_object(curs):
    query = """SELECT Count(*) FROM (SELECT * from pragma_foreign_key_list("object_object") p WHERE p."table" = "object" AND p."from" = "ocel_source_id" AND p."to" = "ocel_id");"""
    curs.execute(query)
    res0 = curs.fetchone()

    query = """SELECT Count(*) FROM (SELECT * from pragma_foreign_key_list("object_object") p WHERE p."table" = "object" AND p."from" = "ocel_target_id" AND p."to" = "ocel_id");"""
    curs.execute(query)
    res1 = curs.fetchone()

    return res0[0] == 1 and res1[0] == 1


def const_23_foreign_key_event_type_specific(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM (SELECT tbl_name FROM sqlite_master WHERE type = "table") m JOIN event_map_type ty on m.tbl_name = "event_" || ty.ocel_type_map LEFT OUTER JOIN pragma_foreign_key_list(m.tbl_name) p ON p."table" = "event" AND p."from" = "ocel_id" AND p."to" = "ocel_id" WHERE p."table" IS NULL)"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 0


def const_24_foreign_key_object_type_specific(curs):
    query = """SELECT Count(*) FROM (SELECT m.tbl_name, p.* FROM (SELECT tbl_name FROM sqlite_master WHERE type = "table") m JOIN object_map_type ty on m.tbl_name = "object_" || ty.ocel_type_map LEFT OUTER JOIN pragma_foreign_key_list(m.tbl_name) p ON p."table" = "object" AND p."from" = "ocel_id" AND p."to" = "ocel_id" WHERE p."table" IS NULL)"""
    curs.execute(query)
    res0 = curs.fetchone()

    return res0[0] == 0


constraints = {
    "const_1_existence_type_independent_tables": const_1_existence_type_independent_tables,
    "const_2_existence_object_type_tables_map_obj_types": const_2_existence_object_type_tables_map_obj_types,
    "const_3_existence_event_type_tables_map_ev_types": const_3_existence_event_type_tables_map_ev_types,
    "const_4_ocel_type_column": const_4_ocel_type_column,
    "const_5_ocel_type_map": const_5_ocel_type_map,
    "const_6_ocel_id": const_6_ocel_id,
    "const_7_ocel_qualifier": const_7_ocel_qualifier,
    "const_8_event_object_fields": const_8_event_object_fields,
    "const_9_object_object_fields": const_9_object_object_fields,
    "const_10_existence_ocel_id_obj_type_spec_tables": const_10_existence_ocel_id_obj_type_spec_tables,
    "const_11_existence_ocel_id_ev_type_spec_tables": const_11_existence_ocel_id_ev_type_spec_tables,
    "const_12_existence_type_ocel_time_obj_type_spec_tables": const_12_existence_type_ocel_time_obj_type_spec_tables,
    "const_13_existence_type_ocel_time_ev_type_spec_tables": const_13_existence_type_ocel_time_ev_type_spec_tables,
    "const_14_primary_key_object_event_map_type_tables": const_14_primary_key_object_event_map_type_tables,
    "const_15_primary_key_object_event_tables": const_15_primary_key_object_event_tables,
    "const_16_primary_key_event_object_table": const_16_primary_key_event_object_table,
    "const_17_primary_key_object_object_table": const_17_primary_key_object_object_table,
    "const_18_primary_key_event_type_spec_tables": const_18_primary_key_event_type_spec_tables,
    "const_19_foreign_key_event": const_19_foreign_key_event,
    "const_20_foreign_key_object": const_20_foreign_key_object,
    "const_21_foreign_key_event_object": const_21_foreign_key_event_object,
    "const_22_foreign_key_object_object": const_22_foreign_key_object_object,
    "const_23_foreign_key_event_type_specific": const_23_foreign_key_event_type_specific,
    "const_24_foreign_key_object_type_specific": const_24_foreign_key_object_type_specific,
}


def apply(file_path: str) -> Tuple[Collection[str], Collection[str]]:
    """
    Validates the relational schema of an OCEL 2.0 SQLite database

    Parameters
    ----------------
    file_path
        Path to the OCEL 2.0 SQLite database

    Returns
    ----------------
    satisfied
        List of satisfied constraints
    unsatisfied
        List of unsatisfied constraints
    """
    import sqlite3

    conn = sqlite3.connect(file_path)
    curs = conn.cursor()

    satisfied = []
    unsatisfied = []

    for c in constraints:
        res = constraints[c](curs)
        if res:
            satisfied.append(c)
        else:
            unsatisfied.append(c)

    curs.close()
    conn.close()

    return satisfied, unsatisfied
