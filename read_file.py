"""
该文件用于读取解析xxx.pkts文件内的相关统计数据
便于流识别程序识别其准确性
"""
import pickle
from collections import namedtuple
from logging import debug
from statistics import mean, variance, median
import os
from typing import List
import glob

import pandas as pd
import numpy as np
from common_utils import load_json, save_pkl
from path_utils import get_prj_root


win_size = 10  # 窗口大小
limit = 100000

Instance = namedtuple("Instance", ["features", "label", "id"])  # 实例





def get_filename(path):
    """
    获取同一个目录下面的所有ptks文件的文件名
    """
    # 获取文件名
    filename_list = []
    # 保存每个文件
    file_list = os.listdir(path)

    for i in file_list:
        # 判断后缀是否相同
        if os.path.splitext(i)[1] == '.pkts':
            # 将文件名保存到列表中
            filename_list.append((path + i))

    return filename_list



#               0     1     2           3           4           5           6           7           8         9         10      11
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes, start windows,end win, start time, end time, max twin, min twin, aver twin]

#               0     1     2           3           4           5              6          7                 8         9
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes,  windows size, time win size,  max twin, min twin, aver twin]

#               0     1     2           3           4           5              6          7                 8         9         10      11
# feature = [总Bytes,包数, max bytes , min bytes, aver bytes, start windows,end win, windows size, time win size,  max twin, min twin, aver twin]
# 读取我的特征文件然后生成对应的pkl
def read_pkl_to_instance(filename,big_dict):
    # print(filename)
    feature_list = []

    with open(filename, 'rb') as f:
        f_list = pickle.load(f)
        # print(f_list[:10])

        # 统计流的数量和总的流大小
        # tmp_dict = {}
        all_bytes = 0
        all_pkts = 0
        # f = [map_key, feature, lable]
        for f in f_list:
            # tmp_dict[f[0]] = 0
            all_bytes += f[1][0]
            all_pkts += f[1][1]
        # print(len(f_list))
        x = 0

        flow_num = len(f_list)



        for f in f_list:
            # print(f)
            # feature = f[1][:5]
            feature = f[1][:7]
            feature.append(f[1][6] - f[1][5])
            feature.append(f[1][8] - f[1][7])
            feature.append(f[1][9])
            feature.append(f[1][10])
            feature.append(f[1][11])

            feature.append(f[1][12])
            feature.append(f[1][13])

            feature[0] /= all_bytes
            feature[1] /= all_pkts
            feature[5] /= all_pkts
            feature[6] /= all_pkts
            feature[7] /= all_pkts
            # feature[0] = feature[0]/all_bytes*flow_num
            # feature[1] = feature[1]/all_pkts*flow_num
            # feature[5] = feature[5]/all_pkts
            # feature[6] = feature[6]/all_pkts
            # feature[7] = feature[7]/all_pkts

            # one_flow_feature = Instance(features=f[1], label=f[2])
            if f[0] in big_dict.keys():
                # print("big")
                one_flow_feature = Instance(features=feature, label=1, id=f[0])
            else:
                one_flow_feature = Instance(features=feature, label=0, id=f[0])

            # one_flow_feature = Instance(features=feature, label=f[2], id=f[0])
            feature_list.append(one_flow_feature)

            x += 1
            # if x<5:
            #     print(feature)
            #     print(feature)
    return feature_list

def gen_label_file(filename,big_dict):
    label_list = []
    with open(filename, 'rb') as f:
        f_list = pickle.load(f)
        for f in f_list:
            if f[0] in big_dict.keys():
                label_list.append(1)
                # print("big")
            else:
                label_list.append(0)

    return label_list


def read_pkl():
    wf = './data/feature/timeWin/SB-F-202201051400/0.05/'


    pre = '../../Data/feature/timeWin/SB-F-202201051400/'
    wname = wf + '0.pkl'

    # with open(wname, 'rb') as f:
    #     f_list = pickle.load(f)
    #     # for i in f_list[:200]:
    #     sum = 0
    #     n_train = int(len(f_list) * 0.7)
    #     for i in f_list[n_train:]:
    #         if i[2] == 1:
    #             sum += 1

    #     print(sum)
    wname = './data/instances/SB-F-202201021400/0.05/instance_0.pkl'

    # wname = './data/instances/instance_0.pkl'
    with open(wname, 'rb') as f:
        f_list = pickle.load(f)
        for i in f_list[:100]:
            print(i)


def generate_instance_pkl_by_feature_pkl(big_percent,data_name):
    """
    读取所有的feature pkl，生成instance
    :return:
    """
    # instances_dir = os.path.join(get_prj_root(), "./data/instances")  # 修改：instances_dir实例的路径
    # pkl_dir = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201051400/0.05/")
    # count_file = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201051400/count.pkl")
    # pkl_dir = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201021400/0.05/")
    # instances_dir = os.path.join(get_prj_root(), "./data/instances/test")  # 修改：instances_dir实例的路径
    # count_file = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201021400/count.pkl")

    # data_list = []
    # print(instances_dir)
    # big_percent = 0.2
    # big_percent = 0.05

    # data_name = "SB-F-202201051400"
    # data_name = "SB-F-202201021400"
    # data_name = "SB-F-202201041400"

    fn_head = "./data/feature/timeWin/" + data_name +"/"
    instances_head = "./data/instances/" + data_name + "/"
    fn_head = "./data/feature/1s/" + data_name +"/"
    instances_head = "./data/instances/" + data_name + "/1s/"
    fn_head = "./data/feature/0.5s/" + data_name +"/"
    instances_head = "./data/instances/" + data_name + "/0.5s/"

    # pkl_dir = fn_head + str(big_percent) + '/'
    # pkl_dir = fn_head + '0.05/'
    pkl_dir = fn_head + 'origin/'
    instances_dir = instances_head + str(big_percent) + '/'
    count_file = fn_head + "count.pkl"


    if os.path.isdir(pkl_dir):
        print("是目录")
    else:
        print("不是")
        os.mkdir(pkl_dir)
    if os.path.isdir(instances_head):
        print("是目录")
    else:
        print("不是")
        os.mkdir(instances_head)

    if os.path.isdir(instances_dir):
        print("是目录")
    else:
        print("不是")
        os.mkdir(instances_dir)

    f_list = []
    big_dict = {}

    with open(count_file, 'rb') as f:
        sorted_list = pickle.load(f)

        big_dict = {}
        bound = int(len(sorted_list) * big_percent)
        for k in sorted_list[:bound]:
            big_dict[k[0]] = k[1]
        # [map_key, feature, lable]

        # print(sorted_list[bound - 100:bound])

    y = 0
    files = os.listdir(pkl_dir)
    files.sort(key = lambda x:(len(x),x))
    # print(files)
    label_list = []
    save_pkl_file = []
    for file in files:
        if file[-3:] == "pkl":

        # if file == "0.pkl":
            y+=1
            # print("processing file {}".format(y))
            instances = []
            # pass
            fname = pkl_dir + file
            # print("load pkl:" + fname)
            instances = read_pkl_to_instance(filename=fname,big_dict=big_dict)
            save_pkl_file.append(instances)


            label_list = label_list + gen_label_file(filename=fname,big_dict=big_dict)

            print("{} 流的数量：{}".format(fname, len(instances)))
    print(len(save_pkl_file))
    save_file = "instances.pkl"
    save_pkl(os.path.join(instances_dir, save_file), save_pkl_file)


    print(len(label_list))
    save_lable_file = "label" + str(big_percent)
    save_pkl(os.path.join(instances_head, save_lable_file), label_list)



if __name__ == "__main__":
    # path = './raw_data/iot/'
    # # path = './raw_data/voip/'
    #
    # wait_saving_list = calc_data_list(path)
    #
    # deal(path, wait_saving_list)

    # generate_instances_pkl()
    # read_pkl()
    big_list = [0.05, 0.1, 0.2, 0.3]
    # big_list = [0.05]
    data_name = ["SB-F-202201051400","SB-F-202201041400","SB-F-202201021400"]
    for d in data_name[:1]:
        for b in big_list:
            print("processing d={0} b={1}:".format(d,b))
            generate_instance_pkl_by_feature_pkl(b,d)

    # read_pkts_generate_instances(filename="./tmp/pkts/video/Vimeo_Workstation.pkts", label='video')
