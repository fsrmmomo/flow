"""
该文件用于读取解析xxx.pkts文件内的相关统计数据
便于流识别程序识别其准确性
"""
from statistics import mean, variance, median
import os
from typing import List
import numpy as np

from common_utils import load_json, debug

dirs = {
    "video": "./tmp/dt/video",
    "iot": "./tmp/dt/iot",
    "voip": "./tmp/dt/voip",
    "AR": "./tmp/dt/AR"
}
win_size = 10  # 窗口大小
limit = 100000


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
    if min(packet_interval_list) == -1:
        feature_list.append(0)
    else:
        feature_list.append(min(packet_interval_list))  # 最小值
    feature_list.append(max(packet_interval_list))  # 最大值
    feature_list.append(mean(packet_interval_list))  # 平均值
    feature_list.append(variance(packet_interval_list))  # 方差
    feature_list.append(median(packet_interval_list))  # 中位数

    # 返回结果的列表 第一个为特征 第二个为五元组 暂时只有传输协议
    res_list = []
    res_list.append(feature_list)
    flow_protocol[0] = "五元组 " + flow_protocol[0]
    res_list.append(flow_protocol)

    return res_list


def calc_data_list(path):
    """
    读取文件夹中的文件计算特征值然后生成multithread_client中的data_list文件
    用于测试识别的准确度
    """
    data_list = []
    # 找到文件名
    filename_list = get_filename(path)

    # 计算每个pkts文件的特征值
    for name in filename_list:
        temp_list = read_pkts(name)

        # 如果长度为0 直接下一次循环
        if len(temp_list) == 0:
            continue

        # 如果数据重复了 不添加
        if len(data_list) == 0:
            temp_list[1][0] = name + temp_list[1][0]  # 把文件名作为五元组
            data_list.append(temp_list)
        else:
            if temp_list[0] not in list(np.array(data_list).T[0]):
                # if temp_list not in data_list[0]:
                temp_list[1][0] = name + temp_list[1][0]  # 把文件名作为五元组
                data_list.append(temp_list)

    # 给data_list添加其他命令
    data_list.append("send")
    data_list.append("exit")
    data_list.append("send")
    data_list.append("send")

    # 将data_list保存为本地txt
    path = path + 'data_list.txt'
    with open(path, 'w') as f:
        f.write(str(data_list))
        f.close
    print(path, "文件解析成功！")


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
    return [features, [flow_name]]


def generate_feature(save_file_dir):
    # instances_dir = os.path.join(get_prj_root(), "classify/instances2")  # 修改：instances_dir实例的路径
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
        # print(instances)
        # 将目标解析后的数据保存到txt中
        with open(save_file_dir + flow_type + '_data_list.txt', 'w') as f:
            f.write(str(instances))
            f.close
        print(save_file_dir + flow_type + '_data_list.txt', "解析成功！")


if __name__ == "__main__":
    # path = './raw_data/AR/'
    # calc_data_list(path)
    save_file_dir = "./tmp/dt/"
    generate_feature(save_file_dir)
