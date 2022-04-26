import struct

from packet_struct import *
from dat_trace import *
import os
import sys
import pickle

big_percent = 0.05


#               0     1     2           3           4           5           6           7           8         9         10      11
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes, start windows,end win, start time, end time, max twin, min twin, aver twin]

def get_new_dat_for_es():
    wdat = './data/dat/SB-F-202201051400/'
    time = [5, 10]
    # time = [5, 10, 20, 30]
    # time = [10, 20, 30]
    time = [0.5]
    for T in time:
        if T == 5 or T == 10:
            t = 11*T
            mint = 10*T
        else:
            t = T
            mint = 0
        new_dat_dir = wdat + str(T) + '/'
        if os.path.isdir(new_dat_dir):
            print("是目录")
        else:
            print("不是")
            os.mkdir(new_dat_dir)

        trace_byte_size = 32
        x = 0
        features = []
        # key_map.item = [key:[map_key, bytes, pkts]]
        key_map = {}
        # t = T
        N = 10
        N = 600
        # tmp_feature.item = [map_key:feature]
        tmp_feature = {}
        # [map_key, bytes, pkts]
        sorted_list = []
        dat_list = []
        with open('./data/dat/SB-F-202201051400.dat', 'rb') as f:
            bin_trace = f.read(trace_byte_size)
            tmp_list = []
            y = 0
            while bin_trace:
                x += 1
                y += 1
                p = packet_struct()
                p.init_from_binary(bin_trace)
                if p.time<mint:
                    y=0
                    bin_trace = f.read(trace_byte_size)
                    continue

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

                tmp_list.append(n_dat)

                bin_trace = f.read(trace_byte_size)

                if p.time > t:
                    print("y=" + str(y))
                    # print(len(key_map))
                    y = 0
                    # print(x)
                    t += T
                    print('p.time:' + str(p.time))
                    dat_list.append(tmp_list[:])
                    # print(len(tmp_list))
                    tmp_list.clear()

                    if len(dat_list) >= N:
                        break
                    # break


        # for i in range(N):
        #     new_dat_name = new_dat_dir + str(i) + '.dat'
        #     with open(new_dat_name, 'wb') as f:
        #         print(len(dat_list[i]))
        #         for dat in dat_list[i]:
        #             save_bin = dat.to_binary()
        #             # print(len(save_bin))
        #             f.write(save_bin)
        for k, v in key_map.items():
            sorted_list.append(v)
            # save_map[v[0]] = k
            # print(tmp_feature[v[0]])
            # print(v)
        sorted_list.sort(reverse=True, key=lambda x: x[2])

        w_list_name = './data/dat/SB-F-202201051400/' + 'count.pkl'
        with open(w_list_name,'wb') as f:
            pickle.dump(sorted_list, f)


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


#               0     1     2           3           4           5           6           7           8         9         10      11          12      13
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes, start windows,end win, start time, end time, max twin, min twin, aver twin, dst port, src port]
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


def read_dat():
    rf = './raw_data/MAWI/dat/SB-F-202201051400.dat'
    pre = './data/feature/timeWin/SB-F-202201051400/'
    wf = './data/feature/timeWin/SB-F-202201051400/origin/'
    pre = './data/feature/1s/SB-F-202201051400/'
    wf = './data/feature/1s/SB-F-202201051400/origin/'
    pre = './data/feature/0.5s/SB-F-202201051400/'
    wf = './data/feature/0.5s/SB-F-202201051400/origin/'
    trace_byte_size = 32
    x = 0
    features = []
    # key_map.item = [key:[map_key,pkts]]
    # key_map.item = [key:[map_key, bytes, pkts]]
    key_map = {}
    T = 1
    t = T
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
                t += T
                # 导出tmp_feature = {}
                # wname = wf+ str(t/5) + '.pkl'
                print('p.time:' + str(p.time))
                tmp_list = []
                for k, v in tmp_feature.items():
                    tmp_list.append([k, v])
                features.append(tmp_list)
                print(len(tmp_feature))
                tmp_feature.clear()

                if len(features) >= 300:
                    break
                # break

            bin_trace = f.read(trace_byte_size)
    # return

    if len(tmp_feature) != 0 and len(features) < 300:
        print('p.time:' + str(p.time))
        tmp_list = []
        for k, v in tmp_feature.items():
            tmp_list.append([k, v])
        features.append(tmp_list)
        tmp_feature.clear()

    # save_map = [mapkey:key]
    # save_map = {}

    for k, v in key_map.items():
        sorted_list.append(v)
        # save_map[v[0]] = k
        # print(tmp_feature[v[0]])
        # print(v)
    sorted_list.sort(reverse=True, key=lambda x: x[1])

    w_list_name = pre + 'count.pkl'
    # w_map_list_name = pre + 'mapkey_to_key.pkl'
    # with open(w_map_list_name,'wb') as f:
    #     pickle.dump(save_map, f)
    print(sorted_list[:100])

    with open(w_list_name, 'wb') as f:
        pickle.dump(sorted_list, f)

    print('len(features):' + str(len(features)))
    # for i in sorted_list:
    #     print(i)
    big_dict = {}
    small_dict = {}
    bound = int(len(sorted_list) * big_percent)
    for k in sorted_list[:bound]:
        big_dict[k[0]] = k[1]
    # print(sorted_list[bound - 100:bound])
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

    for i in range(len(features)):
        f_list = features[i]
        wname = wf + str(i) + '.pkl'
        with open(wname, 'wb') as f:
            pickle.dump(f_list, f)


if __name__ == '__main__':
    # read_dat('')
    get_new_dat_for_es()
    # read_pkl()
