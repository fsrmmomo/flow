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

import pickle

start = time.time()  # 计算时间

random.seed(datetime.now())
# model_dir = os.path.join(get_prj_root(), "classify/model_predict") #修改：模型model文件夹路径
# predict_model_pkl = os.path.join(model_dir, "dt3_1_9.pkl") #修改：模型的版本，只用修改此处就行

Instance = namedtuple("Instance", ["features", "label"])  # 实例

dirs = {
    "video": "./tmp/dt/video",
    "iot": "./tmp/dt/iot",
    "car": "./tmp/dt/car",
}
# instances_dir = os.path.join(get_prj_root(), "./classify/instances2")  # 修改：instances路径
instances_dir = os.path.join(get_prj_root(), "./even/instances")  # 修改：instances路径
# instances_dir = os.path.join(get_prj_root(), "./feature/timeWin/SB-F-202201051400/0.05/")  # 修改：instances路径


def train_and_predict():
    # data_list = []
    # print(instances_dir)
    # for file in os.listdir(instances_dir):
    #     if file[-3:] == "pkl":
    #         # pass
    #         print("load pkl:" + instances_dir +file)
    #         data_list.append(load_pkl(instances_dir+file))


    iot = load_pkl(os.path.join(instances_dir, "iot.pkl"))  # 不同实例的pkl是不同特征的
    print(iot)
    print(type(iot[0]))
    videos = load_pkl(os.path.join(instances_dir, "video.pkl"))
    car = load_pkl(os.path.join(instances_dir, "voip.pkl"))
    for i in videos:
        assert i.label == 0
    for i in iot:
        assert i.label == 1
    for i in car:
        assert i.label == 2

    debug("# iot instances {}".format(len(iot)))
    debug("# video instances {}".format(len(videos)))
    debug("# car instances {}".format(len(car)))

    random.shuffle(car)  # 打乱排序
    random.shuffle(iot)
    random.shuffle(videos)

    n_video_train = int(len(videos) * 0.7)
    n_video_test = len(videos) - n_video_train

    video_train = videos[:n_video_train]
    # video_test = videos[len(videos) - int(n_video_test * 1):]
    video_test = videos[len(videos) - 100:]

    iot_train = iot[:n_video_train]
    # iot_test = iot[len(iot) - int(n_video_test * 1):]
    iot_test = iot[len(iot) - 100:]

    car_train = car[:n_video_train]
    # car_test = car[len(car)-int(n_video_test * 1):]
    car_test = car[len(car) - 100:]

    print("##########################")
    print("#video train {}".format(len(video_train)))
    print("#iot train {}".format(len(iot_train)))
    print("#car train {}".format(len(car_train)))
    print("##########################")

    debug("# video test instances {}".format(len(videos) - len(video_train)))
    debug("# iot test instances {}".format(len(iot) - len(iot_train)))
    debug("# car test instances {}".format(len(car) - len(car_train)))

    train = []
    train.extend(iot_train)
    train.extend(video_train)
    train.extend(car_train)
    random.shuffle(train)

    train_x = [x.features for x in train]
    train_y = [x.label for x in train]

    dt_min = []
    dt_max = []
    dt_mean = []
    dt_f = []
    ps_min = []
    ps_max = []
    ps_mean = []
    ps_f = []
    train_y_name = []
    for i in range(len(train_x)):
        dt_min.append(train_x[i][4])
        dt_max.append(train_x[i][5])
        dt_mean.append(train_x[i][6])
        dt_f.append(train_x[i][7])
        ps_min.append(train_x[i][0])
        ps_max.append(train_x[i][1])
        ps_mean.append(train_x[i][2])
        ps_f.append(train_x[i][3])
    for i in train_y:
        if i == 0:
            train_y_name.append(" ")
        if i == 1:
            train_y_name.append("IOT")
        if i == 2:
            train_y_name.append("VOIP")
    # list = {'包间隔最小值': dt_min, '包间隔最大值': dt_max, '包间隔平均值': dt_mean, '包间隔方差': dt_f,
    # 		'包大小最小值': ps_min, '包大小最大值': ps_max, '包大小平均值': ps_mean, '包大小方差': ps_f, '类别': train_y_name}
    # dataframe = pd.DataFrame(list)
    # # print(dataframe)
    # dataframe.to_excel('./data_train.xlsx', index=False)
    # info('打印训练集')

    test = []

    print("#video test {}".format(len(video_test)))
    print("#iot test {}".format(len(iot_test)))
    print("#car test {}".format(len(car_test)))
    print("##########################")

    test.extend(video_test)
    test.extend(iot_test)
    test.extend(car_test)
    random.shuffle(test)

    test_x = [t.features for t in test]
    test_y = [t.label for t in test]
    # print(test_x)
    dt_min = []
    dt_max = []
    dt_mean = []
    dt_f = []
    ps_min = []
    ps_max = []
    ps_mean = []
    ps_f = []
    test_y_name = []
    for i in range(len(test_x)):
        dt_min.append(test_x[i][4])
        dt_max.append(test_x[i][5])
        dt_mean.append(test_x[i][6])
        dt_f.append(test_x[i][7])
        ps_min.append(test_x[i][0])
        ps_max.append(test_x[i][1])
        ps_mean.append(test_x[i][2])
        ps_f.append(test_x[i][3])
    for i in test_y:
        if i == 0:
            test_y_name.append("VIDEO")
        if i == 1:
            test_y_name.append("IOT")
        if i == 2:
            test_y_name.append("VOIP")

    # list_test = {'包间隔最小值': dt_min, '包间隔最大值': dt_max, '包间隔平均值': dt_mean, '包间隔方差': dt_f,
    # 		'包大小最小值': ps_min, '包大小最大值': ps_max, '包大小平均值': ps_mean, '包大小方差': ps_f, '类别': test_y_name}
    # dataframe = pd.DataFrame(list_test)
    # # print(dataframe)
    # dataframe.to_excel('./data_test.xlsx', index=False)
    # info('打印测试集')

    # 训练以及预测
    predict_model = RandomForestClassifier(n_jobs=-1)  # 引入训练方法
    predict_model.fit(train_x, train_y)  # 对训练数据进行拟合

    with open("./even/model/random_forest.pkl", "wb") as fp:
        cPickle.dump(predict_model, fp)
        fp.close()
    predicts = predict_model.predict(test_x)

    with open("./even/model/random_forest.pkl", "rb") as fp:
        try:
            predict_model = cPickle.load(fp)
        except EOFError:
            print("模型为空")
    predicts = predict_model.predict(test_x)
    pre_y_name = []
    for i in predicts:
        if i == 0:
            pre_y_name.append("video")
        if i == 1:
            pre_y_name.append("iot")
        if i == 2:
            pre_y_name.append("voip")
    list_pre = {'包间隔最小值': dt_min, '包间隔最大值': dt_max, '包间隔平均值': dt_mean, '包间隔方差': dt_f,
                '包大小最小值': ps_min, '包大小最大值': ps_max, '包大小平均值': ps_mean, '包大小方差': ps_f, '类别': pre_y_name}
    # dataframe = pd.DataFrame(list_pre)
    # print(dataframe)
    # with pd.ExcelWriter('./data_pre.xlsx') as writer:
    # 	dataframe.to_excel(writer,sheet_name='预测数据', index=False)

    # 评价模型
    count = 0
    count0 = 0
    count1 = 0
    count2 = 0
    for idx in range(len(test_x)):
        if int(predicts[idx]) == int(test_y[idx]):
            count += 1
            if int(predicts[idx]) == 0:
                count0 += 1
            if int(predicts[idx]) == 1:
                count1 += 1
            if int(predicts[idx]) == 2:
                count2 += 1
    '''                
    print("#video Accuracy {:.2f}%".format(count0 / len(video_test) *100))
    print("#iot Accuracy {:.2f}%".format(count1 / len(iot_test)*100))
    print("#car Accuracy {:.2f}%".format(count2 / len(car_test)*100))
    print("#AR Accuracy {:.2f}%".format(count3 / len(AR_test)*100))
    print("ALL Accuracy {:.2f}%".format(count / len(test_x)*100))
    print("##########################")
    '''
    return (count0 / len(video_test) * 100), (count1 / len(iot_test) * 100), (count2 / len(car_test) * 100), \
           (count / len(test_x) * 100), len(video_test), len(iot_test), len(car_test), list_pre


def classify_flows(mode: 'int', predict_flow):
    """
    该函数用于训练模型并且测试模型的准确度 或者 预测结果
    :param mode: 0--训练模型    1--预测和分类流并返回
    :param predict_dir: 待预测的流的目录下的pkl文件
    :return: 待分类的流的分类结果列表
    """
    # 判断是只训练模型 还是 只是预测结果
    if mode == 0:
        # 此时训练使用数据训练模型 并且 保存模型 评价模型
        times = 10
        sum_predict = 0
        for _ in range(times):
            res = train_and_predict()
            sum_predict = sum_predict + res
        print("模型准确率为:", sum_predict / times)
    else:
        # 使用传递的文件来预测结果并且返回
        # predict = load_pkl(os.path.join(predict_dir, "predict2.pkl"))
        with open("./random_forest.pkl", "rb") as fp:
            try:
                predict_model = cPickle.load(fp)
            except EOFError:
                print("模型为空")

        # test = json.loads(predict_flow)
        # info("#video test {}".format(len(predict)))
        #
        # test.extend(predict)
        # # random.shuffle(test)

        test_x = [t[:-1] for t in predict_flow]

        predict_result = predict_model.predict(test_x)
        res_list = identify_classification(predict_result)
        return res_list


def identify_classification(predict_result):
    """
    该函数将分类结果的标签转换为具体内容字符串的结果
    :param predict_result:标签分类结果
    :return: 字符串分类结果
    """
    res_list = []
    for label in predict_result:
        if label == 0:
            res_list.append("videos")
        elif label == 1:
            res_list.append("iot")
        elif label == 2:
            res_list.append("voip")
        elif label == 3:
            res_list.append("AR")
    return res_list


# 保存模型
# os.path.join(model_dir, predict_model_pkl)
# joblib.dump(predict_model,predict_model_pkl)


if __name__ == '__main__':
    n = 10
    count0 = 0
    count1 = 0
    count2 = 0
    count4 = 0
    for i in range(n):
        count00, count11, count22, count44, num_video, num_iot, num_car, list_pre = train_and_predict()
        count0 = count0 + count00
        count1 = count1 + count11
        count2 = count2 + count22
        count4 = count4 + count44
    print("video {:.2f}%".format(count0 / n))
    print("--------------------------")
    print("iot {:.2f}%".format(count1 / n))
    print("--------------------------")
    print("car {:.2f}%".format(count2 / n))
    print("--------------------------")
    print("ALL {:.2f}%".format(count4 / n))
    print("##########################")
    # print(predict_sum / n)

    list_result = {'VIDEO个数': [num_video], 'IOT个数': [num_iot], '车载网个数': [num_car],
                   '准确率': [str(round((count4 / n), 2)) + "%"]}
    dataframe1 = pd.DataFrame(list_pre)
    # print(dataframe1)
    dataframe2 = pd.DataFrame(list_result)
    # print(dataframe2)

    writer = pd.ExcelWriter('./data_pre.xlsx')
    dataframe1.to_excel(writer, sheet_name='预测数据', index=False)
    dataframe2.to_excel(writer, sheet_name='预测结果', index=False)
    writer.save()
    info('打印预测结果')

    end = time.time()
    print("模型测试次数：{}次".format(n))
    print("程序运行时间:%.2f秒" % (end - start)) \
 \
    # predict_flow = [
    #     [4, 819, 248.5, 154985.83333333334, 4.0, 0, 121355855104, 89990397798.3, 1.9039464108892084e+21, 121207225984.0,
    #      'iot'], [90, 218, 102.8, 1638.4, 90.0, 0, 1035015168, 712070399.9, 1.6883848979054346e+17, 944033024.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 2981932800, 1124691481.5, 5.3135012046579494e+17, 1031028480.0, 'iot'],
    #     [90, 218, 102.8, 1638.4, 90.0, 0, 1036396800, 812630399.9, 1.4267351388782602e+17, 1024595968.0, 'iot'],
    #     [90, 218, 102.8, 1638.4, 90.0, 0, 1538089984, 918660505.5, 1.6118634021447776e+17, 1031232512.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 3015629056, 1230884198.3, 6.089420008331529e+17, 1039953920.0, 'iot'],
    #     [90, 106, 91.6, 25.599999999999998, 90.0, 0, 1079034112, 844081407.9, 1.5343089565782886e+17, 1036454528.0,
    #      'iot'], [90, 90, 90, 0, 90.0, 0, 1073283840, 812402611.1, 1.2544851750637958e+17, 969145728.0, 'iot'],
    #     [149, 149, 149, 0, 149.0, 0, 27035812864, 24324518783.9, 7.304720023549811e+19, 27026965120.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 1965510912, 1123028684.7, 3.029359003511446e+17, 1041307008.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 1049880064, 919384089.5, 1.0576039759409808e+17, 1028683520.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 2072202752, 1115677004.7, 3.2641283941382995e+17, 1034001536.0, 'iot'],
    #     [159, 159, 159, 0, 159.0, 0, 27026612992, 24323015219.1, 7.303815738290249e+19, 27025640064.0, 'iot'],
    #     [1, 85, 23, 1273.7777777777778, 1.0, 0, 10215960064, 7702443699.1, 1.5230131562256531e+19, 10203353600.0,
    #      'iot'],
    #     [90, 106, 91.6, 25.599999999999998, 90.0, 0, 1961534976, 1019949388.7, 3.549228106421989e+17, 1030261504.0,
    #      'iot'],
    #     [90, 106, 91.6, 25.599999999999998, 90.0, 0, 1038351104, 814336435.1, 1.445110595346008e+17, 1027354112.0,
    #      'iot'], [90, 90, 90, 0, 90.0, 0, 3098483968, 1327910195.1, 7.074504846600379e+17, 1031787008.0, 'iot'],
    #     [90, 218, 104.4, 1618.4888888888888, 90.0, 0, 1042714112, 721452492.7, 1.7457642025826227e+17, 1021771392.0,
    #      'iot'],
    #     [90, 308, 113.4, 4700.488888888889, 90.0, 0, 2062443776, 1020062668.7, 4.384568957570431e+17, 1031896960.0,
    #      'iot'],
    #     [90, 218, 102.8, 1638.4, 90.0, 0, 2063992064, 1072039398.3, 3.801795241674229e+17, 1028590592.0, 'iot'],
    #     [1, 85, 24.6, 1462.9333333333334, 1.0, 0, 10233620224, 8459930598.3, 1.1238713093370497e+19, 10203511424.0,
    #      'iot'], [90, 90, 90, 0, 90.0, 0, 2056805120, 1019053286.3, 2.363579215952823e+17, 1027779328.0, 'iot'],
    #     [90, 218, 102.8, 1638.4, 90.0, 0, 2068697856, 1327932236.7, 5.441113328540085e+17, 1239569024.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 1047502080, 918024883.1, 1.0544869563890253e+17, 1030896896.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 1040857856, 919063295.9, 1.0551365944328254e+17, 1031879040.0, 'iot'],
    #     [90, 90, 90, 0, 90.0, 0, 1929675008, 1024005887.9, 2.0795474143661392e+17, 1039242112.0, 'iot'],
    #     [69, 357, 205, 20664.88888888889, 197.0, 0, 10048967168, 4975506585.5, 2.7437347519321244e+19, 4870326528.0,
    #      'iot']]
    #
    # res_list = classify_flows(mode=1, predict_flow=predict_flow)
    # print(res_list)
