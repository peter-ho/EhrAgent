import pandas as pd
import jsonlines
import json
import re
import sqlite3
import mariadb
import sys
import os
import Levenshtein
def db_loader(target_ehr):
    ehr_csv_base_path = "S:\\Work\\mimic-iii-clinical-database-1.4"
    ehr_dict = {"admissions":os.path.join(ehr_csv_base_path,"ADMISSIONS.csv.gz"),
                "chartevents":os.path.join(ehr_csv_base_path,"CHARTEVENTS.csv.gz"),
                "cost":os.path.join(ehr_csv_base_path,"COST.csv.gz"),
                "d_icd_diagnoses":os.path.join(ehr_csv_base_path,"D_ICD_DIAGNOSES.csv.gz"),
                "d_icd_procedures":os.path.join(ehr_csv_base_path,"D_ICD_PROCEDURES.csv.gz"),
                "d_items":os.path.join(ehr_csv_base_path,"D_ITEMS.csv.gz"),
                "d_labitems":os.path.join(ehr_csv_base_path,"D_LABITEMS.csv.gz"),
                "diagnoses_icd":os.path.join(ehr_csv_base_path,"DIAGNOSES_ICD.csv.gz"),
                "icustays":os.path.join(ehr_csv_base_path,"ICUSTAYS.csv.gz"),
                "inputevents_cv":os.path.join(ehr_csv_base_path,"INPUTEVENTS_CV.csv.gz"),
                "labevents":os.path.join(ehr_csv_base_path,"LABEVENTS.csv.gz"),
                "microbiologyevents":os.path.join(ehr_csv_base_path,"MICROBIOLOGYEVENTS.csv.gz"),
                "outputevents":os.path.join(ehr_csv_base_path,"OUTPUTEVENTS.csv.gz"),
                "patients":os.path.join(ehr_csv_base_path,"PATIENTS.csv.gz"),
                "prescriptions":os.path.join(ehr_csv_base_path,"PRESCRIPTIONS.csv.gz"),
                "procedures_icd":os.path.join(ehr_csv_base_path,"PROCEDURES_ICD.csv.gz"),
                "transfers":os.path.join(ehr_csv_base_path,"TRANSFERS.csv.gz"),
                }
    data = pd.read_csv(ehr_dict[target_ehr])
    # data = data.astype(str)
    column_names = ', '.join(data.columns.tolist())
    return data
# def get_column_names(self, target_db):
#     return ', '.join(data.columns.tolist())

def data_filter(data, argument):
    # commands = re.sub(r' ', '', argument)
    backup_data = data
    # print('-->', argument)
    commands = argument.split('||')
    for i in range(len(commands)):
        try:
            # commands[i] = commands[i].replace(' ', '')
            if '>=' in commands[i]:
                command = commands[i].split('>=')
                column_name = command[0]
                value = command[1]
                try:
                    value = type(data[column_name][0])(value)
                except:
                    value = value
                data = data[data[column_name] >= value]
            elif '<=' in commands[i]:
                command = commands[i].split('<=')
                column_name = command[0]
                value = command[1]
                try:
                    value = type(data[column_name][0])(value)
                except:
                    value = value
                data = data[data[column_name] <= value]
            elif '>' in commands[i]:
                command = commands[i].split('>')
                column_name = command[0]
                value = command[1]
                try:
                    value = type(data[column_name][0])(value)
                except:
                    value = value
                data = data[data[column_name] > value]
            elif '<' in commands[i]:
                command = commands[i].split('<')
                column_name = command[0]
                value = command[1]
                if value[0] == "'" or value[0] == '"':
                    value = value[1:-1]
                try:
                    value = type(data[column_name][0])(value)
                except:
                    value = value
                data = data[data[column_name] < value]
            elif '=' in commands[i]:
                command = commands[i].split('=')
                column_name = command[0]
                value = command[1]
                # print(command)
                # print(value)
                if value[0] == "'" or value[0] == '"':
                    value = value[1:-1]
                try:
                    examplar = backup_data[column_name].tolist()[0]
                    value = type(examplar)(value)
                    # print(value, type(value), type(examplar))
                except:
                    value = value
                    # print('--', value, type(value), type(examplar))
                # print('------', len(data))
                data = data[data[column_name] == value]
                # print('======', len(data))
            elif ' in ' in commands[i]:
                command = commands[i].split(' in ')
                column_name = command[0]
                value = command[1]
                value_list = [s.strip() for s in value.strip("[]").split(',')]
                value_list = [s.strip("'").strip('"') for s in value_list]
                # print(command)
                # print(column_name)
                # print(value)
                # print(value_list)
                value_list = list(map(type(data[column_name][0]), value_list))
                # print(len(data))
                data = data[data[column_name].isin(value_list)]
                # print(len(data))
            elif 'max' in commands[i]:
                command = commands[i].split('max(')
                column_name = command[1].split(')')[0]
                data = data[data[column_name] == data[column_name].max()]
            elif 'min' in commands[i]:
                command = commands[i].split('min(')
                column_name = command[1].split(')')[0]
                data = data[data[column_name] == data[column_name].min()]
        except:
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
    return data

def get_value(data, argument):
    try:
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

def sql_interpreter(command):
    try:
        con = mariadb.connect(user='root', host='127.0.0.1', port=3306, database='mimiciiiv14')
        cur = con.cursor()
        cur.execute(command)
        return cur.fetchall()
    finally:
        con.close()

def date_calculator(argument):
    try:
        con = mariadb.connect(user='root', host='127.0.0.1', port=3306, database='mimiciiiv14')
        cur = con.cursor()
        command = "SELECT DATE_ADD(CURRENT_TIMESTAMP, INTERVAL {})".format(argument)
        cur.execute(command)
        return cur.fetchall()[0][0]
    except:
        raise Exception("The date calculator {} is incorrect. Please check the syntax and make necessary changes. For the current date and time, please call Calendar('0 year').".format(argument))

def sql_interpreter_sqlite(command):
    con = sqlite3.connect("<YOUR_DATASET_PATH>/ehrsql/mimic_iii/mimic_iii.db")
    cur = con.cursor()
    results = cur.execute(command).fetchall()
    return results

def date_calculator_sqlite(argument):
    try:
        con = sqlite3.connect("<YOUR_DATASET_PATH>/ehrsql/mimic_iii/mimic_iii.db")
        cur = con.cursor()
        command = "select datetime(current_time, '{}')".format(argument)
        results = cur.execute(command).fetchall()[0][0]
    except:
        raise Exception("The date calculator {} is incorrect. Please check the syntax and make necessary changes. For the current date and time, please call Calendar('0 year').".format(argument))
    return results

if __name__ == "__main__":
    db = table_toolkits()
    print(db.db_loader("microbiologyevents"))
    # print(db.data_filter("SPEC_TYPE_DESC=peripheral blood lymphocytes"))
    print(db.data_filter("HADM_ID=107655"))
    print(db.data_filter("SPEC_TYPE_DESC=peripheral blood lymphocytes"))
    print(db.get_value('CHARTTIME'))
    # results = db.sql_interpreter("select max(t1.c1) from ( select sum(cost.cost) as c1 from cost where cost.hadm_id in ( select diagnoses_icd.hadm_id from diagnoses_icd where diagnoses_icd.icd9_code = ( select d_icd_diagnoses.icd9_code from d_icd_diagnoses where d_icd_diagnoses.short_title = 'comp-oth vasc dev/graft' ) ) and datetime(cost.chargetime) >= datetime(current_time,'-1 year') group by cost.hadm_id ) as t1")
    # results = [result[0] for result in results]
    # if len(results) == 1:
    #     print(results[0])
    # else:
    #     print(results)
    # print(db.date_calculator('-1 year'))