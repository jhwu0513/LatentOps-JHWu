# 用來生成 LockBit classifier 訓練資料的 Python
import os
import random
import yaml

samples = set()
step_samples = {}
exclude_random = {}

for i in range(12):
    step_samples[i] = [[],[]] # 分別存放屬於 0 的跟不屬於 0 的 payload
    exclude_random[i] = []

with open('../lockbit_samples.txt', 'r') as file:
    for line in file:
        data = line.strip().split(' ',1)
        num = int(data[0])
        step_samples[num][0].append(data[1])
        samples.add(data[1])

for i in range(12):
    exclude = list(samples -  set(step_samples[i][0]))
    # step_samples[i].append(exclude)
    
    payloads = []
    for p in step_samples[i][0]:
        payloads.append(p)
        payloads.append(f'powershell -c "{p}"')
        payloads.append(f'cmd.exe /c "{p}"')
    
    for j in range(len(step_samples[i][0])):
        random_num = random.randint(0, len(exclude)-1)
        while exclude[random_num] in payloads:
            random_num = random.randint(0, len(exclude)-1)
        step_samples[i][1].append(exclude[random_num])

for i in range(12):
    with open(f'{i}_train.txt', 'w') as f:
        for p in step_samples[i][0]:
            f.write(f"1\t{p}\n")
        for p in step_samples[i][1]:
            f.write(f"0\t{p}\n")

