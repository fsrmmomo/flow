import _pickle as cPickle
import joblib
from common_utils import *  # 修改了
from argparse import ArgumentParser
from collections import namedtuple
from typing import List, Dict
# from path_utils import get_prj_root
from datetime import datetime
from path_utils import get_prj_root
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier  # 训练模型
import pandas as pd
import time
import glob

Instance = namedtuple("Instance", ["features", "label"])  # 实例

dirs = {
    "video": "./tmp/dt/video",
    "iot": "./tmp/dt/iot",
    "car": "./tmp/dt/car",
}

pkts_dirs = {
    "video": "./even/pkts/video",
    "iot": "./even/pkts/iot",
    "voip": "./even/pkts/voip"
}
instances_dir = os.path.join(get_prj_root(), "./classify/instances2")  # 修改：instances路径


def test():
    videos = load_pkl(os.path.join(instances_dir, "video.pkl"))
    print(videos)


def get_time():
    path = "raw_data/iot/example.pkts"
    # path = "tmp/pkts/video/Vimeo_Workstation.pkts"
    # path = "raw_data/voip/85.pkts"
    # path = "tmp/pkts/voip/captured.voip.pkts"
    dic = dict()
    with open(path, 'r') as f:
        lines = f.readlines()

        sum = 0
        for line in lines:
            sum += (float) (line.split()[0])
            dic[line.split()[3]] = 1

        print(sum / 1e9)
        print(len(lines) / (sum / 1e9))
        print(len(dic))


def divide_by_flow():
    for flow_type, dirname in pkts_dirs.items():
        dic = {}
        pkts_list = glob.glob(dirname + "/*.pkts")  # 获取每个pkts文件
        for pkts in pkts_list:
            # 获取flow的id和类型
            with open(pkts, 'r') as f:
                lines = f.readlines()
                flow_id_list = []
                for line in lines:
                    if line.split()[3] not in flow_id_list:
                        flow_id_list.append(line.split()[3])
                print("flow_id_list: ", len(flow_id_list))
                dic.fromkeys(flow_id_list, [])
                for line in lines:
                    dic[line.split()[3]].append(line)
            # 重新保存
            for flow_id, flows in dic.items():
                with open(dirname + "/split/" + flow_type + flow_id + ".pkts", 'w') as f:
                    for line in flows:
                        f.write(line + "\r")
                f.close()


def divided_flows(out_path, path):
    # path = "tmp/pkts/video/Vimeo_Workstation.pkts"
    # path = "raw_data/voip/85.pkts"
    # path = "tmp/pkts/voip/captured.voip.pkts"
    dic = dict()
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            dic[line.split()[3]] = []
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            dic[line.split()[3]].append(line)
    for k, v in dic.items():
        with open(out_path + "_" + k + ".pkts", 'w') as f:
            for line in v:
                f.write(line)
    # print(dic)


if __name__ == '__main__':
    # test()
    # get_time()
    # out_path = "even/pkts/iot/iot"
    # path = "even/pkts/iot/example.pkts"
    out_path = "even/pkts/voip/voip"
    path = "even/pkts/voip/captured.voip.pkts"
    divided_flows(out_path, path)
