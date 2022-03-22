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

dirs = {
    "video": "./tmp/dt/video",
    "iot": "./tmp/dt/iot",
    "voip": "./tmp/dt/voip"
}
# pkts_dirs = {
#     "video": "./tmp/pkts/video",
#     "iot": "./tmp/pkts/iot",
#     "voip": "./tmp/pkts/voip"
# }

pkts_dirs = {
    "video": "./even/pkts/video",
    "iot": "./even/pkts/iot",
    "voip": "./even/pkts/voip"
}

win_size = 10  # 窗口大小
limit = 100000

Instance = namedtuple("Instance", ["features", "label", "id"])  # 实例


def to_int(str):
    """
    str转int
    """
    try:
        int(str)
        return int(str)
    except ValueError:  # 报类型错误，说明不是整型的
        try:
            float(str)  # 用这个来验证，是不是浮点字符串
            return int(float(str))
        except ValueError:  # 如果报错，说明即不是浮点，也不是int字符串。   是一个真正的字符串
            return False


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



        for f in f_list:
            # print(f)
            # feature = f[1][:5]
            feature = f[1][:7]
            feature.append(f[1][6] - f[1][5])
            feature.append(f[1][8] - f[1][7])
            feature.append(f[1][9])
            feature.append(f[1][10])
            feature.append(f[1][11])

            feature[0] /= all_bytes
            # feature[2] /= all_bytes
            # feature[3] /= all_bytes
            # feature[4] /= all_bytes
            feature[1] /= all_pkts
            feature[5] /= all_pkts
            feature[6] /= all_pkts
            feature[7] /= all_pkts

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


def read_pkl():
    wf = './data/feature/timeWin/SB-F-202201051400/0.05/'
    pre = '../../Data/feature/timeWin/SB-F-202201051400/'
    wname = wf + '0.pkl'

    with open(wname, 'rb') as f:
        f_list = pickle.load(f)
        # for i in f_list[:200]:
        sum = 0
        n_train = int(len(f_list) * 0.7)
        for i in f_list[n_train:]:
            if i[2] == 1:
                sum += 1

        print(sum)
    # wname = './data/instances/instance_0.pkl'
    # with open(wname, 'rb') as f:
    #     f_list = pickle.load(f)
    #     for i in f_list[:200]:
    #         print(i)


def generate_instance_pkl_by_feature_pkl():
    """
    读取所有的feature pkl，生成instance
    :return:
    """
    instances_dir = os.path.join(get_prj_root(), "./data/instances")  # 修改：instances_dir实例的路径
    pkl_dir = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201051400/0.05/")
    count_file = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201051400/count.pkl")
    pkl_dir = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201021400/0.05/")
    instances_dir = os.path.join(get_prj_root(), "./data/instances/test")  # 修改：instances_dir实例的路径
    count_file = os.path.join(get_prj_root(), "./data/feature/timeWin/SB-F-202201021400/count.pkl")

    # data_list = []
    # print(instances_dir)
    # big_percent = 0.2
    big_percent = 0.05

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


    for file in os.listdir(pkl_dir):
        if file[-3:] == "pkl":
        # if file == "0.pkl":
            instances = []
            # pass
            fname = pkl_dir + file
            print("load pkl:" + fname)
            instances = read_pkl_to_instance(filename=fname,big_dict=big_dict)
            print("{} 流的数量：{}".format(fname, len(instances)))

            save_file = "instance_" + file
            save_pkl(os.path.join(instances_dir, save_file), instances)


# def change_label

def generate_instances_pkl():
    """
    调用 read_pkts_generate_instances 读取每个pkts文件 生成instance 然后保存成pkl
    :return:
    """
    instances_dir = os.path.join(get_prj_root(), "./even/instances")  # 修改：instances_dir实例的路径
    for flow_type, dirname in pkts_dirs.items():
        instances = []
        pkts_list = glob.glob(dirname + "/*.pkts")  # 获取每个pkts文件
        print("parsing {} catalogue".format(dirname))
        print("{} pkts数量：{}".format(dirname, len(pkts_list)))
        for pkts in pkts_list:
            # instances = instances + read_pkts_generate_instances(filename=pkts, label=generate_label(flow_type))
            instances = instances + read_pkl_to_instance(filename=pkts)
            print("flow {} finished".format(pkts))
        print("{} 流的数量：{}".format(dirname, len(instances)))
        print(instances)
        save_pkl(os.path.join(instances_dir, "{}.pkl".format(flow_type)), instances)  # 保存Python内存数据到文件


def generate_label(flow_type):
    """
    将video iot voip 分别改为0 1 2
    :param flow_type:
    :return:
    """
    if flow_type == 'video':
        return 0
    if flow_type == 'iot':
        return 1
    if flow_type == 'voip':
        return 2


def calc_data_list(path):
    """
    读取文件夹中的文件计算特征值然后生成 multithread_client中的data_list文件
    用于测试识别的准确度
    """
    data_list = []
    # 找到文件名
    filename_list = get_filename(path)

    # 计算每个pkts文件的特征值
    for name in filename_list:
        temp_list = read_pkts(name)
        if len(temp_list) == 0:
            continue
        # temp_list[1][0] = name + temp_list[1][0] # 把文件名作为五元组
        if temp_list not in data_list:
            data_list.append(temp_list)

    """
    # 给data_list添加其他命令
    data_list.append("hhhh")
    data_list.append("exit")
    data_list.append("send")
    data_list.append("send")
    """

    # 将data_list保存为本地txt
    path = path + 'data_list.txt'
    with open(path, 'w') as f:
        f.write(str(data_list))
        f.close
    print(path, "文件解析成功！")

    return data_list


def get_median(data):  # 产生中位数
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2


def gen_single_feature(dirname, flow, flow_type):
    # debug("generate {}".format(flow["file"]))
    def extract_features(raw_features: List[float]):  # 修改特征
        extracted_features = []
        raw_features = [r for r in raw_features if int(r) >= 0]

        extracted_features.append(min(raw_features))
        extracted_features.append(max(raw_features))
        extracted_features.append(sum(raw_features) / len(raw_features))
        extracted_features.append(np.std(raw_features))  # 标准差
        extracted_features.append(get_median(raw_features))
        return extracted_features

    features = []
    idts = []
    ps = []
    idt_file = os.path.join(dirname, flow["idt"])  # 包大小
    ps_file = os.path.join(dirname, flow["ps"])  # 包间隔
    with open(idt_file, 'r') as fp:
        lines = fp.readlines()
        fp.close()
    lines = [l.strip() for l in lines]  # .strip()用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列。

    lines = [l for l in lines if len(l) > -1]
    if len(lines) > win_size:
        lines = lines[:win_size]
    else:
        return
    for l in lines:
        idts.append(float(l))

    with open(ps_file, "r") as fp:
        lines = fp.readlines()
        fp.close()

    lines = [l.strip() for l in lines]
    lines = [l for l in lines if len(l) > 0]
    if len(lines) > win_size:
        lines = lines[:win_size]
    else:
        return
    for l in lines:
        ps.append(float(l))

    # 有很奇怪的现象
    ps = [p for p in ps if p > 0]
    if len(ps) == 0:
        print(flow["ps"])
        return None
    idts = [i for i in idts if i >= 0]
    if len(idts) == 0:
        return None

    features.extend(extract_features(ps))  # 包间隔的数理统计
    features.extend(extract_features(idts))  # 包大小的数理统计

    flow_name = flow["ps"][:-3] + "_" + flow_type
    return [features, flow_name]


def generate_feature(file_path):
    instances_dir = os.path.join(file_path, "classify/instances2")  # 修改：instances_dir实例的路径
    for flow_type, dirname in dirs.items():
        stats_fn = os.path.join(dirname, "statistics.json")  # statistics.json流量统计的文件
        debug(stats_fn)
        statistics = load_json(os.path.join(dirname, "statistics.json"))
        debug("#flows {}".format(statistics["count"]))
        flows: List = statistics["flows"]
        sorted(flows, key=lambda f: -f["num_pkt"])
        if len(flows) > limit:
            flows = flows[:limit]
        instances = [gen_single_feature(dirname, f, flow_type) for f in flows]
        instances = [i for i in instances if i is not None]
        debug("#{} instances {}".format(flow_type, len(instances)))
        print(instances)
        # 将目标解析后的数据保存到txt中
        file_path = file_path + 'data_list.txt'
        with open(file_path, 'w') as f:
            f.write(str(instances))
            f.close
        print(file_path, "文件解析成功！")


def deal(path, wait_saving_list):
    """
    将二维的list存储到xls中
    :return: null
    """
    # list转dataframe
    df = pd.DataFrame(wait_saving_list, columns=['包大小-最小值', '包大小-最大值', '包大小-平均值', '包大小-方差', '包大小-中位数'
        , '包间隔-最小值', '包间隔-最大值', '包间隔-平均值', '包间隔-方差', '包间隔-中位数', '标签'])

    # 保存到本地excel
    path = path + 'feature.xlsx'
    df.to_excel(path, index=False)


def write_xls(path, wait_saving_lsit):
    path = path + 'feature.xls'
    output = open(path, 'w', encoding='gbk')
    output.write('包大小-最小值\t包大小-最大值\t包大小-平均值\t包大小-方差\t包大小-中位数\t包间隔-最小值\t包间隔-最大值\t包间隔-平均值\t包间隔-方差\t包间隔-中位数\t标签\n')
    for i in range(len(wait_saving_lsit)):
        for j in range(len(wait_saving_lsit[i])):
            output.write(str(wait_saving_lsit[i][j]))  # write函数不能写int类型的参数，所以使用str()转化
            output.write('\t')  # 相当于Tab一下，换一个单元格
        output.write('\n')  # 写完一行立马换行
    output.close()


if __name__ == "__main__":
    # path = './raw_data/iot/'
    # # path = './raw_data/voip/'
    #
    # wait_saving_list = calc_data_list(path)
    #
    # deal(path, wait_saving_list)

    # generate_instances_pkl()
    # read_pkl()
    generate_instance_pkl_by_feature_pkl()
    # read_pkts_generate_instances(filename="./tmp/pkts/video/Vimeo_Workstation.pkts", label='video')
