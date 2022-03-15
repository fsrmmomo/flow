"""
10个特征的（前五个包大小，后五个包间隔）：最小值，最大值，平均值，方差，中位数
每次运行前，检查：
四个需要修改的地方，命名是否正确
最后的运行模式是否正确
"""
from common_utils import *  # 修改了
from argparse import ArgumentParser
from collections import namedtuple
from typing import List, Dict
from path_utils import get_prj_root
from model import DT  # 修改了
from datetime import datetime
from path_utils import get_prj_root
import numpy as np
from sklearn.decomposition import PCA
import time

start = time.time()

random.seed(datetime.now())
model_dir = os.path.join(get_prj_root(), "classify/models2")  # 修改：模型models路径
dt_model_pkl = os.path.join(model_dir, "dt10.pkl")  # 修改：模型的版本，只用修改此处就行

Instance = namedtuple("Instance", ["features", "label"])  # 实例

win_size = 10  # 窗口大小
limit = 100000

dirs = {
    "video": "./tmp/dt/video",
    "iot": "./tmp/dt/iot",
    "voip": "./tmp/dt/voip",
    "AR": "./tmp/dt/AR"
}
instances_dir = os.path.join(get_prj_root(), "classify/instances2")  # 修改：instances路径

"""
def get_median(data: List[float]): #产生中位数
	data = sorted(data)
	size = len(data)
	if size % 2 == 0: # 判断列表长度为偶数
		median = (data[size//2]+data[size//2-1])/2
		data[0] = median
	if size % 2 == 1: # 判断列表长度为奇数
		median = data[(size-1)//2]
		data[0] = median
	return data[0]
    #采用新的那个可能更省时间
"""


def get_median(data):  # 产生中位数
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2


def gen_single_instance(dirname, flow, flow_type):
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
    if flow_type == "video":
        label = 0
    elif flow_type == "iot":
        label = 1
    elif flow_type == "voip":
        label = 2
    elif flow_type == "AR":
        label = 3
    else:
        err("Unsupported flow type")
        raise Exception("Unsupported flow type")
    return Instance(features=features, label=label)


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


def generate():
    instances_dir = os.path.join(get_prj_root(), "classify/instances2")  # 修改：instances_dir实例的路径
    for flow_type, dirname in dirs.items():
        stats_fn = os.path.join(dirname, "statistics.json")  # statistics.json流量统计的文件
        debug(stats_fn)
        statistics = load_json(os.path.join(dirname, "statistics.json"))
        debug("#flows {}".format(statistics["count"]))
        flows: List = statistics["flows"]
        sorted(flows, key=lambda f: -f["num_pkt"])
        if len(flows) > limit:
            flows = flows[:limit]
        instances = [gen_single_instance(dirname, f, flow_type) for f in flows]
        instances = [i for i in instances if i is not None]
        debug("#{} instances {}".format(flow_type, len(instances)))
        #print(instances)
        save_pkl(os.path.join(instances_dir, "{}.pkl".format(flow_type)), instances)  # 保存Python内存数据到文件


def generate_feature():
    instances_dir = os.path.join(get_prj_root(), "classify/instances2")  # 修改：instances_dir实例的路径
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
        # # 将目标解析后的数据保存到txt中
        # file_path = file_path + 'data_list.txt'
        # with open(file_path, 'w') as f:
        #     f.write(str(instances))
        #     f.close
        # print(file_path, "文件解析成功！")
        save_pkl(os.path.join(instances_dir, "{}.pkl".format(flow_type)), instances)  # 保存Python内存数据到文件


def train_and_predict():
    iot = load_pkl(os.path.join(instances_dir, "iot.pkl"))
    videos = load_pkl(os.path.join(instances_dir, "video.pkl"))
    voip = load_pkl(os.path.join(instances_dir, "voip.pkl"))
    AR = load_pkl(os.path.join(instances_dir, "AR.pkl"))
    for i in videos:
        assert i.label == 0
    for i in iot:
        assert i.label == 1
    for i in voip:
        assert i.label == 2
    for i in AR:
        assert i.label == 3

    debug("# iot instances {}".format(len(iot)))
    debug("# video instances {}".format(len(videos)))

    random.shuffle(voip)  # 打乱排序
    random.shuffle(iot)
    random.shuffle(videos)
    random.shuffle(AR)

    n_video_train = int(len(videos) * 0.7)
    n_video_test = len(videos) - n_video_train

    video_train = videos[:n_video_train]
    video_test = videos[n_video_train:]

    iot_train = iot[:n_video_train]
    iot_test = iot[len(iot) - len(video_test):]

    voip_train = voip[:n_video_train]
    voip_test = voip[len(voip) - len(video_test):]

    AR_train = AR[:n_video_train]
    AR_test = AR[len(AR) - len(video_test):]

    info("#video train {}".format(len(video_train)))
    info("#iot train {}".format(len(iot_train)))
    info("#voip train {}".format(len(voip_train)))
    info("#AR train {}".format(len(AR_train)))

    train = []
    train.extend(iot_train)
    train.extend(video_train)
    train.extend(voip_train)
    train.extend(AR_train)
    random.shuffle(train)

    train_x = [x.features for x in train]
    train_y = [x.label for x in train]

    # test 1:1
    test = []

    info("#video test {}".format(len(video_test)))
    info("#iot test {}".format(len(iot_test)))
    info("#voip test {}".format(len(voip_test)))
    info("#AR test {}".format(len(AR_test)))

    test.extend(video_test)
    test.extend(iot_test)
    test.extend(voip_test)
    test.extend(AR_test)
    random.shuffle(test)

    test_x = [t.features for t in test]
    test_y = [t.label for t in test]

    # #PCA降维
    # pca = PCA(n_components=8).fit(train_x)  # n_components设置降维到n维度
    # train_x = pca.transform(train_x) # 将规则应用于训练集
    # test_x = pca.transform(test_x)  # 将规则应用于测试集

    # 训练以及预测
    dt = DT()
    dt.fit((train_x, train_y))
    predicts = dt.predict(test_x)

    # 评价
    count = 0
    for idx in range(len(test_x)):
        if int(predicts[idx]) == int(test_y[idx]):
            count += 1
    print(count / len(test_x))
    dt.save_model(dt_model_pkl)  # 储存模型


if __name__ == '__main__':
    parser = ArgumentParser()
    print("running mode\n"
          "1. generate instances\n"
          "2. train dt\n")
    parser.add_argument("--mode", type=int, default=1)  # default为模式修改
    args = parser.parse_args()
    mode = int(args.mode)
    # mode = 1
    if mode == 1:
        # generate()
        generate_feature()
    elif mode == 2:
        train_and_predict()
    end = time.time()
    print("程序运行时间:%.2f秒" % (end - start))
