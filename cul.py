from numpy import mean


def cul():
    pre = [0.0347,
0.0334,
0.0320,
0.0311,
0.0314,
0.0307,
0.0313,
0.0314,
0.0314,
0.0317]
    are = [0.4220,
0.4185,
0.3988,
0.3955,
0.3963,
0.3889,
0.3980,
0.4010,
0.3927,
0.4026]
    pre.sort()
    # pre = pre[1:-1]
    print(mean(pre))

    are.sort()
    are = are[1:-1]
    print(mean(are))

if __name__ == '__main__':
    cul()
    # print([0.2*x for x in range(1,6)])
