# 用來生成 LockBit classifier 訓練資料的 Python
import os
import random
import yaml

samples = set()
step_samples = {}
exclude_random = {}

# for i in range(12):
#     step_samples[i] = [[],[]] # 分別存放屬於 0 的跟不屬於 0 的 payload
#     exclude_random[i] = []

cls = {}
cls_idx = 0
exist = set()

with open('../LockBit_technique_samples.txt', 'r') as file:
    for line in file:
        data = line.strip().split(' ',1)
        if data[0] not in exist:
            cls[data[0]] = cls_idx
            step_samples[cls_idx] = [[],[]]
            exclude_random[cls_idx] = []
            cls_idx += 1
            exist.add(data[0])
        num = cls[data[0]]
        step_samples[num][0].append(data[1])
        samples.add(data[1])

for i in range(cls_idx):
    exclude = list(samples -  set(step_samples[i][0]))
    # step_samples[i].append(exclude)
    
    payloads = []
    for p in step_samples[i][0]:
        payloads.append(p)
    
    for j in range(len(step_samples[i][0])):
        random_num = random.randint(0, len(exclude)-1)
        while exclude[random_num] in payloads:
            random_num = random.randint(0, len(exclude)-1)
        step_samples[i][1].append(exclude[random_num])

for i in range(cls_idx):
    with open(f'{i}_train.txt', 'w') as f:
        idx = int(0.9*len(step_samples[i][0]))
        for p in step_samples[i][0][:idx]:
            f.write(f"1\t{p}\n")
        for p in step_samples[i][1][:idx]:
            f.write(f"0\t{p}\n")
for i in range(cls_idx):
    with open(f'{i}_test.txt', 'w') as f:
        for p in step_samples[i][0][idx:]:
            f.write(f"1\t{p}\n")
        for p in step_samples[i][1][idx:]:
            f.write(f"0\t{p}\n")
for i in range(cls_idx):
    with open(f'cls2technique.txt', 'w') as f:
        f.write('technique, class\n')
        for t in cls:
            f.write(f"{t} {cls[t]}\n")

