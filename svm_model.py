"""
预测函数：随机森林
8个特征的（前五个包大小，后五个包间隔）：最小值，最大值，平均值，方差
每次运行前，检查：
四个需要修改的地方，命名是否正确
最后的运行模式是否正确
"""
import random

import _pickle as cPickle
import joblib
from sklearn import svm
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


from thundersvm import *
import dill

from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

import pickle


my_data_list = []
my_test_data = []
my_test_model = None
ss = None
def train_and_predict(instances_dir):
    my_data_list.clear()
    # instances_dir = os.path.join(get_prj_root(), "./data/instances/")  # 修改：instances路径
    data_list = []
    print(instances_dir)
    for file in os.listdir(instances_dir):
        if file[-3:] == "pkl":
            # if file == "instance_0.pkl":
            # pass
            # print("load pkl:" + instances_dir + file)
            data_list = data_list + load_pkl(instances_dir + file)
            # data_list.append(load_pkl(instances_dir+file))
    print(len(data_list))
    n_train = int(len(data_list) * 0.7)
    d_train = data_list[:n_train]
    d_test = data_list[n_train:]
    # my_data_list = data_list
    my_data_list.extend(data_list)
    # print("#my train {}".format(len(d_train)))
    # print("#my test {}".format(len(d_test)))

    d_train,d_test = train_test_split(data_list,train_size=0.7,random_state=10,shuffle=True)

    global my_test_data
    my_test_data = d_test
    # print("#my train {}".format(len(d_train)))
    # print("#my test {}".format(len(d_test)))

    train = []
    # =====================================
    train = d_train

    # random.shuffle(train)
    train_x = [x.features for x in train]
    # train_x = [x[:-2] for x in train_x]
    train_y = [x.label for x in train]
    test = []
    # ===============================
    test = d_test
    # random.shuffle(test)
    test_x = [t.features for t in test]
    # test_x = [x[:-2] for x in test_x]
    test_y = [t.label for t in test]

    global ss
    ss = StandardScaler()
    train_x = ss.fit_transform(train_x)
    test_x = ss.transform(test_x)






    # 训练以及预测
    predict_model = RandomForestClassifier(n_jobs=-1)  # 引入训练方法
    # predict_model = svm.SVC(kernel='linear')
    predict_model = SVC(kernel='linear')
    predict_model = SGDClassifier()
    # predict_model = svm.LinearSVC(tol=0.001,max_iter=2000)
    print("正在拟合")
    # print(train_x)
    # print(train_y)
    # print(train_x[0])
    # print(train_y[0])
    # predict_model.fit(train_x, train_y)  # 对训练数据进行拟合
    start = time.time()  # 计算时间
    predict_model.fit(train_x, train_y)  # 对训练数据进行拟合
    elapsed = (time.time() - start)
    print("Time used:", elapsed)

    model_file_name = "./data/model/svm" + instances_dir.split("/")[-2] + ".pkl"

    # predict_model.save_to_file(model_file_name)
    # predict_model.load_from_file(model_file_name)
    with open(model_file_name, "wb") as fp:
        cPickle.dump(predict_model, fp)
        # joblib.dump(predict_model, fp)
        # dill.dump(predict_model, fp)
        fp.close()
    # predicts = predict_model.predict(test_x)

    with open(model_file_name, "rb") as fp:
        try:
            predict_model = cPickle.load(fp)
            # predict_model = joblib.load(fp)
            # predict_model = dill.load(fp)
        except EOFError:
            print("模型为空")

    predicts = predict_model.predict(test_x)

    global my_test_model

    my_test_model = predict_model

    pre_y_name = []

    acc = predict_model.score(test_x, test_y)  # 根据给定数据与标签返回正确率的均值
    print('决策树模型评价:', acc)

    # 评价模型
    count = 0
    count0 = 0
    count1 = 0
    for idx in range(len(test_x)):
        if int(predicts[idx]) == int(test_y[idx]):
            count += 1
            if int(predicts[idx]) == 0:
                count0 += 1
            if int(predicts[idx]) == 1:
                count1 += 1

    all_big = sum(test_y)
    print(all_big)
    print(count1)

    print("big accuracy {:.2f}%".format(count1 / all_big * 100))
    print("ALL Accuracy {:.2f}%".format(count / len(test_x) * 100))
    print("##########################")
    test_classify()



def test_classify(instances_dir=None):
    # instances_dir = os.path.join(get_prj_root(), "./data/instances/")  # 修改：instances路径
    # instances_dir = os.path.join(get_prj_root(), "./data/instances/test/")  # 修改：instances路径
    data_list = []
    print(instances_dir)
    stat = {}
    if len(my_data_list) == 0:
        for file in os.listdir(instances_dir):
            if file[-3:] == "pkl":
                # if file == "instance_0.pkl":
                # pass
                # print("load pkl:" + instances_dir + file)
                data_list = data_list + load_pkl(instances_dir + file)

                # data_list.append(load_pkl(instances_dir+file))
    else:
        data_list = my_data_list

    n_train = int(len(data_list) * 0.7)
    # d_test = data_list[n_train:]
    # print("#my test {}".format(len(d_test)))
    # data_list = data_list[n_train:]
    # data_list = train_test_split(data_list, train_size=0.7, random_state=10, shuffle=True)
    if len(my_test_data)!=0:
        data_list = my_test_data




    for f in data_list:
        if f.id not in stat.keys():
            stat[f.id] = [f.label, 0]


    test_x = [x.features for x in data_list]
    # test_x = [x[:-2] for x in test_x]
    # print(len(test_x))
    # print(len(test_x[0]))
    test_y = [x.label for x in data_list]
    # print(len(test_y))

    test_x = ss.transform(test_x)

    print("加载模型。。。")
    if my_test_model == None:
        model_file_name = "./data/model/svm" + instances_dir.split("/")[-2] + ".pkl"
        with open(model_file_name, "rb") as fp:
            try:
                predict_model = cPickle.load(fp)
            except EOFError:
                print("模型为空")
    else:
        predict_model = my_test_model


    print("加载完成，开始预测")
    predicts = predict_model.predict(test_x)

    # 评价模型
    count = 0
    count0 = 0
    count1 = 0
    for idx in range(len(test_x)):
        if int(predicts[idx]) == int(test_y[idx]):
            #预测正确
            count += 1
            if int(predicts[idx]) == 0:
                #小流正确
                count0 += 1
            if int(predicts[idx]) == 1:
                #大流正确
                # stat[data_list[idx].id][1] = 1
                count1 += 1
        if int(predicts[idx]) == 1:
            stat[data_list[idx].id][1] = 1

    # print(type(test_y[0]))
    all_big = sum(test_y)

    b_flow_n = 0
    c_flow_n = 0

    w_big_flow_n = 0
    w_flow_n = 0

    res_b_n = 0
    print(len(stat))
    for k, v in stat.items():
        if v[0] != v[1]:
            # 总错误
            w_flow_n += 1
        if v[0] == 0 and v[1] == 1:
            # 小流变大流
            w_big_flow_n += 1
        if v[0] == 1:
            b_flow_n += 1
            if v[1] == 1:
                # 大流是大流
                c_flow_n += 1
        if v[1] == 1:
            res_b_n += 1
    # print(b_flow_n)
    # print(c_flow_n)
    # print(w_big_flow_n)
    # print(w_flow_n)
    # print(res_b_n)

    print("特征数："+ str(len(data_list)))
    print("大流特征数："+ str(all_big))
    print("大流正确特征数："+ str(count1))
    print("大流特征数占比：{:.2f}%".format(all_big/len(data_list)* 100))
    print("小流特征数占比：{:.2f}%".format((1-all_big/len(data_list))* 100))
    # print("大流正确特征数："+ str(count1))

    print("all feature big recall {:.2f}%".format(count1 / all_big * 100))
    print("aLL feature Accuracy {:.2f}%".format(count / len(test_x) * 100))

    print("流的数量是：{}".format(len(stat)))
    print("大流的数量是：{0},占比{1:.2f}".format(b_flow_n,b_flow_n/len(stat)))
    print("识别出的大流的数量是：{}".format(res_b_n))
    print("识别错误的数量是：{0},占总比例{1:.2f}%".format(w_flow_n, w_flow_n / len(stat) * 100))
    print("小流识别成大流的数量是：{0},占小流比例：{1:.2f}%,占大流比例:{2:.2f}%".format(w_big_flow_n,
                                                                 w_big_flow_n / (len(stat) - b_flow_n) * 100,
                                                                 w_big_flow_n / b_flow_n * 100))
    print("大流识别成大流的数量是：{0},占大流比例：{1:.2f}%,占判定大流的比例：{2:.2f}%".format(c_flow_n,
                                                                    c_flow_n / b_flow_n * 100,
                                                                    c_flow_n / res_b_n * 100))

    # print("real big recall {:.2f}%".format(c_flow_n / b_flow_n * 100))

    print(len(data_list))


# 保存模型
# os.path.join(model_dir, predict_model_pkl)
# joblib.dump(predict_model,predict_model_pkl)


if __name__ == '__main__':
    n = 1
    # for i in range(n):
    # save_model()

    # train_and_predict()
    # big_list = [0.05, 0.1, 0.2, 0.3]
    # big_list = [0.05]
    big_list = [0.1, 0.2, 0.3]

    for big_percent in big_list:
        print("processing b={}:".format(big_percent))
        data_name = "SB-F-202201051400"
        instances_dir = os.path.join(get_prj_root(), "./data/instances/" + data_name + "/" + str(big_percent) + "/")
        train_and_predict(instances_dir)

        data_name = "SB-F-202201021400"
        data_name = "SB-F-202201041400"
        test_instances_dir = os.path.join(get_prj_root(), "./data/instances/" + data_name + "/" + str(big_percent) + "/")
        # test_classify(test_instances_dir)
