with open("F:\\Matann\\fa.txt", 'r', encoding='utf-8') as file:
    ls = []
    data = file.readlines()
    for line in data:
        line = line.strip()
        ls.append(line)
with open("F:\\Matann\\fa.txt", 'w', encoding='utf-8') as file:
    data = file.readlines()
    for line in data:
        file.write(line)
