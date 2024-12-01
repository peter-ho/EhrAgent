import os
import json
import random
import numpy as np
import argparse
import autogen
from toolset_high import *
from medagent import MedAgent
from pathlib import Path
from config import openai_config, llm_config_list
import time
import re

def judge(pred, ans):
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
    print(f'JUDGING {pred0} vs {ans0} == {result}')
    return result

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm_azure", type=str, default="<YOUR_LLM_NAME>")
    parser.add_argument("--llm_autogen", type=str, default="<YOUR_LLM_NAME>")
    parser.add_argument("--num_questions", type=int, default=1)
    parser.add_argument("--dataset", type=str, default="mimic_iii")
    parser.add_argument("--data_path", type=str, default="<YOUR_DATASET_PATH>")
    parser.add_argument("--logs_path", type=str, default="<YOUR_LOGS_PATH>")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reverse_sequence", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--debug_id", type=str, default="")
    parser.add_argument("--start_id", type=int, default=0)
    parser.add_argument("--num_shots", type=int, default=4)
    args = parser.parse_args()
    set_seed(args.seed)
    if args.dataset == 'mimic_iii':
        from prompts_mimic import EHRAgent_4Shots_Knowledge
    else:
        from prompts_eicu import EHRAgent_4Shots_Knowledge

    config_autogen = [openai_config(args.llm_autogen)]
    config_azure = [openai_config(args.llm_azure)]
    llm_config = llm_config_list(args.seed, config_autogen)

    #    name="gpt-35-turbo",
    chatbot = autogen.agentchat.AssistantAgent(
        name=args.llm_autogen,
        system_message="For coding tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done. Save the answers to the questions in the variable 'answer'. Please only generate the code.",
        llm_config=llm_config,
    )
    #response = chatbot.send(message="this is a test, why am i getting 404 when doing receive on this chatbot?", recipient=chatbot, 
    #                        silent=False, request_reply=True)
    #print(response)

    user_proxy = MedAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "coding", "use_docker": False},
        config_list=config_azure,
    )

    # register the functions
    user_proxy.register_function(
        function_map={
            "python": run_code,
        }
    )
    #        "Calculate": run_code,
    #        "LoadDB": run_code,
    #        "FilterDB": run_code,
    #        "GetValue": run_code,
    #        "SQLInterpreter": run_code,
    #        "Calendar": run_code
    #    }
    #)

    user_proxy.register_dataset(args.dataset)

    file_path = args.data_path
    # read from json file
    with open(file_path, 'r') as f:
        contents = json.load(f)

    # random shuffle
    import random
    random.shuffle(contents)
    #file_path = "{}/{}/".format(args.logs_path, args.num_shots) + "{id}.txt"
    log_dir = os.path.join(args.logs_path, f"{args.llm_azure}.{args.llm_autogen}", str(args.num_shots))
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(log_dir, "{id}.txt")

    start_time = time.time()
    if args.num_questions == -1:
        args.num_questions = len(contents)
    long_term_memory = []
    init_memory = EHRAgent_4Shots_Knowledge
    init_memory = init_memory.split('\n\n')
    for i in range(len(init_memory)):
        item = init_memory[i]
        item = item.split('Question:')[-1]
        question = item.split('\nKnowledge:\n')[0]
        item = item.split('\nKnowledge:\n')[-1]
        knowledge = item.split('\nSolution:')[0]
        code = item.split('\nSolution:')[-1]
        new_item = {"question": question, "knowledge": knowledge, "code": code}
        long_term_memory.append(new_item)
    if args.reverse_sequence:
        start_sequence = args.num_questions - 1
        end_sequence = args.start_id
        increment = -1
    else:
        start_sequence = args.start_id
        end_sequence = args.num_questions
        increment = 1

    cnt_completion, cnt_judge, cnt_total = 0, 0, 0
    for i in range(start_sequence, end_sequence, increment):
        if not args.debug_id is None and len(args.debug_id) > 0 and contents[i]['id'] != args.debug_id:
            continue
        if contents[i]['id'] in ['5f9ee75b40aa7b05578e576c', 'bf1fb18f8c33093f41af877d', 
                                 '1f739d651d3e475012d6dd7c', 'c05df0b81e03432ce9a0d68f',
                                 'd733bf0081e4f4424205bf51', '9b548026218e4baffd6d0c4c',
                                 '2cb4e7220cc9a842fd4a686d']:
            print(f"===== skipping {contents[i]['id']} due to past issues.")
            continue
        file_directory = file_path.format(id=contents[i]['id'])
        if os.path.isfile(file_directory):
            print(f"===== {file_directory} was processed last time, skipping.")
            continue
        question = contents[i]['template']
        answer = contents[i]['answer']
        print(f"===== Execution begins for id - {contents[i]['id']}")
        try:
            user_proxy.update_memory(args.num_shots, long_term_memory)
            user_proxy.initiate_chat(
                chatbot,
                message=question,
            )
            logs = user_proxy._oai_messages

            logs_string = []
            logs_string.append(str(question))
            logs_string.append(str(answer))
            for agent in list(logs.keys()):
                for j in range(len(logs[agent])):
                    if logs[agent][j]['content'] != None:
                        logs_string.append(logs[agent][j]['content'])
                    else:
                        argums = logs[agent][j]['function_call']['arguments']
                        if type(argums) == dict and 'cell' in argums.keys():
                            logs_string.append(argums['cell'])
                        else:
                            logs_string.append(argums)
        except Exception as e:
            logs_string = [str(e)]
        if args.debug:
            print(logs_string)
        # f = open(file_directory, 'w')
        if type(answer) == list:
            answer = ', '.join(answer)
        logs_string.append("Ground-Truth Answer ---> "+answer)
        with open(file_directory, 'w') as f:
            f.write('\n----------------------------------------------------------\n'.join(logs_string))
        logs_string = '\n----------------------------------------------------------\n'.join(logs_string)
        if '"cell": "' in logs_string:
            last_code_start = logs_string.rfind('"cell": "')
            last_code_end = logs_string.rfind('"\n}')
            last_code = logs_string[last_code_start+9:last_code_end]
        else:
            last_code_end = logs_string.rfind('Solution:')
        prediction_end = logs_string.rfind('TERMINATE')
        match = re.search(r'\n-+\n(.*?)\n-+\nTERMINATE\n', logs_string)
        prediction = match.group(1) if match else None
        if prediction is None:
            prediction = ''
        else:
            cnt_completion += 1
        result = judge(prediction, answer)
        if result:
            new_item = {"question": question, "knowledge": user_proxy.knowledge, "code": user_proxy.code}
            long_term_memory.append(new_item)
            cnt_judge += 1
        cnt_total += 1
    end_time = time.time()
    print("Time elapsed: ", end_time - start_time)
    print(f"SR: {cnt_judge/cnt_total*100.0 if cnt_judge > 0 else 0}\t CR: {cnt_completion/cnt_total*100.0 if cnt_total > 0 else 0}")
    print(f'total number of questions: {args.num_questions}')

if __name__ == "__main__":
    main()