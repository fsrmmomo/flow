import os
import pickle

import numpy as np
import matplotlib.pyplot as plt


def draw_precision_cmp():
    dir = "./result/"
    ts = [5, 10]
    ms = [512000, 1024000, 2048000]
    al = ['es', 'opt', 'sketch', 'test']
    al_dict = {}

    print(os.listdir(dir))
    for a in al:
        filename = dir + a + '_result.pkl'
        with open(filename, "rb") as f:
            al_dict[a] = pickle.load(f)
    print(al_dict)
    # for t in ts:
    #     for m in ms:
    for t in ts[:1]:
        al_precision = {}
        al_are = {}
        for a in al:
            tmplist = []
            for m in ms[1:2]:
                tmp = al_dict[a][t][m]
                pre_list = [x[1] for x in tmp]
                pre_list.sort()
                pre_list = pre_list[1:-1]
                avr = np.mean(pre_list)
                tmplist.append(avr)
            al_precision[a] = tmplist
        for k,v in al_precision.items():
            print(k)
            print(v)
        # print(al_precision)









if __name__ == '__main__':
    draw_precision_cmp()
    # dat_file_folder = "../../Data/result/"
    # x = [1, 200, 500, 1000, 2000, 5000, 10000, 20000]
    # y = [[] for i in range(len(x))]
    # for file in os.listdir(dat_file_folder):
    #     if file[-8:] == "slot.res":
    #         num = int(file[:-8])
    #         print("Process: ", dat_file_folder + file)
    #         with open(dat_file_folder + file, 'rb') as f:
    #             str = f.readline().split()
    #             i = x.index(num)
    #             y[i] = list(map(float, str))
    # y_real = []
    # for l in y:
    #     print(l)
    #     y_real.append(np.mean(l))
    # print(y_real)
    #
    # plt.figure()
    # plt.figure(figsize=(8, 6))
    # # 设置 x 和 y 轴标尺最大最小值
    # plt.xlim(1, 8.5)
    # plt.ylim(0.2, 1.8)
    # # 显示中文标签
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    #
    # plt.xticks(np.arange(1, 9, 1), x, rotation=0)
    # # plt.plot(x,y_real,'s-')
    # myx = [i + 1 for i in range(len(x))]
    # plt.plot(myx, y_real, 's-', label='Mem 600KB')
    #
    # # 设置标题
    # plt.title('ARE')
    #
    # # 设置 x 和 y 轴名称
    # plt.xlabel('窗口大小')
    # plt.ylabel('ARE对比')
    #
    # for x1, y1 in zip(myx, y_real):
    #     plt.text(x1, y1, '%.3f' % y1, fontdict={'fontsize': 14})
    #
    # y = [[] for i in range(len(x))]
    # for file in os.listdir(dat_file_folder):
    #     if file[-14:] == "slot_300KB.res":
    #         num = int(file[:-14])
    #         print("Process: ", dat_file_folder + file)
    #         with open(dat_file_folder + file, 'rb') as f:
    #             str = f.readline().split()
    #             i = x.index(num)
    #             y[i] = list(map(float, str))
    # y_real = []
    # for l in y:
    #     print(l)
    #     y_real.append(np.mean(l))
    # print(y_real)
    #
    # plt.plot(myx, y_real, 's-', label='Mem 300KB')
    # for x1, y1 in zip(myx, y_real):
    #     plt.text(x1, y1, '%.3f' % y1, fontdict={'fontsize': 14})
    #
    # plt.legend(loc='best')
    # plt.savefig("../../Data/figure/ARE_CMP.png")
    # plt.show()
