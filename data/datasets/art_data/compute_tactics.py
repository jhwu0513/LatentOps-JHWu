import os
import random
import yaml

# 创建一个空字典
technique_to_tactic = {}

# 打开txt文件进行读取
with open('technique2tactic.txt', 'r') as file:
    # 逐行读取文件内容
    for line in file:
        # 分割每一行，并去除空格
        data = line.strip().split(' ',1)
        # 将读取的内容添加到字典中
        technique_to_tactic[data[0]] = data[1]

# 打印字典
# print(technique_to_tactic)
tactic_sample = {}

executors = {}
yaml_paths = []
cls = {}
cls_idx = 0
num_cls = {}

def truncate_string_at_dot(input_string):
    dot_index = input_string.find('.')
    if dot_index != -1:
        return input_string[:dot_index]
    else:
        return input_string


print('Collecting atomic red team yaml files ...')
techniques = [t for t in os.listdir('./atomic-red-team/atomics') if t.startswith('T')]
for t in techniques:
    technique_path = os.path.join('./atomic-red-team/atomics', t)
    yaml_file = [y for y in os.listdir(technique_path) if y.startswith('T') and y.endswith('.yaml')][0]
    yaml_path = os.path.join(technique_path, yaml_file)
    yaml_paths.append(yaml_path)

print('Parsing yaml files ...')
for y in yaml_paths:
    # print(y)
    with open(y, 'r') as f:
        data = yaml.safe_load(f)
        for test in data['atomic_tests']:
            if 'command' not in test['executor']: continue # 如果沒有payload，就跳過

            if test['executor']['name'] in ['powershell', 'cmd', 'command_prompt'] :
                payload = ';'.join([c for c in test['executor']['command'].strip('\n').split('\n')]) # payload 儲存一個 atomic test 的 command
            elif test['executor']['name'] in ['sh', 'bash']:
                payload = '&&'.join([c for c in test['executor']['command'].strip('\n').split('\n')])
            else: print(f"unknown name {test['executor']['name']}")

            if data['attack_technique'] not in executors: # executors 裡面存放 {'Technique Name':[ Payload List ]}
                executors[data['attack_technique']] = [payload] # executors 紀錄所有 technique 的 payload
                cls[data['attack_technique']] = cls_idx # cls 用來記錄 technique 對應的 Label ID，cls = {Technique Name : Technique Label ID}
                cls_idx += 1
                num_cls[data['attack_technique']] = 1
            else:
                executors[data['attack_technique']].append(payload)
                num_cls[data['attack_technique']] += 1
            ID = technique_to_tactic[truncate_string_at_dot(data['attack_technique'])]
            if ID in tactic_sample:
                tactic_sample[ID] += 1
            else:
                tactic_sample[ID] = 0

with open('tactic_samples.txt', 'w') as file:
    for key, value in tactic_sample.items():
        file.write(f"{key}: {value}\n")