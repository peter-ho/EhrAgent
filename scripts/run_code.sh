python main.py --llm XXX --dataset mimic_iii --data_path XXX --logs_path XXX --num_questions -1 --seed 0

python main.py --llm_autogen gpt-4-0613 --llm_azure gpt-4-0613 --dataset mimic_iii --data_path S:\Work\ehrsql-ehragent\mimic_iii\valid_preprocessed.json --logs_path C:\src\EhrAgent\logs --num_questions -1 --seed 0

python main.py --llm_autogen gpt-4-0613 --llm_azure gpt-4-0613 --dataset mimic_iii --data_path C:\src\EhrAgent\data\valid_preprocessed_exclude_cost.json --logs_path C:\src\EhrAgent\logs --num_questions -1 --seed 0 --debug  --debug_id 228a176ead6a30e7d7ea4a7b

python main.py --llm_autogen gpt-4-0613 --llm_azure gpt-4-0613 --dataset mimic_iii --data_path C:\src\EhrAgent\data\valid_preprocessed_exclude_cost.json --logs_path C:\src\EhrAgent\logs --num_questions -1 --seed 0 --reverse_sequence

### 
python main.py --llm_autogen gpt-4-0613 --llm_azure gpt-4-0613 --dataset mimic_maria --data_path C:\src\EhrAgent\data\valid_preprocessed_exclude_cost.json --logs_path C:\src\EhrAgent\logs_maria --num_questions -1 --seed 0
