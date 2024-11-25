<div align="center">
<h1> ⚕️EHRAgent🤖 </h1>
</div>

This a reproduction of the code of the paper ["EHRAgent: Code Empowers Large Language Models for Complex Tabular Reasoning on Electronic Health Records"](https://arxiv.org/abs/2401.07128). EHRAgent is an LLM agent empowered with a code interface, to autonomously generate and execute code for complex clinical tasks within electronic health records (EHRs). The original project page is available at [this link](https://wshi83.github.io/EHR-Agent-page/).

### Features

- EHRAgent is an LLM agent augmented with tools and medical knowledge, to solve complex tabular reasoning derived from EHRs;
- Planning with a code interface, EHRAgent enables the LLM agent to formulate a clinical problem-solving process as an executable code plan of action sequences, along with a code executor;
- We introduce interactive coding between the LLM agent and code executor, iteratively refining plan generation and optimizing code execution by examining environment feedback in depth.

### Data Preparation

We use the [EHRSQL](https://github.com/glee4810/EHRSQL) benchmark for evaluation. The original dataset is for text-to-SQL tasks, and we have made adaptations to our evaluation. We release our clean and pre-processed version of [EHRSQL-EHRAgent](https://drive.google.com/file/d/1EE_g3kroKJW_2Op6T2PiZbDSrIQRMtps/view?usp=sharing) data. Please download the data and record the path of the data.

### Credentials Preparation
Our experiments are based on OpenAI API services. Please record your API keys and other credentials in the ``./ehragent/config.py``. 

### Setup

See ``requirements.txt``. Packages with versions specified in ``requirements.txt`` are used to test the code. Other versions that are not fully tested may also work. We also kindly suggest the users to run this code with Python version: ``python>=3.9``. Install required libraries with the following command:

```bash
pip3 install -r requirements.txt
```

### Instructions

The outputting results will be saved under the directory ``./logs/``. Use the following command to run our code:
```bash
python main.py --llm YOUR_LLM_NAME --dataset mimic_iii --data_path YOUR_DATA_PATH --logs_path YOUR_LOGS_PATH --num_questions -1 --seed 0
```

We also support debugging mode to focus on a single question:
```bash
python main.py --llm YOUR_LLM_NAME --dataset mimic_iii --data_path YOUR_DATA_PATH --logs_path YOUR_LOGS_PATH --debug --debug_id QUESTION_ID_TO_DEBUG

python main.py --llm gpt-35-turbo --dataset mimic_iii --data_path S:\Work\ehrsql-ehragent\mimic_iii\valid_preprocessed.json --logs_path C:\src\EhrAgent\logs --debug --debug_id 0d92a1f6eab9515735f242f4 --num_questions -1
```

Only MIMIC-III was evaluated at this moment.

### Issues and resolutions
#### OS environment difference
When reading files from file system, / was assumed to be path separator, since my environment is Windows, os.path.join was used instead

#### api/packages differences
When installing packages according to the original requirements.txt, autogen 1.0.16 was specified, but the latest to be found was 0.3.2 at the beginning of this effort, with 0.4 released on 11/22/2024 according to [pypi.org](https://pypi.org/project/pyautogen/#history). When accessing openai, api_type was not accessible and error was thrown, so api_type was not set. Package flaml[automl] was also added to resolve dependency issue.

#### Code exectuion
Agent prompt has mentioned certain functions are available including Calculate(FORMULA), LoadDB(DBNAME), FilterDB(DATABASE, CONDITIONS), GetValue(DATABASE, ARGUMENT), SQLInterpreter(SQL), Calendar(DURATION). While debugging execute_function, the agent requested to execute these functions, but the only registered function was python in main.py causing these functions not to be never found. 

After registering these functions, an error is thrown due to json in the response
```
{'content': None, 'role': 'assistant', 'function_call': {'arguments': '{"DBNAME":"prescriptions"}', 'name': 'LoadDB'}, 'tool_calls': None}
```
from gpt-4o-mini was not in the expected format of
```
{'cell': '<python code block>'}
```

After switching to gpt-4-0613, the response looks much better:
```
{'arguments': "# Load the prescriptions database
prescriptions_db = LoadDB('prescriptions')
# Filter the database for records of lidocaine 5% ointment
filtered_prescriptions_db = FilterDB(prescriptions_db, 'DRUG=lidocaine 5% ointment')

# Get the intake method of the drug
answer = GetValue(filtered_prescriptions_db, 'ROUTE')", 'name': 'python'}
```
set PYTHONPATH=
setx PYTHONPATH "%PYTHONPATH%;C:\src\EhrAgent"

python main.py --llm_autogen gpt-4-0613 --llm_azure gpt-4-0613 --dataset mimic_iii --data_path S:\Work\ehrsql-ehragent\mimic_iii\valid_preprocessed.json --logs_path C:\src\EhrAgent\logs --debug --debug_id 228a176ead6a30e7d7ea4a7b --num_questions -1


### Citation
If you find this repository useful, please consider citing:
```bibtex
@article{shi2024ehragent,
  title={Ehragent: Code empowers large language models for complex tabular reasoning on electronic health records},
  author={Shi, Wenqi and Xu, Ran and Zhuang, Yuchen and Yu, Yue and Zhang, Jieyu and Wu, Hang and Zhu, Yuanda and Ho, Joyce and Yang, Carl and Wang, May D},
  journal={EMNLP},
  year={2024}
}
```
