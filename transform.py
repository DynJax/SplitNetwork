from math import *

a = 6378137.0000  # 单位为m
b = 6356752.3142
B0 = 0;
L0 = 0;
e1 = sqrt(pow(a, 2) - pow(b, 2)) / a
e2 = sqrt(pow(a, 2) - pow(b, 2)) / b
K = a * cos(B0) / sqrt(1 - pow(exp(2), 2) * pow(sin(B0), 2))
print(a, b, B0, L0, e1, e2, K)


def get_coordinate(latitude, longitude):
    B = latitude
    L = longitude
    q = log(tan(pi / 4 + B / 2) * (1 - exp(1) * sin(B)) / (1 + exp(1) * sin(B)) ** exp(1 / 2))
    x = K * q
    y = K * (L - L0)
    return x, y


if __name__ == '__main__':

    content = []
    with open("D:/Workspace/Python/SplitNetwork/scheme/枢纽网络构建/最小的实验网/data/Tcoor.txt", 'r') as f:
        for line in f:
            lineList = line.split()
            if len(lineList) == 1:
                continue

            line = line.replace("\n", "")
            line = line.strip()
            lineList = line.split()
            content.append(lineList)

    for item in content:
        y = float(item[1])
        x = float(item[2])
        print(y, x)
        data = get_coordinate(x, y)
        print(data)
