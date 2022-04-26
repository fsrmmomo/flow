import time

from numpy import mean

from packet_struct import *
from dat_trace import *
import os
import sys
import pickle
import hashlib
import murmurhash as mmh

big_percent = 0.05


def analyze(all_result, big_sketch, mixed_sketch, measured_big_set):
    true_sum = 0
    m_sum = 0
    ARE = 0
    for k, v in all_result.items():
        true = v
        meas = 0
        if k in measured_big_set:
            meas = big_sketch.query(k) + mixed_sketch.query(k)
        else:
            meas = mixed_sketch.query(k)
        true_sum += true
        m_sum += meas
        ARE += abs(meas - true) / true
    print("流数目:{:1}".format(len(all_result)), end="  ")
    print("真实结果：" + str(true_sum), end="  ")
    print("测量结果：" + str(m_sum), end="  ")
    print("准确率为：{:.4f}".format((1 - abs(m_sum - true_sum) / true_sum)), end="  ")
    print("ARE：{:.4f}".format(abs(ARE / len(all_result))))

    return [(1 - abs(m_sum - true_sum) / true_sum), abs(ARE / len(all_result))]


def analyze3(all_result, big_sketch, mixed_sketch, measured_big_set):
    true_sum = 0
    m_sum = 0
    ARE = 0
    for k, v in all_result.items():
        true = v
        meas = 0
        if k in measured_big_set:
            meas = big_sketch.query(k)
        else:
            meas = mixed_sketch.query(k)
        true_sum += true
        m_sum += meas
        ARE += abs(meas - true) / true
    print("流数目:{:1}".format(len(all_result)), end="  ")
    print("真实结果：" + str(true_sum), end="  ")
    print("测量结果：" + str(m_sum), end="  ")
    print("准确率为：{:.4f}".format((1 - abs(m_sum - true_sum) / true_sum)), end="  ")
    print("ARE：{:.4f}".format(abs(ARE / len(all_result))))
    return [(1 - abs(m_sum - true_sum) / true_sum), abs(ARE / len(all_result))]


def analyze2(all_result, mixed_sketch):
    true_sum = 0
    m_sum = 0
    ARE = 0
    for k, v in all_result.items():
        true = v
        meas = mixed_sketch.query(k)

        true_sum += true
        m_sum += meas
        ARE += abs(meas - true) / true
    print("流数目:{:1}".format(len(all_result)), end="  ")
    print("真实结果：" + str(true_sum), end="  ")
    print("测量结果：" + str(m_sum), end="  ")
    print("准确率为：{:.4f}".format((1 - abs(m_sum - true_sum) / true_sum)), end="  ")
    print("ARE：{:.4f}".format(abs(ARE / len(all_result))))

    return [(1 - abs(m_sum - true_sum) / true_sum), abs(ARE / len(all_result))]


def sketch_measure(mode=0, T=5, total_mem=1000 * 1024):
    new_dat_dir = './data/dat/SB-F-202201051400/1/'
    N = T * 10
    if mode == 0:
        mixed_sketch = sketch(total_mem, 3, 2)
    else:
        mixed_sketch = sketch(total_mem, 3, 4)
    x = 0
    cc = 0
    trace_byte_size = 15
    all_result = dict()
    if T == 5 or T == 10:
        ilist = range(N, 2 * N)
    else:
        ilist = range(N)

    res = []
    for i in ilist:
        # for i in range(N):
        r_name = new_dat_dir + str(i) + '.dat'
        with open(r_name, 'rb') as f:
            bin_trace = f.read(trace_byte_size)
            while bin_trace:
                x += 1
                p = dat_trace()
                p.init_from_binary(bin_trace)
                if mode == 0:
                    if p.src_ip in all_result.keys():
                        all_result[p.src_ip] += 1
                    else:
                        all_result[p.src_ip] = 1
                    mixed_sketch.insert(p.src_ip, 1)
                else:
                    if p.src_ip in all_result.keys():
                        all_result[p.src_ip] += p.payload
                    else:
                        all_result[p.src_ip] = p.payload
                    mixed_sketch.insert(p.src_ip, p.payload)
                bin_trace = f.read(trace_byte_size)

        # if (i+1) % T == 0 and i != 0:
        if (i + 1) % T == 0:
            print("data-" + str(cc), end='  ')
            cc += 1
            res.append(analyze2(all_result, mixed_sketch))
            all_result.clear()
            mixed_sketch.clear()
    prec = [x[0] for x in res]
    prec.sort()
    prec = prec[1:-1]
    print("{:.4f}".format(mean(prec)))

    prec = [x[1] for x in res]
    prec.sort()
    prec = prec[1:-1]
    print("{:.4f}".format(mean(prec)))
    return res


def opt_measure(mode=0, T=5, total_mem=1000 * 1024, fraction=0.4):
    big = 2
    small = 1
    print("big = " + str(big), end=' ')
    print("small = " + str(small), end=' ')
    print(big_percent, end=' ')
    print(fraction)
    new_dat_dir = './data/dat/SB-F-202201051400/1/'
    N = T * 10
    count_f = './data/dat/SB-F-202201051400/count.pkl'
    trace_byte_size = 15
    sorted_list = []
    with open(count_f, 'rb') as f:
        sorted_list = pickle.load(f)

    big_set = set()
    all_result = dict()
    # sorted_list.sort(reverse=True, key=lambda x: x[2])

    for flow in sorted_list[:int(len(sorted_list) * big_percent)]:
        big_set.add(flow[0])

    big_sketch = sketch(int(total_mem * fraction), 3, big)
    if mode == 0:
        mixed_sketch = sketch(int(total_mem * (1 - fraction)), 3, small)
    else:
        mixed_sketch = sketch(int(total_mem * (1 - fraction)), 3, 4)
    # print(mixed_sketch.arrays)
    x = 0
    cc = 0
    if T == 5 or T == 10:
        ilist = range(N, 2 * N)
    else:
        ilist = range(N)
    res = []
    for i in ilist:
        # for i in range(N):
        r_name = new_dat_dir + str(i) + '.dat'
        with open(r_name, 'rb') as f:
            bin_trace = f.read(trace_byte_size)
            while bin_trace:
                x += 1
                p = dat_trace()
                p.init_from_binary(bin_trace)
                if mode == 0:
                    if p.src_ip in all_result.keys():
                        all_result[p.src_ip] += 1
                    else:
                        all_result[p.src_ip] = 1

                    if p.src_ip in big_set:
                        big_sketch.insert(p.src_ip, 1)
                    else:
                        mixed_sketch.insert(p.src_ip, 1)
                else:
                    if p.src_ip in all_result.keys():
                        all_result[p.src_ip] += p.payload
                    else:
                        all_result[p.src_ip] = p.payload

                    if p.src_ip in big_set:
                        big_sketch.insert(p.src_ip, p.payload)
                    else:
                        mixed_sketch.insert(p.src_ip, p.payload)
                bin_trace = f.read(trace_byte_size)

        if (i + 1) % T == 0:
            # print(sorted_list[:100])
            # print(len(sorted_list))
            # for l in sorted_list[:10000]:
            #     if big_sketch.query(l[0])>10:
            #         print(big_sketch.query(l[0]))
            # if()
            print("data-" + str(cc), end='  ')
            cc += 1
            res.append(analyze3(all_result, big_sketch, mixed_sketch, big_set))
            all_result.clear()
            big_sketch.clear()
            mixed_sketch.clear()

    prec = [x[0] for x in res]
    prec.sort()
    prec = prec[1:-1]
    print("{:.4f}".format(mean(prec)))

    prec = [x[1] for x in res]
    prec.sort()
    prec = prec[1:-1]
    print("{:.4f}".format(mean(prec)))
    return res


def measure_file(mode=0, T=5, total_mem=1000 * 1024, fraction=0.15):
    big = 2
    small = 1
    print("big = " + str(big), end=' ')
    print("small = " + str(small), end=' ')
    print(big_percent, end=' ')
    print(fraction)
    # new_dat_dir = './data/dat/SB-F-202201051400/1/'
    # new_dat_dir = './data/dat/SB-F-202201051400/0.5/'
    TT = 0.5
    if TT == 0.5:
        xx = 2
        new_dat_dir = './data/dat/SB-F-202201051400/0.5/'
    else:
        xx = 1
        new_dat_dir = './data/dat/SB-F-202201051400/1/'
    # N = T * 10
    # print(xx)
    N = T * 10 * xx

    count_f = './data/dat/SB-F-202201051400/count.pkl'
    trace_byte_size = 15
    sorted_list = []
    with open(count_f, 'rb') as f:
        sorted_list = pickle.load(f)

    big_set = set()
    all_result = dict()
    sorted_list.sort(reverse=True, key=lambda x: x[2])
    for flow in sorted_list[:int(len(sorted_list) * big_percent)]:
        big_set.add(flow[0])
    # print(sorted_list[:int(len(sorted_list) * big_percent)][-100:])
    # return

    # total_mem = 2000 * 1024
    # fraction = 0.05
    big_sketch = sketch(int(total_mem * fraction), 3, big)
    if mode == 0:
        mixed_sketch = sketch(int(total_mem * (1 - fraction)), 3, small)
    else:
        mixed_sketch = sketch(int(total_mem * (1 - fraction)), 3, 4)

    measured_big_set = set()
    tmp_big_set = set()
    x = 0
    cc = 0
    if T == 5 or T == 10:
        ilist = range(N, 2 * N)
    else:
        ilist = range(N)
    res = []
    for i in ilist:
        # print(i)
        # for i in range(N):
        r_name = new_dat_dir + str(i) + '.dat'
        with open(r_name, 'rb') as f:
            bin_trace = f.read(trace_byte_size)
            while bin_trace:
                x += 1
                p = dat_trace()
                p.init_from_binary(bin_trace)

                if mode == 0:
                    if p.src_ip in all_result.keys():
                        all_result[p.src_ip] += 1
                    else:
                        all_result[p.src_ip] = 1

                    if p.src_ip in measured_big_set:
                        big_sketch.insert(p.src_ip, 1)
                    else:
                        mixed_sketch.insert(p.src_ip, 1)
                else:
                    if p.src_ip in all_result.keys():
                        all_result[p.src_ip] += p.payload
                    else:
                        all_result[p.src_ip] = p.payload

                    if p.src_ip in measured_big_set:
                        big_sketch.insert(p.src_ip, p.payload)
                    else:
                        mixed_sketch.insert(p.src_ip, p.payload)

                # if (p.src_ip in big_set) and (all_result[p.src_ip] > 1):
                if p.src_ip in big_set:
                    # print("in")
                    tmp_big_set.add(p.src_ip)

                bin_trace = f.read(trace_byte_size)

        # if (i+1) % T == 0 and i != 0:
        if (i + 1) % (xx * T) == 0:
            # print(";" + str(i))
            print("data-" + str(cc), end='  ')
            cc += 1
            print(len(measured_big_set), end='  ')
            res.append(analyze(all_result, big_sketch, mixed_sketch, measured_big_set))
            all_result.clear()
            tmp_big_set.clear()
            measured_big_set.clear()
            big_sketch.clear()
            mixed_sketch.clear()
        else:
            # print("else" + str(i))
            # print(len(tmp_big_set))
            # measured_big_set = measured_big_set.union(tmp_big_set)
            # print(len(measured_big_set))
            measured_big_set = measured_big_set | tmp_big_set
            # print(len(measured_big_set))
            # print()
            tmp_big_set.clear()
    prec = [x[0] for x in res]
    prec.sort()
    prec = prec[1:-1]
    print("{:.4f}".format(mean(prec)))

    prec = [x[1] for x in res]
    prec.sort()
    prec = prec[1:-1]
    print("{:.4f}".format(mean(prec)))
    return res


class sketch:
    def __init__(self, size, d, n):
        self.w = size // d // n
        self.d = d
        self.arrays = [[0 for _ in range(self.w)] for _ in range(d)]
        self.seeds = [(i + 1) * 700 for i in range(d)]
        self.n = n
        self.max = pow(256, n) - 1

    def insert(self, key, value):
        for i, s in enumerate(self.seeds):
            x = mmh.hash(key.to_bytes(4, 'big'), seed=s)
            y = x % self.w

            self.arrays[i][y] += value
            self.arrays[i][y] = min(self.max, self.arrays[i][y])
        # print(self.arrays)

    def query(self, key):
        result = []
        for i, s in enumerate(self.seeds):
            x = mmh.hash(key.to_bytes(4, 'big'), seed=s)
            y = x % self.w
            result.append(self.arrays[i][y])
        return min(result)

    def clear(self):
        self.arrays = [[0 for _ in range(self.w)] for _ in range(self.d)]


def get_sorted():
    rf = './data/dat/SB-F-202201051400.dat'
    # pre = './data/feature/timeWin/SB-F-202201051400/'
    # wf = './data/feature/timeWin/SB-F-202201051400/origin/'
    count_wf = './data/dat/SB-F-202201051400/count.pkl'
    trace_byte_size = 32
    x = 0
    features = []
    # key_map.item = [key:[map_key, bytes, pkts]]
    key_map = {}
    N = 300
    T = 1
    t = T
    # tmp_feature.item = [map_key:feature]
    tmp_feature = {}
    # [map_key, bytes, pkts]
    sorted_list = []
    dat_list = []
    new_dat_dir = './data/dat/SB-F-202201051400/1/'
    with open(rf, 'rb') as f:

        bin_trace = f.read(trace_byte_size)
        tmp_list1 = []

        while bin_trace:
            x += 1
            p = packet_struct()
            p.init_from_binary(bin_trace)
            insert_p(p, tmp_feature, key_map, x)

            key = p.src_ip + p.src_port + p.dst_ip + p.dst_port + p.proto
            map_key = key_map[key][0]
            n_dat = dat_trace()
            n_dat.src_ip = map_key
            n_dat.src_port = 0
            n_dat.dst_ip = 0
            n_dat.dst_port = 0
            n_dat.proto = 0
            n_dat.payload = p.length
            tmp_list1.append(n_dat)

            if p.time > t:
                t += T
                print('p.time:' + str(p.time))
                tmp_list = []
                for k, v in tmp_feature.items():
                    tmp_list.append([k, v])
                features.append(tmp_list)
                print(len(tmp_feature))
                tmp_feature.clear()

                dat_list.append(tmp_list1[:])
                print(len(tmp_list1))
                tmp_list1.clear()

                if len(features) >= N:
                    break
                # break

            bin_trace = f.read(trace_byte_size)

    # return
    for i in range(N):
        new_dat_name = new_dat_dir + str(i) + '.dat'
        with open(new_dat_name, 'wb') as f:
            print(len(dat_list[i]))
            for dat in dat_list[i]:
                save_bin = dat.to_binary()
                # print(len(save_bin))
                f.write(save_bin)

    for k, v in key_map.items():
        sorted_list.append(v)
    sorted_list.sort(reverse=True, key=lambda x: x[1])

    print(sorted_list[:100])

    # w_list_name = pre + 'count.pkl'
    with open(count_wf, 'wb') as f:
        pickle.dump(sorted_list, f)


def insert_p(p, tmp_feature, key_map, now_win):
    key = p.src_ip + p.src_port + p.dst_ip + p.dst_port + p.proto
    # key = p.src_ip + " " + p.src_port + " " + p.dst_ip + " " + p.dst_port + " " + p.proto
    # key_map = {}
    # tmp_feature = {}
    length = p.length
    now_time = p.time
    map_key = None
    if key in key_map.keys():
        key_map[key][2] += 1
        key_map[key][1] += length
        map_key = key_map[key][0]
    else:
        map_key = len(key_map)
        # key_map[key] = [map_key, 1]
        # key_map[key] = [map_key, length]
        key_map[key] = [map_key, length, 1]

    if map_key in tmp_feature.keys():
        last_feature = tmp_feature[map_key]
        last_feature[0] += length
        last_feature[1] += 1
        last_feature[2] = max(last_feature[2], length)
        last_feature[3] = min(last_feature[3], length)
        last_feature[4] = ((last_feature[4] * (last_feature[1] - 1)) + length) / last_feature[1]
        last_feature[6] = now_win
        twin = now_time - last_feature[8]
        last_feature[8] = now_time
        last_feature[9] = max(twin, last_feature[9])
        last_feature[10] = min(twin, last_feature[10])
        last_feature[11] = ((last_feature[11] * (last_feature[1] - 2)) + twin) / (last_feature[1] - 1)
    else:
        # last_feature = [0 for _ in range(12)]
        last_feature = [0 for _ in range(14)]
        last_feature[0] += length
        last_feature[1] += 1
        last_feature[2] = length
        last_feature[3] = length
        last_feature[4] = length
        last_feature[5] = now_win
        last_feature[6] = now_win
        # twin = now_time - last_feature[8]
        last_feature[7] = now_time
        last_feature[8] = now_time
        # last_feature[9] = max(twin,last_feature[9])
        last_feature[10] = sys.maxsize
        # last_feature[11] = ((last_feature[11] * (last_feature[1] - 2)) + twin) / (last_feature[1] - 1)

        last_feature[12] = int(p.src_port)
        last_feature[13] = int(p.dst_port)
        # last_feature.append(int(p.src_port))
        # last_feature.append(int(p.dst_port))
        tmp_feature[map_key] = last_feature


def read_pkl():
    for file in os.listdir("./result/"):
        if file[-3:] == "pkl":
            with open("./result/" + file, 'rb') as f:
                result_dict = pickle.load(f)
                print(result_dict)


def get_es_result():
    rf = 'my_result'
    with open(rf, 'r') as f:
        lines = f.readlines()
        t = [5, 10]
        m = [512000, 1024000, 2048000]
        result_dict = {}
        for k in range(2):
            c_dict = {}
            for i in range(3):

                lines = lines[1:]
                c_dict[m[i]] = []
                for j in range(10):
                    tmp = lines[j].rstrip().split(',')
                    tmp = [float(x) for x in tmp]
                    c_dict[m[i]].append(tmp)
                lines = lines[10:]
            result_dict[t[k]] = c_dict
        # for cc,vv in result_dict.items():
        #     print(cc )
        #     print(vv )
        print(result_dict)
        with open("./result/es_result.pkl", 'wb') as f:
            pickle.dump(result_dict, f)
            # print(result_dict)
        # print(result_dict)


if __name__ == '__main__':
    K = 1024
    M = 1000 * K
    # read_pkl()
    # get_es_result()

    types = ["sketch", "opt", "test"]
    # times = [5, 10, 20, 30]
    times = [5, 10, 20]
    times = [5, 10]
    times = [5]
    mems = [0.5 * M, 1 * M, 1.5 * M, 2 * M, 2.5 * M]
    mems = [0.5 * M, 1 * M, 2 * M]
    mems = [1 * M]
    mems = [int(x) for x in mems]
    # wf = "./result/result.pkl"
    # for ty in types[2:]:
    #     ty = 'opt'
    for ty in types[1:2]:

        print(ty)
        wf = "./result/" + ty + "_result.pkl"
        result_list = {}
        for t in times:
            print(t)
            res = {}
            for m in mems:
                print(m)
                if ty == "sketch":
                    ans = sketch_measure(0, t, m)
                elif ty == "opt":
                    ans = opt_measure(0, t, m)
                else:
                    ans = measure_file(0, t, m)
                res[m] = ans
            result_list[t] = res

        # with open(wf, 'wb') as f:
        #     pickle.dump(result_list, f)
