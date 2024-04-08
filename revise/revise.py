import re

def extract_quoted_strings(instruction):
    # 使用正则表达式匹配包含引号的字串
    quoted_strings = re.findall(r'"([^"]*)"', instruction)
    return quoted_strings

def match_instructions(A,B):
    # 将E指令中的参数解析出来
    B_params = set(B.split()[1:])

    # 对于每个A~D指令，检查是否存在E指令中的参数，并构建修正后的指令
    corrected_instructions = []

    params = set(A.split())
    corrected_params = []

    # 匹配路径变量并添加到修正后的指令中
    quoted_strings = extract_quoted_strings(B)
    for i in quoted_strings:
        corrected_params.append(i)

    # 匹配E指令中的参数并添加到修正后的指令中
    for param in B_params:
        if param in params:
            corrected_params.append(param)
            continue

    # 删除修正后的指令中的重复参数
    # corrected_params = list(dict.fromkeys(corrected_params))

    # 将修正后的指令添加到列表中
    corrected_instructions.append(' '.join(corrected_params))

    return corrected_instructions[0]

# 测试演算法
L = []
with open('input.txt', 'r') as file:
    for line in file:
        # 根據process name和command之間的分隔符進行分割
        L.append(line.strip())
# print(L[:5])

def read_commands_from_file(file_path):
    command_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            # 根據process name和command之間的分隔符進行分割
            parts = line.strip().split(' ',1)
            process_name = parts[0]
            command_dict[process_name] = line.strip()
    return command_dict

# 測試函數
file_path = 'utility.txt'  # 指定檔案路徑
command_dict = read_commands_from_file(file_path)

out = []
for i in L:
    if i.split(' ',1)[0] in command_dict:
        process = i.split(' ',1)[0]
        corrected_instructions = match_instructions(i,command_dict[process])
        # print(corrected_instructions)
        out.append(process+' '+corrected_instructions)
    else:
        out.append(i)

def write_list_to_file(data_list, file_path):
    with open(file_path, 'w') as file:
        for item in data_list:
            file.write(str(item) + '\n')

write_list_to_file(out, 'output.txt')
