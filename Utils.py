import json
def read_my_file(file):
    f = open(file, "r", encoding="utf-8")
    data = f.read()
    return data


if __name__ == '__main__':

    read_my_file()