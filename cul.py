from numpy import mean


def cul():
    pre = [0.9312, 0.9581, 0.8909, 0.9069, 0.8725, 0.9453, 0.9359, 0.9608, 0.9565, 0.9368, ]
    are = [0.2928,0.2062,0.4093,0.3257,0.4426,0.2086,0.2440,0.1952,0.1945,0.2477]
    pre.sort()
    pre = pre[1:-1]
    print(mean(pre))

    are.sort()
    are = are[1:-1]
    print(mean(are))

if __name__ == '__main__':
    cul()
