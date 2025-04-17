import os

file_list = []
delete_list = []

for (root, dirs, file) in os.walk("C:\\Users\\119252\Desktop\\Py Tools\\wayback\\bleeping_computer"):
    for f in file:
        if '.txt' in f:
            file_list.append(f'{root}/{f}')

print(len(file_list))

for q in file_list:
    with open(q, 'r', encoding='utf-8') as file:
        content = file.read()
        if 'Your Browser is Outofdate and Cannot Access the Internet' in content:
            delete_list.append(q)
        else:
            continue

print(len(delete_list))

for boop in delete_list:
    os.remove(boop)
    print(f'{boop} BALETED')