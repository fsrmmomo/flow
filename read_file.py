"""
该文件用于读取解析xxx.pkts文件内的相关统计数据
便于流识别程序识别其准确性
"""
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

Instance = namedtuple("Instance", ["features", "label"])  # 实例

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


def read_pkts(filename):
    """
    解析pkts文件内容
    """
    # 定义列表保存前10个包的大小和包间隔
    packet_size_list = []
    packet_interval_list = []
    # 保存流编号和传输协议
    flow_no = ''
    flow_protocol = []
    # 将第一行的流编号
    with open(filename, 'r') as f:
        flow_no = f.readline().split()[3]
        flow_protocol.append(f.readline().split()[2])
        f.close()

    # 找到同一个流的前10个包的包大小和包间隔
    with open(filename, 'r') as f:
        for line in f.readlines():
            # 找到流编号相同的
            if flow_no == line.split()[3]:
                packet_size_list.append(int(line.split()[1]))
                packet_interval_list.append(to_int(line.split()[4]))
            # 有10个数据 退出
            if len(packet_size_list) == 10:
                break
        f.close()
    if len(packet_size_list) < 10:
        return []

    # 计算特征值 (前五个包大小，后五个包间隔）：最小值，最大值，平均值，方差，中位数
    feature_list = []
    # 计算前10个包大小的5个特征值
    feature_list.append(min(packet_size_list))  # 最小值
    feature_list.append(max(packet_size_list))  # 最大值
    feature_list.append(mean(packet_size_list))  # 平均值
    feature_list.append(variance(packet_size_list))  # 方差
    feature_list.append(median(packet_size_list))  # 中位数
    # 计算前10个包间隔的5个特征值
    packet_interval_list.remove(-1)
    feature_list.append(min(packet_interval_list))  # 最小值
    feature_list.append(max(packet_interval_list))  # 最大值
    feature_list.append(mean(packet_interval_list))  # 平均值
    feature_list.append(variance(packet_interval_list))  # 方差
    feature_list.append(median(packet_interval_list))  # 中位数

    feature_list.append('iot')  # label
    # feature_list.append('voip')  # label

    # 返回结果的列表 第一个为特征 第二个为五元组 暂时只有传输协议
    res_list = []
    res_list.append(feature_list)
    flow_protocol[0] = "五元组 " + flow_protocol[0]
    res_list.append(flow_protocol)

    return feature_list


def read_pkts_generate_instances(filename, label):
    """
    解析pkts文件内容 然后生成可以训练的带标签的数据 训练模型
    """
    # 取出该文件中不同的流的编号
    flow_id_list = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            flow_no = line.split()[3]
            if flow_no not in flow_id_list:
                flow_id_list.append(flow_no)

    # 定义列表保存流的大小和间隔
    flow_size_list = []
    flow_interval_list = []
    # 每个不同的流取前十个包的数据
    for flow_no in flow_id_list:
        # 定义列表保存包的大小和包间隔
        packet_size_list = []
        packet_interval_list = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                # 找到流编号相同的
                if flow_no == line.split()[3]:
                    packet_size_list.append(int(line.split()[1]))
                    packet_interval_list.append(to_int(line.split()[4]))
                # 有10个数据 退出
                if len(packet_size_list) == 10:
                    break
            f.close()
        flow_size_list.append(packet_size_list)
        flow_interval_list.append(packet_interval_list)

    # 将小于10个包的流舍弃掉
    for i in range(len(flow_size_list)):
        if len(flow_size_list[i]) < 10:
            flow_size_list.remove(flow_size_list[i])
            flow_interval_list.remove(flow_interval_list[i])
    # 计算特征值 (前五个包大小，后五个包间隔）：最小值，最大值，平均值，方差，中位数
    feature_list = []
    for i in range(len(flow_size_list)):
        tmp_list = []
        # 计算前10个包大小的5个特征值
        tmp_list.append(min(flow_size_list[i]))  # 最小值
        tmp_list.append(max(flow_size_list[i]))  # 最大值
        tmp_list.append(mean(flow_size_list[i]))  # 平均值
        tmp_list.append(variance(flow_size_list[i]))  # 方差
        tmp_list.append(median(flow_size_list[i]))  # 中位数
        # 计算前10个包间隔的5个特征值
        # 将-1去掉
        flow_interval_list[i].remove(-1)
        tmp_list.append(min(flow_interval_list[i]))  # 最小值
        tmp_list.append(max(flow_interval_list[i]))  # 最大值
        tmp_list.append(mean(flow_interval_list[i]))  # 平均值
        tmp_list.append(variance(flow_interval_list[i]))  # 方差
        tmp_list.append(median(flow_interval_list[i]))  # 中位数

        # 添加标签
        one_flow_feature = Instance(features=tmp_list, label=label)
        feature_list.append(one_flow_feature)

    return feature_list


def generate_instances_pkl():
    """
    调用 read_pkts_generate_instances 读取每个pkts文件 生成instance 然后保存成pkl
    :return:
    """
    instances_dir = os.path.join(get_prj_root(), "./even/instances")  # 修改：instances_dir实例的路径
    for flow_type, dirname in pkts_dirs.items():
        instances = []
        pkts_list = glob.glob(dirname + "/*.pkts") # 获取每个pkts文件
        print("parsing {} catalogue".format(dirname))
        print("{} pkts数量：{}".format(dirname, len(pkts_list)))
        for pkts in pkts_list:
            instances = instances + read_pkts_generate_instances(filename=pkts, label=generate_label(flow_type))
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

    generate_instances_pkl()
    # read_pkts_generate_instances(filename="./tmp/pkts/video/Vimeo_Workstation.pkts", label='video')
