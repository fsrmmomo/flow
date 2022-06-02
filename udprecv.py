import os
import socket
import struct
import _pickle as cPickle
from sklearn.model_selection import train_test_split

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


def get_prj_root():
    return os.path.abspath(os.curdir)


data_name = "SB-F-202201051400"
big_percent = 0.01
instances_dir = os.path.join(get_prj_root(), "./data/instances/" + data_name + "/0.5s/" + str(big_percent) + "/")


def recv_feature_and_send_result():
    # 加载模型
    model_file_name = "./data/model/0.5s/random_forest" + instances_dir.split("/")[-2] + ".pkl"
    with open(model_file_name, "rb") as fp:
        try:
            predict_model = cPickle.load(fp)
        except EOFError:
            print("模型为空")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = "127.0.0.1"
    port = 8001
    s.bind((host, port))  # 绑定地址（host,port）到套接字
    while True:
        # 接收客户端传过来的数据
        data, addr = s.recvfrom(1024)  # data是接收到的数据 addr是对方的地址 也就是发送方的地址

        # print(type(data))
        print("收到的数据为：", str(data))
        dlist = struct.unpack("5d9iI", data)
        print(dlist)
        feature = [0 for i in range(11)]
        feature[0] = dlist[0]
        feature[1] = dlist[1]
        feature[2] = dlist[5]
        feature[3] = dlist[6]
        feature[4] = dlist[7]
        feature[5] = dlist[2]
        feature[6] = dlist[3]
        feature[7] = dlist[4]
        feature[8] = dlist[8] / 1E6
        feature[9] = dlist[9] / 1E6
        feature[10] = dlist[10] / 1E6
        feature.extend(dlist[11:14])

        key = dlist[14]
        print(feature)
        print(key)
        result =  predict_model.predict([feature])
        print(result)
        print(type(result))

if __name__ == '__main__':
    recv_feature_and_send_result()
# print("addr",addr)

# send_data = input("请输入要发送到客户端的数据:\n")
# s.sendto(send_data.encode("gbk"),addr)
# s.close()
