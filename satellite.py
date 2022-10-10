import copy
from datetime import datetime
from datetime import timedelta
from dateutil import parser
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import numpy as np
from numpy import mean
from tkinter import *
import time
import math
satellite=["sat0","sat1","sat2","sat3","sat4","sat5","sat6","sat7","sat8"]
address_name=["Abidjan","Accra","Asmara","Balikpapan","Bozeman","Crystal-Lake","Elk-City","Hanahan","Iquique",
              "Lhasa","Madras","Manaus","Mangalore","Minsk","Munchen","Parole","Recife","Rio-de-Janeiro",
              "Sarajevo","Wallingford-Center","Yaounde","北京","南宁","武汉"]
address_position={"Abidjan":[-4.02+360,5.32],"Accra":[-0.2+360,5.56],"Asmara":[15.33,38.97],"Balikpapan":[116.86,-1.21],
                  "Bozeman":[-111.04+360,45.68],"Crystal-Lake":[-88.33+360,42.23],"Elk-City":[-99.41+360,35.4],"Hanahan":[-80.01+360,32.93],
                  "Iquique":[-69.91+360,-20.26],"Lhasa":[91.13,29.65],"Madras":[80.25,13.06],"Manaus":[-60.01+360,-3.12],
                  "Mangalore":[75.16,12.95],"Minsk":[27.58,53.9],"Munchen":[11.54,48.14],"Parole":[-76.55+360,38.98],
                  "Recife":[-34.91+360,-8.09],"Rio-de-Janeiro":[-43.46+360,-22.72],"Sarajevo":[18.43,43.87],"Wallingford-Center":[-72.82+360,41.45],
                  "Yaounde":[11.51,3.87],"北京":[116.39,39.91],"南宁":[108.33,22.8],"武汉":[114.28,30.57]}
dict_circle={"sat0":[],"sat1":[],"sat2":[],"sat3":[],"sat4":[],"sat5":[],"sat6":[],"sat7":[],"sat8":[]}#每个卫星覆盖的圆，【时间，经度，纬度】
address_timewindow={"Abidjan":[],"Accra":[],"Asmara":[],"Balikpapan":[],"Bozeman":[],"Crystal-Lake":[],"Elk-City":[],"Hanahan":[],"Iquique":[],
              "Lhasa":[],"Madras":[],"Manaus":[],"Mangalore":[],"Minsk":[],"Munchen":[],"Parole":[],"Recife":[],"Rio-de-Janeiro":[],"Sarajevo":[],"Wallingford-Center":[],"Yaounde":[],"北京":[],"南宁":[],"武汉":[]}#每个地点对应的窗口时间
address_single_timewindow={}
address_double_timewindow = {"Abidjan": [], "Accra": [], "Asmara": [], "Balikpapan": [], "Bozeman": [],
                                 "Crystal-Lake": [], "Elk-City": [], "Hanahan": [], "Iquique": [],
                                 "Lhasa": [], "Madras": [], "Manaus": [], "Mangalore": [], "Minsk": [], "Munchen": [],
                                 "Parole": [], "Recife": [], "Rio-de-Janeiro": [], "Sarajevo": [],
                                 "Wallingford-Center": [], "Yaounde": [], "北京": [], "南宁": [], "武汉": []}
address_freetime = {"Abidjan": [], "Accra": [], "Asmara": [], "Balikpapan": [], "Bozeman": [], "Crystal-Lake": [],
                        "Elk-City": [], "Hanahan": [], "Iquique": [],
                        "Lhasa": [], "Madras": [], "Manaus": [], "Mangalore": [], "Minsk": [], "Munchen": [],
                        "Parole": [], "Recife": [], "Rio-de-Janeiro": [], "Sarajevo": [], "Wallingford-Center": [],
                        "Yaounde": [], "北京": [], "南宁": [], "武汉": []}#间隙
max_freetime=[]#最大时间间隙
ave_freetime=[]#平均时间间隙
def getshijiancha(str1,str2):
    #datetime.strptime是日期形式，相减之后变成datedelta时间差形式
    #输入str，返回时间差
    timetmp1=datetime.strptime(str(datetime.strptime(str1, '%Y/%m/%d,%H:%M:%S')-datetime.strptime(str2, '%Y/%m/%d,%H:%M:%S')),'%H:%M:%S')
    return(timetmp1.hour * 3600 + timetmp1.minute * 60 + timetmp1.second)
def date2second(str):
    str=datetime.strptime(str, '%Y/%m/%d,%H:%M:%S')
    return (str.hour * 3600 + str.minute * 60 + str.second)


def dataprocessing():#传入相关的卫星和地点
    global address_single_timewindow
    for sat in dict_circle:
        time = datetime(2022, 1, 1, 0, 0, 0)  # 起始时间
        file = open('Data/SatelliteInfo/SatCoverInfo_' + sat[3] + '.txt')
        lines = file.readlines()
        i = 0
        while (i < len(lines)):
            point = []  # 时间，圆心精度，圆心维度，半径
            min1 = lines[i + 6].split()  # 前为经度最小值，后为纬度
            max1 = lines[i + 16].split()  # 前为经度最大值，后为纬度
            r = (float(max1[0]) - float(min1[0])) / 2
            center = r + float(min1[0])  # 圆心的经度
            point.append(time.strftime("%Y/%m/%d,%H:%M:%S"))
            point.append(center)
            point.append(float(min1[1]))
            point.append(r)
            dict_circle[sat].append(point)
            time = time + timedelta(seconds=1)  # 时间+1s
            i += 22
        # break#!!!!!!!!!!!!!!!!!!!!!!！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！1测试点，记得删掉

    start = 0
    end = 0
    # 地点经度：address_position[address][0]，地点纬度：address_position[address][1]
    # 卫星覆盖圆心：dict_circle[circle][t][1],dict_circle[circle][t][2]
    # 半径：dict_circle[circle][t][3]
    for address in address_position:
        for circle in dict_circle:
            for t in range(0, 86401):
                if (start == 0):  # 还没找到开始的时间窗口,则加入开始时间
                    if ((address_position[address][0] - dict_circle[circle][t][1]) ** 2 +
                        (address_position[address][1] - dict_circle[circle][t][2]) ** 2) <= 49.07:
                        start = dict_circle[circle][t][0]
                elif ((start != 0) and (end == 0)):  # 还没找到结束的时间窗口，则加入结束时间
                    if ((address_position[address][0] - dict_circle[circle][t][1]) ** 2 +
                        (address_position[address][1] - dict_circle[circle][t][2]) ** 2) > 49.07:
                        end = dict_circle[circle][t][0]
                        address_timewindow[address].append([circle, start, end])
                        start = end = 0

    # print(address_timewindow["Abidjan"])
    # 计算时间窗口
    # repeat：重叠时间段
    repeat = {"Abidjan": [], "Accra": [], "Asmara": [], "Balikpapan": [], "Bozeman": [], "Crystal-Lake": [],
              "Elk-City": [], "Hanahan": [], "Iquique": [],
              "Lhasa": [], "Madras": [], "Manaus": [], "Mangalore": [], "Minsk": [], "Munchen": [], "Parole": [],
              "Recife": [], "Rio-de-Janeiro": [], "Sarajevo": [], "Wallingford-Center": [], "Yaounde": [], "北京": [],
              "南宁": [], "武汉": []}
    tmp = 0
    for address in address_timewindow:
        for i in range(0, len(address_timewindow[address])):
            for t in range(i + 1, len(address_timewindow[address])):
                if ((address_timewindow[address][t][2] <= address_timewindow[address][i][1]) or (
                        address_timewindow[address][t][1] >= address_timewindow[address][i][2])):
                    continue
                repeat[address].append([i, t])#记录重叠的时间窗口的序号，以配对形式记录

    # for address in address_timewindow:
    #     address_single_timewindow[address]=address_timewindow[address]
    address_single_timewindow=copy.deepcopy(address_timewindow)

    jiaoji = []
    # for address in repeat:
    #     print(repeat[address])
    for address in repeat:
        if (repeat[address]):
            # 按照重叠卫星的第二个降序排列，这样先删除后面的元素不会影响前面的元素
            repeat[address] = sorted(repeat[address], key=lambda x: x[1], reverse=True)
            for timedui in repeat[address]:
                # print(type(address_single_timewindow[address][timedui[0]][1]))
                # print(address_single_timewindow[address][timedui[0]][1])
                # 求并集
                address_single_timewindow[address][timedui[0]][1] = min(address_timewindow[address][timedui[0]][1],
                                                                        address_timewindow[address][timedui[1]][1])
                address_single_timewindow[address][timedui[0]][2] = max(address_timewindow[address][timedui[0]][2],
                                                                        address_timewindow[address][timedui[1]][2])
                del address_single_timewindow[address][timedui[1]]
                # 求交集
                jiaoji.append(address_timewindow[address][timedui[0]][0])  # 卫星一
                jiaoji.append(address_timewindow[address][timedui[1]][0])  # 卫星二
                jiaoji.append(max(address_timewindow[address][timedui[0]][1],
                                  address_timewindow[address][timedui[1]][1]))  # 更大的开始时间
                jiaoji.append(min(address_timewindow[address][timedui[0]][2],
                                  address_timewindow[address][timedui[1]][2]))  # 更小的结束时间
                address_double_timewindow[address].append(jiaoji)
                jiaoji = []#清空再来
    # 求时间间隙
    for address in address_single_timewindow:
        address_single_timewindow[address] = sorted(address_single_timewindow[address], key=lambda x: x[1],
                                                    reverse=False)
        for i in range(1, len(address_single_timewindow[address])):
            freetime = date2second(address_single_timewindow[address][i][2])-date2second(
                address_single_timewindow[address][i - 1][1])
            address_freetime[address].append(freetime)

    print(address_single_timewindow["Crystal-Lake"])
    print(address_freetime["Crystal-Lake"])
    for address in address_freetime:
        maxfree=max(address_freetime[address])
        totalfree=mean(address_freetime[address])
        max_freetime.append(maxfree)
        ave_freetime.append(totalfree)

# print(address_freetime['Abidjan'])
def draw1():
    xold = []
    xnew = []
    for i in range(0, 86401, 3600):
        xold.append((i))
    for t in range(0, 25):
        xnew.append(str(t) + ':00')
    x1 = {}
    x2 = {}
    x3 = {}
    a={}
    b = {}
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示正负号
    plt.rcParams['font.family'] = "SimHei"  # 设置字体
    fig = plt.figure(figsize=(28, 7))
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    for address in address_single_timewindow:
        if (address_single_timewindow[address]):
            tmpx1 = []
            tmpx2 = []
            tmpx3=[]
            for i in range(0, len(address_single_timewindow[address])):
                tmpx1.append(date2second(address_single_timewindow[address][i][1]))
                tmpx3.append(date2second(address_single_timewindow[address][i][2]))
                tmpx2.append(getshijiancha(address_single_timewindow[address][i][2],address_single_timewindow[address][i][1]))
            x1[address] = tmpx1
            x2[address]=tmpx2
            x3[address]=tmpx3
    for address in x1:
        x1_begin = x1[address]#各窗口的开始时间
        x2_during=x2[address]#各窗口的持续时间
        x3_end = x3[address]  # 各窗口的持续时间
        for during in x2_during:
            for begin in x1_begin:
                ax1.barh(y=address,width=during,left=begin)#y轴坐标，矩形块长度，矩形块最左边的坐标，矩形块边的颜色，矩形块的颜色


    for address in address_double_timewindow:
        if (address_double_timewindow[address]):
            tmpx = []
            tmpy = []
            for i in range(0, len(address_double_timewindow[address])):
                tmpx.append(date2second(address_double_timewindow[address][i][2]))
                tmpy.append(getshijiancha(address_double_timewindow[address][i][3],address_double_timewindow[address][i][2]))
            a[address] = tmpx
            b[address] = tmpy
    for address in a:
        x2 = a[address]
        y2 = b[address]
        for during in y2:
            for begin in x2:
                ax2.barh(y=address, width=during, left=begin)
    # plt.xticks(xold, xnew)
    ax1.set_xticks(xold)
    ax1.set_xticklabels(xnew, fontsize=8)
    ax2.set_xticks(xold)
    ax2.set_xticklabels(xnew, fontsize=8)
    ax1.set_title("各地址一重时间窗口分布")
    ax2.set_title("各地址二重时间窗口分布")
    plt.show()
def draw2():
    # 绘制柱状图
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示正负号
    plt.rcParams['font.family'] = "SimHei"  # 设置字体
    x1 = []
    for address in address_freetime:
        if (address_freetime[address]):
            x1.append(address)
    y1 = max_freetime
    y2 = ave_freetime
    fig = plt.figure(figsize=(14, 7))
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax1.bar(x1, y1, color='red')
    ax2.bar(x1, y2, color='blue')
    # for tick in ax1.get_xticklabels():
    #     tick.set_rotation(70)
    plt.xticks(rotation=70)
    ax1.set_title("各地址覆盖时间间隙最大值")
    ax2.set_title("各地址覆盖时间间隙平均值")
    plt.show()
# if __name__ == '__main__':
    # dataprocessing()
    # draw1()
    # draw2()













