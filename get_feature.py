import struct

import pyshark
from packet_struct import *
import os
import sys
import pickle

big_percent = 0.05


#               0     1     2           3           4           5           6           7           8         9         10      11
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes, start windows,end win, start time, end time, max twin, min twin, aver twin]

def read_dat(rf):
    # rf = './raw_data/MAWI/test.dat'
    # rf = './raw_data/MAWI/dat/SB-F-202201051400.dat'
    # pre = './feature/timeWin/SB-F-202201051400/'
    # wf = './feature/timeWin/SB-F-202201051400/'+ str(big_percent) + '/'
    rf = './raw_data/MAWI/dat/SB-F-202201021400.dat'
    pre = './feature/timeWin/SB-F-202201021400/'
    wf = './feature/timeWin/SB-F-202201021400/' + str(big_percent) + '/'
    trace_byte_size = 32
    x = 0
    features = []
    # key_map.item = [key:[map_key,pkts]]
    # key_map.item = [key:[map_key, bytes, pkts]]
    key_map = {}
    t = 5
    # tmp_feature.item = [map_key:feature]
    tmp_feature = {}
    # [map_key, bytes, pkts]
    sorted_list = []
    with open(rf, 'rb') as f:

        bin_trace = f.read(trace_byte_size)

        while bin_trace:
            x += 1
            # print(str(x) + '  ', end='')
            p = packet_struct()

            p.init_from_binary(bin_trace)
            # print(p)
            insert_p(p, tmp_feature, key_map, x)

            if p.time > t:
                # if p.time > t or x > 20000:
                t += 5
                # 导出tmp_feature = {}
                # wname = wf+ str(t/5) + '.pkl'
                print('p.time:' + str(p.time))
                tmp_list = []
                for k, v in tmp_feature.items():
                    tmp_list.append([k, v])
                features.append(tmp_list)
                tmp_feature.clear()
                # break

            bin_trace = f.read(trace_byte_size)

    if len(tmp_feature) != 0:
        print('p.time:' + str(p.time))
        tmp_list = []
        for k, v in tmp_feature.items():
            tmp_list.append([k, v])
        features.append(tmp_list)
        tmp_feature.clear()

    # save_map = [mapkey:key]
    save_map = {}

    for k, v in key_map.items():
        sorted_list.append(v)
        save_map[v[0]] = k
        # print(tmp_feature[v[0]])
        # print(v)
    sorted_list.sort(reverse=True, key=lambda x: x[1])

    w_list_name = pre + 'count.pkl'
    w_map_list_name = pre + 'mapkey_to_key.pkl'
    with open(w_map_list_name,'wb') as f:
        pickle.dump(save_map, f)

    # with open(w_list_name,'wb') as f:
    #     pickle.dump(sorted_list, f)

    print('len(features):' + str(len(features)))
    # for i in sorted_list:
    #     print(i)
    big_dict = {}
    small_dict = {}
    bound = int(len(sorted_list) * big_percent)
    for k in sorted_list[:bound]:
        big_dict[k[0]] = k[1]
    print(sorted_list[bound - 100:bound])
    # for k in sorted_list[bound:]:
    #     small_dict[k[0]] = k[1]

    # features = [
    #     time0 : [[map_key, feature, lable],  ...]
    #     ...
    # ]

    for tmp_list in features:
        for kv in tmp_list:
            if kv[0] in big_dict.keys():
                kv.append(1)
            else:
                kv.append(0)



    # for i in range(len(features)):
    #     f_list = features[i]
    #     wname = wf + str(i) + '.pkl'
    #     with open(wname, 'wb') as f:
    #         pickle.dump(f_list, f)


def read_pkl():
    wf = '../../Data/feature/timeWin/SB-F-202201051400/' + str(big_percent) + '/'
    pre = '../../Data/feature/timeWin/SB-F-202201051400/'
    # pre = '../../Data/feature/timeWin/SB-F-202201021400/'
    wname = wf + '0.pkl'

    with open(wname, 'rb') as f:
        f_list = pickle.load(f)
        bound = int(len(f_list) * big_percent)
        for i in f_list[bound - 100:bound]:
            print(i)
    #
    # w_list_name = pre + 'count.pkl'
    #
    # with open(w_list_name,'rb') as f:
    #     s_list = pickle.load(f)
    #     bound = int(len(s_list) * big_percent)
    #     x = 0
    #     for l in s_list[bound-100:bound]:
    #         # if l[1]<1000:
    #         #
    #         #     print(l)
    #         #     print(x)
    #         #     break
    #         # x += 1
    #         print(l)
    #     print("len :" + str(len(s_list)))


#               0     1     2           3           4           5           6           7           8         9         10      11
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes, start windows,end win, start time, end time, max twin, min twin, aver twin]
def insert_p(p, tmp_feature, key_map, now_win):
    key = p.src_ip + p.src_port + p.dst_ip + p.dst_port + p.proto
    key = p.src_ip + " " + p.src_port + " " + p.dst_ip + " " + p.dst_port + " " + p.proto
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
        last_feature = [0 for _ in range(12)]
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
        tmp_feature[map_key] = last_feature


if __name__ == '__main__':
    read_dat('')
    # read_pkl()
