import os
import random
import yaml

num = int(input("要挑出多少個 Technique 來做訓練集："))

executors = {}
yaml_paths = []
cls = {}
cls_idx = 0
num_cls = {}

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

sorted_tech = sorted(executors.items(), key=lambda x: len(x[1]), reverse=True)
tech_payload = sorted_tech[:num]
tech_times = [(key, len(value)) for key, value in sorted_tech[:num]]
print(f'前 {num} 個最多的 Technique = {tech_times}')


print(f"Number of techniques: {len(executors)}")

ratio = 0.9
train = []
test = []
skip = [] # 裡面存放需要跳過的 Technique Name (只有一個 payload 的 Technique 屬於需要跳過的)
idx = 0
id_list = []
print(f"Splitting train and test with ratio {ratio} ...")

for t, ps in tech_payload: # 遍歷 tech_payload 的 Tuple (a,b)，tech_payload 是一個 List
    split_idx = int(0.9*len(ps))
    for p in ps[:split_idx]:
        pline = [p for p in p.split('\n')]
        train.append((idx, p)) # 將 (Technique Label ID, Payload) 加入到 train 中
    for p in ps[split_idx:]:
        test.append((idx, p))
    id_list.append((t,idx)) # 將 Technique Name, Label ID 加入 id_list
    idx = idx+1

print('Shuffling ...')
random.shuffle(train) # 將 train 中的元素作隨機排序，打亂 List 的元素順序
random.shuffle(test)

print('Writing to files ...')
# VAE
with open(f'train_large_{num}_vae.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(p + '\n')
with open(f'test__large_{num}_vae.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(p + '\n')

# Classifier
with open(f'train_large_{num}_cls.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(f"{cls_idx}\t{p}\n")
with open(f'test_large_{num}_cls.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(f"{cls_idx}\t{p}\n")

# GAN
with open(f'train_large_{num}_gan.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(f"0\t{p}\n")
with open(f'test_large_{num}_gan.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(f"0\t{p}\n")

# Technique, Class
with open('large_tech2class.txt', 'w') as f:
    f.write('technique, class \n')
    for tech, tech_id in id_list:
        f.write(f"{tech} {tech_id}\n")
