import os
import random
import yaml

executors = {}
cls = {}
cls_idx = 0
num_cls = {}
unique_payload = set()

with open('./LockBit_technique_samples.txt', 'r') as file:
    for line in file:
        data = line.strip().split(' ',1)
        unique_payload.add(data[1])
        if data[0] not in executors:
            executors[data[0]] = [data[1]]
            cls[data[0]] = cls_idx
            cls_idx += 1
            num_cls[data[0]] = 1
        else:
            executors[data[0]].append(data[1])
            num_cls[data[0]] += 1

unique_payload = list(unique_payload)*100

print(f"Number of techniques: {len(executors)}")

ratio = 0.9
train = []
test = []
skip = [] # 裡面存放需要跳過的 Technique Name (只有一個 payload 的 Technique 屬於需要跳過的)
print(f"Splitting train and test with ratio {ratio} ...")
for t, ps in executors.items(): # 遍歷 executors 的鍵值對，executors 是一個 dictionary
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

random.shuffle(unique_payload)

print('Writing to files ...')
# # VAE
# with open(f'train_Lockbit_vae.txt', 'w') as f:
#     for p in unique_payload[:int(0.9*len(unique_payload))]:
#         f.write(p + '\n')
# with open(f'test_Lockbit_vae.txt', 'w') as f:
#     for p in unique_payload[int(0.9*len(unique_payload)):]:
#         f.write(p + '\n')

# VAE
with open('train_Lockbit_vae.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(p + '\n')
with open('test_vae.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(p + '\n')

# Classifier
with open(f'train_Lockbit_cls.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(f"{cls_idx}\t{p}\n")
with open(f'test_Lockbit_cls.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(f"{cls_idx}\t{p}\n")

# GAN
with open(f'train_Lockbit_gan.txt', 'w') as f:
    for cls_idx, p in train:
        f.write(f"0\t{p}\n")
with open(f'test_Lockbit_gan.txt', 'w') as f:
    for cls_idx, p in test:
        f.write(f"0\t{p}\n")

# Technique, Class, Count
with open(f'technique_Lockbit_cls_c.txt', 'w') as f:
    f.write('technique, class, count\n')
    for t in cls:
        f.write(f"{t} {cls[t]} {num_cls[t]}\n")
