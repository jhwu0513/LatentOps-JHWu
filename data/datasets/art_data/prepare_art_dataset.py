import os
import random
import yaml

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
                payload = ';'.join([c for c in test['executor']['command'].strip('\n').split('\n')])
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

print(f"Number of techniques: {len(executors)}")

ratio = 0.9
train = []
test = []
skip = [] # 裡面存放需要跳過的 Technique Name (只有一個 payload 的 Technique 屬於需要跳過的)
print(f"Splitting train and test with ratio {ratio} ...")
for t, ps in executors.items(): # 遍歷 executors 的鍵值對，executors 是一個 dictionary
    if len(ps) == 1: 
        skip.append(t)
        continue
    else:
        split_idx = int(0.9*len(ps))
        for p in ps[:split_idx]:
            pline = [p for p in p.split('\n')]
            train.append((cls[t], p)) # 將 (Technique Label ID, Payload) 加入到 train 中
        for p in ps[split_idx:]:
            test.append((cls[t], p))
print(f"Train: {len(train)}")
print(f"Test: {len(test)}")
print(f"Skipped {len(skip)} techniques cuz there's only one sample. You can find the skipped technique in skip.txt.")
print(f"Total number of techniques: {len(cls) - len(skip)}")

print('Shuffling ...')
random.shuffle(train) # 將 train 中的元素作隨機排序，打亂 List 的元素順序
random.shuffle(test)

print('Writing to files ...')
# VAE
with open('train_vae.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(p + '\n')
with open('test_vae.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(p + '\n')

# Classifier
with open('train_cls.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(f"{cls_idx}\t{p}\n")
with open('test_cls.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(f"{cls_idx}\t{p}\n")

# GAN
with open('train_gan.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(f"0\t{p}\n")
with open('test_gan.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(f"0\t{p}\n")

# Skkiped
with open('skip.txt', 'w') as f:
    for t in skip:
        f.write(f"{t}\n")

# Technique, Class, Count
with open('t_cls_c.txt', 'w') as f:
    f.write('technique, class, count\n')
    for t in cls:
        f.write(f"{t} {cls[t]} {num_cls[t]}\n")
