import random
import math
#import numpy as np
import matplotlib.pyplot as plt
#from statistics import mean
from copy import deepcopy
from tqdm import *


type = 1 #0=小规模；1=中规模；2=大规模
if type == 0:
    station = 1     #充电站数目
    customer = 10   #客户数目
    n_car = 2       #电动车数目
    popsize = 100   #种群规模
    genmax = 100    #迭代次数
    pop = 2         #精英选择
    pc = 0.8        #交叉概率
    pm = 0.1        #变异概率
elif type == 1:
    station = 2
    customer = 25
    n_car = 3
    popsize = 100
    genmax = 5000
    pop = 2
    pc = 0.9
    pm = 0.1
else:
    station = 8
    customer = 70
    n_car = 5
    popsize = 200
    genmax = 500
    pop = 4
    pc = 0.8
    pm = 0.1

speed = 40      #速度 km/h
Q = 35        #电池容量 kwh
cost_e = 1      #充电成本 1元每度
cost_d = 5      #运输成本 5元/km
H = 0.2        #耗电系数kwh/km
h = 5          #1kwh可以行驶的路程 km
pun_e = 20      #早到惩罚
pun_l = 30      #迟到惩罚
dis = 175    #续航里程 km dis = Q / H
Weight = 5      #载重量 t

#X,Y分别代表横纵坐标
#N代表客户需要运输的重量
#T_e是客户可以接受的早到时间
#T_l是客户可以接受的晚到时间
#T_s是客户的服务时间
X_pos = [50, 10, 58, 97, 88, 18, 21, 32, 63, 41, 120, 73, 87, 29, 44, 79, 47, 5, 98, 97, 45, 3, 26, 65, 82, 91, 85, 29]
Y_pos = [50, 25, 8, 45, 25, 33, 90, 59, 100, 66, 49, 10, 99, 30, 31, 60, 25, 56, 15, 87, 99, 10, 71, 83, 41, 76, 55, 39]
N =  [0,0.2,0.3,0.7,0.7,0.4,0.7,0.1,0.2,0.3,0.4,0.8,0.1,0.5,0.2,0.4,0.4,0.5,0.3,0.9,0.1,0.7,0.4,0.6,0.8,0.6,0,0]
T_e = [0,1,4,7,5,0,2,6,4,0,3,5,3,1,0,0,5,8,8,6,7,8,7,6,5,5,0,0]
T_l = [100,3,6,11,6,2,4,10,6,2,4,7,5,3,3,1,7,9,10,8,8,10,9,7,6,8,100,100]
T_s = [0,0.1,0.2,0.6,0.8,0.2,0.4,0.5,0.4,0.2,0.2,0.1,0.6,0.5,0.3,0.1,0.3,0.3,0.2,0.7,0.4,0.5,0.4,0.1,0.3,0.5,0.4,0.4]

#贪婪匹配
#X_new = []
#Y_new = []

# X_new.append(X[0])
# Y_new.append(Y[0])
#
# for i in range(0, len(X)-1):
#     i = 0
#     if X == []:
#         break
#     min_dis = 1000000
#     min_pos = i+1
#     for j in range(i+1, len(X)):
#         Dist = math.sqrt(((X[i] - X[j]) ** 2) + ((Y[i] - Y[j]) ** 2))
#         if Dist < min_dis:
#             min_dis = Dist
#             min_pos = j
#     X_new.append(X[min_pos])
#     Y_new.append(Y[min_pos])
#     x = X[min_pos]
#     y = Y[min_pos]
#     X[i] = x
#     Y[i] = y
#     del(X[min_pos])
#     del(Y[min_pos])
# print(X_new)
# print(Y_new)
#
# X = X_new
# Y = Y_new


class evolution:
    def __init__(self, name = "Generation", data=None):
        self.length = station + customer + 1
        self.name = name
        if data is None:
            self.data = self.initpop(self.length)
        else:
            assert(self.length + n_car == len(data))
            self.data = data
        self.fit = self.fitness()
        self.prob = 0

    #插0
    def insert_zero(self, data):
        load = 0
        new_list = []
        for i, pos in enumerate(data):
            load += N[pos]
            if load > Weight:
                new_list.append(0)
                load = N[pos]
            new_list.append(pos)
        return new_list

    #初始化种群
    def initpop(self, length):
        list_init = [i for i in range(1, length)]
        random.shuffle(list_init)

        list_init.insert(0, 0)
        list_init.append(0)
        #根据载重
        # insert_zero = n_car - 1
        # for i in range(0, insert_zero):
        #     insert_place = random.choice(range(2, len(list_init)-2)) #首尾及相邻一个位置不插入
        #     list_init.insert(insert_place, 0)
        list_init = self.insert_zero(list_init)
        return list_init

    # 计算适应度
    def fitness(self):
        fit = overload_cost = time_cost = trans_cost = charge_cost = overtrans_cost =0

        #1.计算运输成本
        dist = []
        i = 1
        while i < len(self.data):
            cal_dist = lambda x1, y1, x2, y2: math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))
            dist.append(cal_dist(X_pos[self.data[i]], Y_pos[self.data[i]], X_pos[self.data[i - 1]], Y_pos[self.data[i - 1]]))
            i += 1
        trans_cost = sum(dist) * cost_d

        #2.计算时间成本
        sum_time = 0
        for i, j in enumerate(self.data):
            #运输中心
            if i == 0:
                continue
            #车辆
            elif j == 0:
                sum_time = 0
            #车辆路上花费的时间
            sum_time += (dist[i - 1] / speed)
            #提前到达的惩罚
            if sum_time < T_e[j]:
                time_cost += ((T_e[j] - sum_time) * pun_e)
                sum_time = T_e[j]
            # 迟到的惩罚
            elif sum_time > T_l[j]:
                time_cost += ((sum_time - T_l[j]) * pun_l)
            #服务时间
            sum_time += T_s[j]

        #3.载重惩罚，电量惩罚和充电费用
        load = 0
        dis_after_charge = 0
        for i, j in enumerate(self.data):
            #运输中心出发
            if i == 0:
                continue
            #到达充电站
            if j > customer:
                charge_cost = dis_after_charge / h * cost_e
                dis_after_charge = 0
            #回运输中心
            elif j == 0:
                load = 0
                dis_after_charge = 0
            #其他情况
            else:
                load += N[j]  # 需求量
                dis_after_charge += dist[i - 1]
                overload_cost += (10000000 * (load > Weight))
                overtrans_cost += (10000000 * (dis_after_charge > dis))

        fit = trans_cost + time_cost + overload_cost + charge_cost + overtrans_cost
        return 1 / fit

     # 计算个体的选择概率
    def cal_choose_prob(self, sumFit):
        self.prob = self.fit / sumFit

    #选择路径，并放在最前面，便于后续的交叉
    def pick_path(self):
        target = random.randrange(n_car)  # 选择一个
        index = self.data.index(0, target + 1)
        zero_loc = 0
        self.data.insert(zero_loc, self.data.pop(index))
        index += 1
        zero_loc += 1
        #移动
        while self.data[index] != 0:
            self.data.insert(zero_loc, self.data.pop(index))
            index += 1
            zero_loc += 1
        assert(self.length + n_car == len(self.data))

    #在窗口绘制路径安排
    def plot(self):
        Xorder = [X_pos[i] for i in self.data]
        Yorder = [Y_pos[i] for i in self.data]

        plt.plot(Xorder, Yorder, c='black', zorder=1)
        plt.scatter(X_pos, Y_pos, zorder=2)
        plt.scatter([X_pos[0]], [Y_pos[0]], marker='o', zorder=3)
        plt.scatter(X_pos[-station:], Y_pos[-station:], marker='^', zorder=3)

        plt.title(self.name)
        plt.show()


# 根据种群规模初始化种群
def first(popsize):
    item = []
    for i in range(popsize):
        item.append(evolution("Gene "+str(i)))
    return item


# 计算种群适应度和
def sum_fit(items):
    sumFit = 0
    for item in items:
        sumFit += item.fit
    return sumFit


# 计算每个的选择概率prob
def choose_prob(items):
    sumFit = sum_fit(items)
    for item in items:
        item.cal_choose_prob(sumFit)


# 计算累计概率
def sum_prob(items):
    sum = 0
    for item in items:
        sum += item.prob
    return sum


#选择
def choose(items):
    good_item = int(popsize/6) * 2
    # 根据排序选择概率，并选取前1/3
    key = lambda item: item.prob
    items.sort(reverse=True, key=key)
    return items[0:good_item]

# 对于两个父代交叉，得到子代
def crossover(father_0, father_1, crossed_item):
    child_0 = []
    child_1 = []
    zeros_0 = 0
    pos_0 = 1#记录补零位置
    zeros_1 = 0
    pos_1 = 1
    #分别在两个父代染色体上随机选择一段子路经
    father_0.pick_path()
    father_1.pick_path()
    for i in father_0.data:
        pos_0 += 1
        zeros_0 += (i == 0)
        child_0.append(i)
        if zeros_0 >= 2:
            break
    for i in father_1.data:
        pos_1 += 1
        zeros_1 += (i == 0)
        child_1.append(i)
        if zeros_1 >= 2:
            break

    #子1-父2，子2-父1
    for i in father_1.data:
        if i not in child_0:
            child_0.append(i)
    for i in father_0.data:
        if i not in child_1:
            child_1.append(i)

    #末尾补零
    child_0.append(0)
    child_1.append(0)
    # 计算适应度
    key = lambda item: item.fit
    fit_ = []
    #找最好的插0位置
    while father_0.data[pos_0] != 0:
        new_child = child_0.copy()
        new_child.insert(pos_0, 0)
        new_child = evolution(data=new_child.copy())
        fit_.append(new_child)
        pos_0 += 1
    fit_.sort(reverse=True, key=key)
    assert(fit_)
    crossed_item.append(fit_[0])

    key = lambda gene: gene.fit
    fit_ = []
    while father_1.data[pos_1] != 0:
        new_child = child_1.copy()
        new_child.insert(pos_1, 0)
        new_child = evolution(data=new_child.copy())
        fit_.append(new_child)
        pos_1 += 1
    fit_.sort(reverse=True, key=key)
    crossed_item.append(fit_[0])


# 交叉
def cross(items):
    crossed_item = []
    for i in range(0, len(items), 2):
        #是否交叉
        #if random.random() < pc:
        crossover(items[i], items[i + 1], crossed_item)
    return crossed_item


# 合并
def merge(items, crossed_item):
    #32个根据概率排序
    key = lambda item: item.prob
    items.sort(reverse=True, key=key)
    pos = popsize - 1 #99
    # 因为倒序排列，挤走差的那些
    for item in crossed_item:
        items[pos] = item
        pos -= 1
    return items


# 变异一个
def do_mutate(item):
    varyNum = 10
    varied_item = []
    for i in range(varyNum):
        pos_0, pos_1 = random.choices(list(range(1, len(item.data) - 2)), k=2)
        new_item = item.data.copy()
        # 交换
        new_item[pos_0], new_item[pos_1] = new_item[pos_1], new_item[pos_0]
        varied_item.append(evolution(data=new_item.copy()))
    key = lambda item: item.fit
    varied_item.sort(reverse=True, key=key)
    return varied_item[0]


# 变异
def mutate(items):
    for i, item in enumerate(items):
        # 保留优秀
        if i < 30:
            continue
        if random.random() < pm:
            items[i] = do_mutate(item)
    return items

if __name__ == "__main__":
    # 根据种群规模初始化种群
    items = first(popsize)
    # 根据迭代次数进行迭代
    item_list =[]
    best_list = []
    for i in tqdm(range(genmax)):
        choose_prob(items)#求出每个的选择概率
        sumProb = sum_prob(items)
        chosen_item = choose(deepcopy(items))   # 选择
        crossed_item = cross(chosen_item)       # 对选出的去交叉
        items = merge(items, crossed_item)      # 复制交叉到子代种群
        items = mutate(items)                   # 变异
        #排序
        key = lambda item: item.fit
        items.sort(reverse=True, key=key)
        item_list.append(i)
        best_list.append(1 / items[0].fit)
        #测试
        if i == 500:
            print('500 fit:', items[0].fit, )
            print('500 1/fit:', 1/items[0].fit)
        if i == 1000:
            print('1000 fit:', items[0].fit, )
            print('1000 1/fit:', 1/items[0].fit)
        if i == 1500:
            print('1500 fit:', items[0].fit, )
            print('1500 1/fit:', 1/items[0].fit)
        if i == 2000:
            print('2000 fit:', items[0].fit, )
            print('2000 1/fit:', 1/items[0].fit)
        if i == 3000:
            print('3000 fit:', items[0].fit, )
            print('3000 1/fit:', 1/items[0].fit)
        if i == 4000:
            print('4000 fit:', items[0].fit, )
            print('4000 1/fit:', 1/items[0].fit)

    #排序
    key = lambda item: item.fit
    items.sort(reverse=True, key=key)
    print('\r\n')
    print('data:', items[0].data)
    print('5000 fit:', items[0].fit)
    print('5000 1/fit:', 1/items[0].fit)
    items[0].plot()

    fig, (ax1) = plt.subplots(1)
    ax1.plot(item_list, best_list)
    ax1.set(xlabel='Generation', ylabel='Fitness function (best)')
    plt.show()