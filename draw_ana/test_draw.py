import math
import random
from math import comb

import matplotlib
import murmurhash as mmh
from numpy import mean
import matplotlib.pyplot as plt
import numpy


class heavy:
    def __init__(self, size, d=2):
        self.w = size // d
        self.arrays = [[[] for _ in range(self.w)] for _ in range(d)]
        self.collision = [False for _ in range(self.w)]
        # self.seeds = [(i + 1) * 900 for i in range(d)]
        self.seeds = int(random.uniform(1, 1000))
        # print(self.seeds)
        self.d = d

    def insert(self, key):
        x = mmh.hash(key.to_bytes(4, 'big'), seed=self.seeds)
        y = x % self.w
        for i in range(self.d):
            table = self.arrays[i]
            if len(table[y]) == 0:
                table[y].append(key)
                return True
            elif table[y][0] == key:
                return True
        self.collision[y] = True
        return False

    def query(self, key):
        for i, s in enumerate(self.seeds):
            x = mmh.hash(key.to_bytes(4, 'big'), seed=s)
            y = x % self.w
            table = self.arrays[i]
            if len(table[y]) == 0:
                return 0
            elif table[y][0] == key:
                return table[y][1]
        return 0

    def clear(self):
        self.arrays = [[[] for _ in range(self.w)] for _ in range(self.d)]


def collision_of_one_bucket(n=int(1E5), w=int(1E5)):
    print("n:" + str(n))
    print("w:" + str(w))


def check_bucket_collision_formula(n=int(1E5), total=int(1E5), k=4):
    # k = 4
    # n = int(1E5)
    # total = int(1E5)
    w = total // k
    times = 100
    res = []
    # res.append(check_fomule())
    for i in range(times):
        count_collision_flow = 0
        count_collision_bucket = 0
        table = heavy(total, k)
        for i in range(n):
            if not table.insert(i):
                count_collision_flow += 1

        for f in table.collision:
            if f:
                count_collision_bucket += 1

        # print(count_collision_bucket)
        # print(count_collision_bucket / w)
        res.append(count_collision_bucket / w)
    print('%.6f' % mean(res))
    # print(count_collision_flow)
    # print(count_collision_flow / n)
    print('%.6f' % cul_one_bucket_binomial(n, w, k))
    # print('%.6f' % cul_one_bucket_possion(n, w, k))


def check_count_collision_formula(n=int(1E5), total=int(1E5), k=1):
    # k = 4
    # n = int(1E5)
    # total = int(1E5)
    w = total // k
    times = 100
    res = []
    # res.append(check_fomule())

    for i in range(times):
        count_collision_flow = 0
        count_collision_bucket = 0
        table = heavy(total, k)
        for i in range(n):
            if not table.insert(i):
                count_collision_flow += 1

        for f in table.collision:
            if f:
                count_collision_bucket += 1

        # print(count_collision_bucket)
        # print(count_collision_bucket / w)
        res.append(count_collision_flow / n)
    print('%.6f' % mean(res))
    # print(count_collision_flow)
    # print(count_collision_flow / n)
    # print('%.6f' % cul_one_bucket_binomial(n, w, k))
    print('%.6f' % cul_count_collision(n, w, k))
    # print('%.6f' % cul_one_bucket_possion(n, w, k))


def cul_count_collision(n=int(1E5), w=int(1E5), k=1):
    c = 0
    Lambda = n / w

    for i in range(k):
        c += (k - Lambda) * (math.exp(-1 * Lambda) * ((Lambda ** i) / num(i)))
    c += Lambda * (math.exp(-1 * Lambda) * ((Lambda ** (k - 1)) / num(k - 1)))
    c += Lambda - k
    return c / n * w


def draw_bucket_collision_with_w():
    n = int(1E5)
    # total = int(1E5)
    k = 1
    wlist = [10000 * i for i in range(1, 51)]
    y = [cul_one_bucket_binomial(n, w, k) for w in wlist]
    x = range(1, 51)

    # matplotlib.rc("font", family="MicroSoft YaHei", weight="bold")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(20, 10))
    plt.ylim(0, 1.1)
    plt.xlim(0, 51)
    plt.xlabel('w大小/万', fontsize=18)
    plt.ylabel('桶冲突概率', fontsize=18)
    plt.xticks(x, x, rotation=0, fontsize=15)
    plt.title('桶冲突概率随w数量变化曲线', fontsize=18)
    for a, b in zip(range(1, 51, 2), [y[i - 1] for i in range(1, 51, 2)]):
        # plt.text(a, b, "%d,%.2f" % (a, b), ha='center', va='bottom', fontsize=18)
        plt.text(a, b, "%.2f" % b, ha='center', va='bottom', fontsize=18)

    # plt.figure(figsize=(20, 10), dpi=70)
    plt.tick_params(labelsize=18)
    plt.plot(x, y, marker='*', color='coral')
    plt.show()


def draw_bucket_collision_with_k():
    n = int(1E5)
    # total = int(1E5)
    w = 100000
    kk = 20
    klist = [i + 1 for i in range(kk)]
    # wlist = [10000 * i for i in range(1, 51)]
    y = [cul_one_bucket_binomial(n, w // k, k) for k in klist]
    x = range(1, kk + 1)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(16, 9))
    plt.ylim(0.2, 0.5)
    plt.xlim(0, kk + 1)
    plt.xlabel('k', fontsize=18)
    plt.ylabel('桶冲突概率', fontsize=18)
    # plt.xticks(numpy.arange(10000, 500000, 10000), wlist, rotation=0)
    plt.xticks(x, x, rotation=0, fontsize=15)
    # plt.yticks(y, y, rotation=0,fontsize=15)
    # plt.legend(loc="best")
    plt.title('桶冲突概率随k数量变化曲线', fontsize=18)
    for a, b in zip(x, y):
        # plt.text(a, b, "%d,%.2f" % (a, b), ha='center', va='bottom', fontsize=18)
        plt.text(a, b, "%.3f" % b, ha='center', va='bottom', fontsize=18)

    # plt.figure(figsize=(20, 10), dpi=70)
    plt.tick_params(labelsize=18)
    plt.plot(x, y, marker='*', color='coral')
    plt.show()


def draw_flow_collision_with_w():
    n = int(1E4)
    # total = int(1E5)
    k = 1
    wlist = [1000 * i for i in range(1, 51)]
    y = [cul_count_collision(n, w, k) for w in wlist]
    x = range(1, 51)

    # matplotlib.rc("font", family="MicroSoft YaHei", weight="bold")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(20, 10))
    plt.ylim(0, 1.1)
    plt.xlim(0, 51)
    plt.xlabel('w大小/万', fontsize=18)
    plt.ylabel('流冲突概率', fontsize=18)
    plt.xticks(x, x, rotation=0, fontsize=15)
    plt.title('流冲突概率随w数量变化曲线', fontsize=18)
    for a, b in zip(range(1, 51, 2), [y[i - 1] for i in range(1, 51, 2)]):
        # plt.text(a, b, "%d,%.2f" % (a, b), ha='center', va='bottom', fontsize=18)
        plt.text(a, b, "%.2f" % b, ha='center', va='bottom', fontsize=18)

    # plt.figure(figsize=(20, 10), dpi=70)
    plt.tick_params(labelsize=18)
    plt.plot(x, y, marker='*', color='coral')
    plt.show()

def draw_flow_collision_with_k():
    n = int(1E5)
    # total = int(1E5)
    w = 200000
    kk = 20
    klist = [i + 1 for i in range(kk)]
    # wlist = [10000 * i for i in range(1, 51)]
    y = [cul_count_collision(n, w // k, k) for k in klist]
    x = range(1, kk + 1)

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(16, 9))
    plt.ylim(0, 0.3)
    plt.xlim(0, kk + 1)
    plt.xlabel('k', fontsize=18)
    plt.ylabel('流冲突概率', fontsize=18)
    # plt.xticks(numpy.arange(10000, 500000, 10000), wlist, rotation=0)
    plt.xticks(x, x, rotation=0, fontsize=15)
    # plt.yticks(y, y, rotation=0,fontsize=15)
    # plt.legend(loc="best")
    plt.title('流冲突概率随k数量变化曲线', fontsize=18)
    for a, b in zip(x, y):
        # plt.text(a, b, "%d,%.2f" % (a, b), ha='center', va='bottom', fontsize=18)
        plt.text(a, b, "%.3f" % b, ha='center', va='bottom', fontsize=18)

    # plt.figure(figsize=(20, 10), dpi=70)
    plt.tick_params(labelsize=18)
    plt.plot(x, y, marker='*', color='coral')
    plt.show()


def cul_one_bucket_binomial(n=int(1E5), w=int(1E5), k=1):
    p = 1 / w
    # P_c = 1 - ((n - 1) * p + 1) * ((1 - p) ** (n - 1))
    P_c = 1.0
    for i in range(k + 1):
        P_c -= comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return P_c


def cul_one_bucket_possion(n=int(1E5), w=int(1E5), k=1):
    p = 1 / w
    Lambda = n / w

    # P_c = 1 - ((n - 1) * p + 1) * ((1 - p) ** (n - 1))
    P_c = 1.0
    for i in range(k + 1):
        P_c -= math.exp(-1 * Lambda) * ((Lambda ** i) / num(i))
    return P_c


def num(n):
    if n == 0:
        return 1
    else:
        return n * num(n - 1)


# print(comb(3, 2))
if __name__ == '__main__':
    # draw_bucket_collision_with_k()
    # check_count_collision_formula()
    # draw_flow_collision_with_w()
    draw_flow_collision_with_k()
