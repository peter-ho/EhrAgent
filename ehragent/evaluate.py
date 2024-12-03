import os
import json

def judge(id, pred, ans):
    pred0, ans0 = pred, ans
    old_flag = True
    if not ans in pred:
        old_flag = False
    if "True" in pred:
        pred = pred.replace("True", "1")
    else:
        pred = pred.replace("False", "0")
    if ans == "False" or ans == "false":
        ans = "0"
    if ans == "True" or ans == "true":
        ans = "1"
    if ans == "No" or ans == "no":
        ans = "0"
    if ans == "Yes" or ans == "yes":
        ans = "1"
    if ans == "None" or ans == "none":
        ans = "0"
    if ", " in ans:
        ans = ans.split(', ')
    if ans[-2:] == ".0":
        ans = ans[:-2]
    if not type(ans) == list:
        ans = [ans]
    new_flag = True
    for i in range(len(ans)):
        if not ans[i] in pred:
            new_flag = False
            break
    result = (old_flag or new_flag)
    if not result:
        print(f'JUDGING {id}, {ans0}')
    return result
    #return (old_flag or new_flag)

logs_path = "C:\\src\\EhrAgent\\logs\\gpt-4-0613.gpt-4-0613\\4_baseline\\"
#logs_path = "C:\\src\\EhrAgent\\logs_maria\\gpt-4-0613.gpt-4-0613\\4\\"
files = os.listdir(logs_path)

# read the files 
answer_book = "C:\\src\\EhrAgent\\data\\valid_preprocessed_exclude_cost.json"
with open(answer_book, 'r') as f:
    contents = json.load(f)
answers = {}
for i in range(len(contents)):
    answers[contents[i]['id']] = contents[i]['answer']

stats = {"total_num": 0, "correct": 0, "unfinished": 0, "incorrect": 0}

for file in files:
    id = file.split('.')[0]
    if not id in answers.keys():
        continue
    with open(logs_path+file, 'r') as f:
        logs = f.read()
    split_logs = logs.split('\n----------------------------------------------------------\n')
    question = split_logs[0]
    answer = answers[id]
    if type(answer) == list:
        answer = ', '.join(answer)
    stats["total_num"] += 1
    if not "TERMINATE" in logs:
        stats["unfinished"] += 1
    else:
        if '"cell": "' in logs:
            last_code_start = logs.rfind('"cell": "')
            last_code_end = logs.rfind('"\n}')
            last_code = logs[last_code_start+9:last_code_end]
        else:
            last_code_end = logs.rfind('Solution:')
        prediction_end = logs.rfind('TERMINATE')
        prediction = logs[last_code_end:prediction_end]
        logs = logs.split('TERMINATE')[0]
        result = judge(id, prediction, answer)
        if result:
            stats["correct"] += 1
        else:
            stats["incorrect"] += 1

print(stats)
