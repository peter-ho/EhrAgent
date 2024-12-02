import pandas as pd
import jsonlines
import json
import re
import sqlite3
import mariadb
import sys
import os
import Levenshtein
from datetime import datetime

import sqlite3

class Dataset:
    def __init__(self, table_name):
        self.table_name = table_name
        self.filters = []
        self.columns = '*'
        self.order_by_limit = ''
        
    def filter(self, condition):
        self.filters.append(condition)
        return self
    
    def orderByLimit(self, condition):
        self.order_by_limit = condition
        return self

    def get(self, columns):
        self.columns = columns
        res = self._execute_query()
        return res
    
    def get_count(self):
        self.columns = 'count(*)'
        res = self._execute_query()
        return res[0][0]

    def _execute_query(self):
        query = f"SELECT {self.columns} FROM {self.table_name}"
        if self.filters:
            query += " WHERE " + " AND ".join(self.filters)
        if len(self.order_by_limit) > 0:
            query += f" ORDER BY {self.order_by_limit} "
        
        print(f"Executing SQL: {query}")  # For debugging purposes

        try:
            con = mariadb.connect(user='root', host='127.0.0.1', port=3306, database='mimiciiiv14')
            cur = con.cursor()
            cur.execute(query)
            return cur.fetchall()
        finally:
            cur.close() 
            con.close()

# Example Usage:
# dataset = Dataset('your_table')
# result = dataset.filter("column1 = 'value1'").filter("column2 > 10").get(['column1', 'column2', 'column3'])
# print(result)


def db_loader(target_ehr):
    return Dataset(target_ehr)
# def get_column_names(self, target_db):
#     return ', '.join(data.columns.tolist())

def data_filter(data: Dataset, argument):
    commands = argument.split('||')
    for command in commands:
        # commands = re.sub(r' ', '', argument)
        data.filter(command)
    return data

def order_by(data: Dataset, argument):
    return data.orderByLimit(argument)

def get_first_value(data: Dataset, argument):
    res = data.get(argument)
    if len(res) > 0:
        res = res[0]
        if isinstance(res, tuple) and len(res) > 0:
            return res[0]
    return None

def get_values(data: Dataset, argument):
    res = data.get(argument)
    if len(res) > 0 and len(res[0]) == 1:
        res = [x[0] for x in res]
    return res

def get_count(data: Dataset):
    return data.get_count()

    """
            if column_name not in data.columns.tolist():
                columns = ', '.join(data.columns.tolist())
                raise Exception("The filtering query {} is incorrect. Please modify the column name or use LoadDB to read another table. The column names in the current DB are {}.".format(commands[i], columns))
            if column_name == '' or value == '':
                raise Exception("The filtering query {} is incorrect. There is syntax error in the command. Please modify the condition or use LoadDB to read another table.".format(commands[i]))
        if len(data) == 0:
            # get 5 examples from the backup data what is in the same column
            column_values = list(set(backup_data[column_name].tolist()))
            if ('=' in commands[i]) and (not value in column_values) and (not '>=' in commands[i]) and (not '<=' in commands[i]):
                levenshtein_dist = {}
                for cv in column_values:
                    levenshtein_dist[cv] = Levenshtein.distance(str(cv), str(value))
                levenshtein_dist = sorted(levenshtein_dist.items(), key=lambda x: x[1], reverse=False)
                column_values = [i[0] for i in levenshtein_dist[:5]]
                column_values = ', '.join([str(i) for i in column_values])
                raise Exception("The filtering query {} is incorrect. There is no {} value in the column. Five example values in the column are {}. Please check if you get the correct {} value.".format(commands[i], value, column_values, column_name))
            else:
                return data


        commands = argument.split(', ')
        if len(commands) == 1:
            column = argument
            while column[0] == '[' or column[0] == "'":
                column = column[1:]
            while column[-1] == ']' or column[-1] == "'":
                column = column[:-1]
            if len(data) == 1:
                return str(data.iloc[0][column])
            else:
                answer_list = list(set(data[column].tolist()))
                answer_list = [str(i) for i in answer_list]
                return ', '.join(answer_list)
                # else:
                #     return "Get the value. But there are too many returned values. Please double-check the code and make necessary changes."
        else:
            column = commands[0]
            if 'mean' in commands[-1]:
                res_list = data[column].tolist()
                res_list = [float(i) for i in res_list]
                return sum(res_list)/len(res_list)
            elif 'max' in commands[-1]:
                res_list = data[column].tolist()
                try:
                    res_list = [float(i) for i in res_list]
                except:
                    res_list = [str(i) for i in res_list]
                return max(res_list)
            elif 'min' in commands[-1]:
                res_list = data[column].tolist()
                try:
                    res_list = [float(i) for i in res_list]
                except:
                    res_list = [str(i) for i in res_list]
                return min(res_list)
            elif 'sum' in commands[-1]:
                res_list = data[column].tolist()
                res_list = [float(i) for i in res_list]
                return sum(res_list)
            elif 'list' in commands[-1]:
                res_list = data[column].tolist()
                res_list = [str(i) for i in res_list]
                return list(res_list)
            else:
                raise Exception("The operation {} contains syntax errors. Please check the arguments.".format(commands[-1]))
    except:
        column_values = ', '.join(data.columns.tolist())
        raise Exception("The column name {} is incorrect. Please check the column name and make necessary changes. The columns in this table include {}.".format(column, column_values))
        """

def sql_interpreter_mariadb(command):
    try:
        con = mariadb.connect(user='root', host='127.0.0.1', port=3306, database='mimiciiiv14')
        cur = con.cursor()
        cur.execute(command)
        return cur.fetchall()
    finally:
        con.close()

def date_calculator_mariadb(argument):
    try:
        con = mariadb.connect(user='root', host='127.0.0.1', port=3306, database='mimiciiiv14')
        cur = con.cursor()
        command = "SELECT DATE_ADD(CURRENT_TIMESTAMP, INTERVAL {})".format(argument)
        cur.execute(command)
        return cur.fetchall()[0][0]
    except:
        raise Exception("The date calculator {} is incorrect. Please check the syntax and make necessary changes. For the current date and time, please call Calendar('0 year').".format(argument))

sql_interpreter = sql_interpreter_mariadb
date_calculator = date_calculator_mariadb

if __name__ == "__main__":
    #db = table_toolkits()
    print(date_calculator('-1 year'))
    db = db_loader("microbiologyevents")
    # print(db.data_filter("SPEC_TYPE_DESC=peripheral blood lymphocytes"))
    print(data_filter(db, "HADM_ID=107655"))
    print(data_filter(db, "SPEC_TYPE_DESC='peripheral blood lymphocytes'"))
    print(get_first_value(db, 'CHARTTIME'))

    LoadDB = db_loader
    FilterDB = data_filter
    GetFirstValue = get_first_value
    GetValues = get_values
    GetCount = get_count
    OrderLimit = order_by
    SQLInterpreter = sql_interpreter
    Calendar = date_calculator

    diag_icd_db = LoadDB('diagnoses_icd')
    filtered_diag_icd_db = FilterDB(diag_icd_db, "ICD9_CODE='0389'")
    subject_ids = GetValues(filtered_diag_icd_db, 'SUBJECT_ID')
    for subject_id in subject_ids:
        print(subject_id)

    admission_db = LoadDB('admissions')
    # filter admission database by the patient id or SUBJECT_ID column 2238
    filtered_admission_db = FilterDB(admission_db, 'SUBJECT_ID=2238')
    # order the admissions db by discharge time descending and only selecting the first row, since we are only interested in their last hospital visit
    filtered_ordered_admission_db = OrderLimit(filtered_admission_db, 'DISCHTIME DESC LIMIT 1')
    # Get the admission id of the patient's last hospital visit
    hadm_id = GetFirstValue(filtered_ordered_admission_db, 'HADM_ID')
    # As tpn w/lipids is an item, we can find the corresponding information in the d_items database.
    d_items_db = LoadDB('d_items')
    filtered_d_items_db = FilterDB(d_items_db, "LABEL='tpn w/lipids'")
    item_id = GetFirstValue(filtered_d_items_db, 'ITEMID')
    # We will check the inputevents_cv database to see if there is any record of tpn w/lipids given to patient 2238 in their last hospital visit. 
    inputevents_cv_db = LoadDB('inputevents_cv')
    filtered_inputevents_cv_db = FilterDB(inputevents_cv_db, "HADM_ID='{}' AND ITEMID='{}'".format(hadm_id, item_id))
    if GetCount(filtered_inputevents_cv_db) > 0:
        answer = 1
    else:
        answer = 0


    ## Question: calculate the length of stay of the first stay of patient 27392 in the icu.
    icustays_db = LoadDB('icustays')
    filtered_icustays_db = FilterDB(icustays_db, "SUBJECT_ID='{}'".format(27392))
    ascending_filtered_icustays_db = OrderLimit(filtered_icustays_db, 'INTIME')
    hadm_id = GetFirstValue(ascending_filtered_icustays_db, 'HADM_ID')

    icustays_db = LoadDB('icustays')
    filtered_icustays_db = FilterDB(icustays_db, "HADM_ID='{}'".format(hadm_id))
    intime = GetFirstValue(filtered_icustays_db, 'INTIME')
    outtime = GetFirstValue(filtered_icustays_db, 'OUTTIME')
    if type(intime) == str:
        intime = datetime.strptime(intime, '%Y-%m-%d %H:%M:%S')
    if type(outtime) == str:
        outtime = datetime.strptime(outtime, '%Y-%m-%d %H:%M:%S')
    length_of_stay = outtime - intime
    if length_of_stay.seconds // 3600 > 12:
        answer = length_of_stay.days + 1
    else:
        answer = length_of_stay.days
    print(answer)


    # results = db.sql_interpreter("select max(t1.c1) from ( select sum(cost.cost) as c1 from cost where cost.hadm_id in ( select diagnoses_icd.hadm_id from diagnoses_icd where diagnoses_icd.icd9_code = ( select d_icd_diagnoses.icd9_code from d_icd_diagnoses where d_icd_diagnoses.short_title = 'comp-oth vasc dev/graft' ) ) and datetime(cost.chargetime) >= datetime(current_time,'-1 year') group by#.hadm_id ) as t1")
    # results = [result[0] for result in results]
    # if len(results) == 1:
    #     print(results[0])
    # else:
    #     print(results)
