

#!/usr/bin/env python3

"""
Provides the main CLI functionality for extracting configurable event logs out of a Mimic Database
"""
import argparse
import logging
from typing import List, Optional
import yaml
import argparse
import logging
from typing import List, Optional
import yaml
import sqlite3

from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.conversion.log import converter as log_converter  # type: ignore
from pm4py.objects.log.exporter.xes import exporter as xes_exporter  # type: ignore

from extractor.transfer import extract_transfer_events
from extractor.tables import extract_table_events
from extractor.poe import extract_poe_events
from extractor.extraction_helper import get_filename_string
from extractor.event_attributes import extract_event_attributes
from extractor.admission import extract_admission_events
from extractor.case_attributes import extract_case_attributes
from extractor.cli_helper import ask_event_attributes, create_db_connection,\
    parse_or_ask_case_attributes, parse_or_ask_case_notion, parse_or_ask_cohorts,\
    parse_or_ask_db_settings, parse_or_ask_event_type, parse_or_ask_low_level_tables
from extractor.cohort import extract_cohort, extract_cohort_for_ids
from extractor.constants import ADDITIONAL_ATTRIBUTES_QUESTION, ADMISSION_CASE_KEY,\
    ADMISSION_CASE_NOTION, ADMISSION_EVENT_TYPE, INCLUDE_MEDICATION_QUESTION, OTHER_EVENT_TYPE,\
    POE_EVENT_TYPE, SUBJECT_CASE_KEY, SUBJECT_CASE_NOTION, TRANSFER_EVENT_TYPE

formatter = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger('cli')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

parser = argparse.ArgumentParser(
    description='A CLI tool for extracting event logs out of MIMIC Databases.')

# TODO: sanity check argument inputs before using later on!

# Database Parameters
parser.add_argument('--db_host', type=str, default='https://d53a-2409-40e3-5e-9da5-d5c4-fe2f-dd03-9e5d.ngrok-free.app/', help='Database Host')

# Patient Cohort Parameters
parser.add_argument('--subject_ids', type=str, help='Subject IDs of cohort')
parser.add_argument('--hadm_ids', type=str,
                    help='Hospital Admission IDs of cohort')
parser.add_argument('--icd', type=str, help='ICD code(s) of cohort')
parser.add_argument('--icd_version', type=int, help='ICD version')
parser.add_argument('--icd_sequence_number', type=int,
                    help='Ranking threshold of diagnosis')
parser.add_argument('--drg', type=str, help='DRG code(s) of cohort')
parser.add_argument('--drg_type', type=str, help='DRG type (HCFA, APR)')
parser.add_argument('--age', type=str, help='Patient Age of cohort')

# Event Type Parameter
parser.add_argument('--type', type=str, help='Event Type')
parser.add_argument('--tables', type=str, help='Low level tables')
parser.add_argument('--tables_activities', type=str,
                    help='Activity Columns for Low level tables')
parser.add_argument('--tables_timestamps', type=str,
                    help='Timestamp Columns for Low level tables')

# Case Notion Parameter
parser.add_argument('--notion', type=str, help='Case Notion')

# Case Attribute Parameter
parser.add_argument('--case_attribute_list', type=str, help='Case Attributes')

# Config File Argument
parser.add_argument('--config', type=str,
                    help='Config file for providing all options via file')

# Argument to store intermediate dataframes to disk
parser.add_argument('--save_intermediate', action='store_true',
                    help="Store intermediate extraction results as csv. For debugging purposes.")
parser.add_argument('--ignore_intermediate',
                    dest='save_intermediate', action='store_false',
                    help="Explicitly disable storing of intermediate results.")
parser.set_defaults(save_intermediate=False)

# Argument to store event log as csv instead of xes
parser.add_argument('--csv_log', action='store_true',
                    help="Store resulting log as a .csv file instead of as an .xes event log")
parser.set_defaults(csv_log=False)


def main():
    """Main method for extracting event logs"""
    args = parser.parse_args()

    config: Optional[dict] = None
    if args.config is not None:
        with open(args.config, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

    # Should intermediate dataframes be saved?
    if config is not None and config.get("save_intermediate") is not None:
        save_intermediate: bool = config.get(
            'save_intermediate', False)  # type: ignore
    else:
        save_intermediate = args.save_intermediate

    # Should resulting event log be saved as csv instead of as xes?
    if config is not None and config.get("csv_log") is not None:
        save_csv_log: bool = config.get(
            'csv_log', False)  # type: ignore
    else:
        save_csv_log = args.csv_log

    # Create database connection
    # db_name, db_host, db_user, db_pw = parse_or_ask_db_settings(args, config)
    # db_name, db_host, db_user, db_pw = "mimic","localhost","root",""
    # db_connection = create_db_connection(db_name, db_host, db_user, db_pw)




    # Create a connection to the "mimiciv" SQLite database
    # db_name = "mimic_demo.db"
    # conn = sqlite3.connect(db_name)
    # db_cursor = conn.cursor()
    import pandas as pd
    import pymysql

# database connection
    db_connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="mimicdemo")
    db_cursor = db_connection.cursor()
# some other statements  with the help of cursor
#     connection.close()

    # db_cursor.execute("SELECT * FROM `admissions_1`")
    # adm = db_cursor.fetchall()
    # cols = list(map(lambda x: x[0], db_cursor.description))
    # d = pd.DataFrame(adm, columns=cols)
    # print(d.head)








    # Determine Cohort
    if args.subject_ids is None and args.hadm_ids is None:
        cohort_icd_codes, cohort_icd_version, cohort_icd_seq_num, cohort_drg_codes, \
            cohort_drg_type, cohort_age, \
            cohort_icd_codes_intersection, cohort_subject_ids, \
            cohort_hadm_ids = parse_or_ask_cohorts(args, config)
    # Determine case notion
    determined_case_notion = parse_or_ask_case_notion(args, config)

    # Determine case attributes
    case_attribute_list = parse_or_ask_case_attributes(args,
                                                       determined_case_notion, config)

    event_type = parse_or_ask_event_type(args, config)

    # build cohort
    if args.subject_ids is None and args.hadm_ids is None \
    and cohort_subject_ids is None and cohort_hadm_ids is None:
        cohort = extract_cohort(db_cursor, cohort_icd_codes, cohort_icd_version,
                                cohort_icd_seq_num, cohort_drg_codes, cohort_drg_type,
                                cohort_age, cohort_icd_codes_intersection, save_intermediate)
    else:
        if cohort_subject_ids is not None or cohort_hadm_ids is not None:
            if cohort_subject_ids is not None:
                subject_input = ",".join(cohort_subject_ids)
            else:
                subject_input = cohort_subject_ids # type: ignore
            if cohort_hadm_ids is not None:
                hadm_input = ",".join(cohort_hadm_ids)
            else:
                hadm_input = cohort_hadm_ids # type: ignore
            cohort = extract_cohort_for_ids(
            db_cursor, subject_input, hadm_input, save_intermediate)
        else:
            cohort = extract_cohort_for_ids(
                db_cursor, args.subject_ids, args.hadm_ids, save_intermediate)

    # extract case attributes
    if case_attribute_list is not None:
        case_attributes = extract_case_attributes(
            db_cursor, cohort, determined_case_notion, case_attribute_list, save_intermediate)

    if event_type == ADMISSION_EVENT_TYPE:
        events = extract_admission_events(db_cursor, cohort, save_intermediate)
    elif event_type == TRANSFER_EVENT_TYPE:
        events = extract_transfer_events(db_cursor, cohort, save_intermediate)
    elif event_type == POE_EVENT_TYPE:
        if config is not None and config.get("include_medications") is not None:
            should_include_medications: bool = config.get(
                'include_medications', False)
        else:
            include_medications = input(INCLUDE_MEDICATION_QUESTION).upper()
            should_include_medications = include_medications == "Y"

        events = extract_poe_events(
            db_cursor, cohort, should_include_medications, save_intermediate)
    elif event_type == OTHER_EVENT_TYPE:
        tables_to_extract = parse_or_ask_low_level_tables(args, config)
        if args.tables_activities is not None:
            tables_activities = args.tables_activities.split(',')
        elif config is not None and config.get("low_level_activities") is not None:
            tables_activities = config.get("low_level_activities")
        else:
            tables_activities = None
        if args.tables_timestamps is not None:
            tables_timestamps = args.tables_timestamps.split(',')
        elif config is not None and config.get("low_level_timestamps") is not None:
            tables_timestamps = config.get("low_level_timestamps")
        else:
            tables_timestamps = None
        events = extract_table_events(db_cursor, cohort, tables_to_extract,
                                      tables_activities, tables_timestamps, save_intermediate)

    if config is not None and config.get("additional_event_attributes") is not None:
        additional_attributes: List[dict] = config.get(
            "additional_event_attributes", [])
        for attribute in additional_attributes:
            events = extract_event_attributes(db_cursor, events, attribute['start_column'],
                                              attribute['end_column'], attribute['time_column'],
                                              attribute['table_to_aggregate'],
                                              attribute['column_to_aggregate'],
                                              attribute['aggregation_method'],
                                              attribute.get('filter_column'),
                                              attribute.get('filter_values'))
    else:
        event_attribute_decision = input(ADDITIONAL_ATTRIBUTES_QUESTION)
        while event_attribute_decision.upper() == "Y":
            start_column, end_column, time_column, table_to_aggregate, column_to_aggregate,\
                aggregation_method, filter_column, filter_values = ask_event_attributes(db_cursor,
                                                                                        events)
            events = extract_event_attributes(db_cursor, events, start_column, end_column,
                                              time_column, table_to_aggregate, column_to_aggregate,
                                              aggregation_method, filter_column, filter_values)
            event_attribute_decision = input(ADDITIONAL_ATTRIBUTES_QUESTION)

    if save_intermediate:
        csv_filename = get_filename_string(
            "event_attribute_enhanced_log", ".csv")
        events.to_csv("output/" + csv_filename)

    # set case id key based on determined case notion
    if determined_case_notion == SUBJECT_CASE_NOTION:
        case_id_key = SUBJECT_CASE_KEY
    elif determined_case_notion == ADMISSION_CASE_NOTION:
        case_id_key = ADMISSION_CASE_KEY

    # rename every case attribute to have case prefix
    if case_attribute_list is not None and case_attributes is not None:
        # join case attr to events
        if determined_case_notion == SUBJECT_CASE_NOTION:
            events = events.merge(
                case_attributes, on=SUBJECT_CASE_KEY, how='left')
        elif determined_case_notion == ADMISSION_CASE_NOTION:
            events = events.merge(
                case_attributes, on=ADMISSION_CASE_KEY, how='left')

        # rename case id key, as this will be affected too
        case_id_key = 'case:' + case_id_key
        for case_attr in case_attribute_list:
            events.rename(
                columns={case_attr: "case:" + case_attr}, inplace=True)

    if save_csv_log:
        filename = get_filename_string("event_log", ".csv")
        events.to_csv("output/" + filename)
    else:
        parameters = {log_converter.Variants.TO_EVENT_LOG.value
                      .Parameters.CASE_ID_KEY: case_id_key,
                      log_converter.Variants.TO_EVENT_LOG.value
                      .Parameters.CASE_ATTRIBUTE_PREFIX: 'case:'}
        event_log_object = log_converter.apply(
            events, parameters=parameters, variant=log_converter.Variants.TO_EVENT_LOG)
        filename = get_filename_string("event_log", ".xes")
        xes_exporter.apply(event_log_object, "output/" + filename)

if __name__ == '__main__':
    main()
