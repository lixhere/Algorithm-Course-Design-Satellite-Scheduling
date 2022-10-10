import time
from datetime import datetime
from datetime import timedelta
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from satellite import *
import math
import random
import os
from math import radians, sin
allarea=30033828000283.74
cellset=[]#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# time

#输入格式：首尾相连的经纬度对
# data = "115.989099,39.646023;115.987394,39.645988;115.987371,39.647407;115.986684,39.647423;115.986602,39.648088;115.989095,39.648151;115.989188,39.646021;115.989099,39.646023"
def getArea(data):
    arr = data.split(';')
    arr_len = len(arr)
    if arr_len < 3:
        return 0.0
    temp = []
    for i in range(0,arr_len):
        temp.append([float(x) for x in arr[i].split(',')])
    s = temp[0][1] * (temp[arr_len -1][0]-temp[1][0])
    for i in range(1,arr_len):
        s += temp[i][1] * (temp[i-1][0] - temp[(i+1)%arr_len][0])
    return round(math.fabs(s/2)*9101160000.085981,6)

def getArea1(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    r = 6371
    return abs(r**2 * (lon2 - lon1) * (sin(lat2) - sin(lat1)))

class cell():
    def __init__(self,lt,l,state,smallcell):
        self.lt=lt#左上顶点
        self.l=l#边长
        self.state=state#状态：0不在，1在，2不确定
        self.smallcell=smallcell#分割后的小格子
        self.jingwei = [(lt[0] - 50) / 10 + 75, 55 - ((lt[1] - 50) / 10)]  # 经纬度

def inicell(cellsettmp):
    # 初始化528个格子
    cellsettmp=[]
    for i in range(50, 650, 25):
        for t in range(50, 600, 25):
            tmp = cell([i, t], 25, 0,[])
            cellsettmp.append(tmp)
    return cellsettmp
#点x，点y，圆心x，圆心y，半径，在内返回1
def judge(x1,y1,x2,y2,r2):
    if((x1-x2)**2+(y1-y2)**2)<=r2:
        return 1
    else:
        return 0

def getall2():
    global Area1
    areaall=[]
    x=[]
    for timenow in range(0,86400,60):
        Area1 = 0
        x.append(timenow)
        for sat in dict_circle:
            centerx = dict_circle[sat][timenow][1]
            centery = dict_circle[sat][timenow][2]
            getall(cellset, centerx, centery)
        print(Area1/allarea*100,timenow)
        areaall.append(Area1/allarea*100)

    # 参数linewidth设置plot()绘制的线条的粗细
    plt.plot(x, areaall, linewidth=1)
    # 语法：plot(x轴坐标，y轴坐标，其他参数设置)
    # 函数title()给图表指定标题，参数fontsize指定了图表中文字的大小。
    plt.title("Coverage", fontsize=24)
    # 给x轴添加标签，设置字体大小
    plt.xlabel("Time/s", fontsize=14)
    # 给y轴添加标签，设置字体大小
    plt.ylabel("rate/%", fontsize=14)
    # # 设置每个坐标轴的取值范围
    # plt.axis([0, 6, 0, 100])  # [x.x,x.y,y.x,y.y]
    # # tick_params()设置刻度标记的大小，设置刻度的样式
    # plt.tick_params(axis='both', labelsize=14)
    # 打开matplotlib查看器，并显示绘制的图形
    plt.show()



def getall(cellss,centerx,centery):
    global Area1
    x = centerx
    y = centery
    cells=copy.deepcopy(cellss)
    if (cells[0].l > 4):  # S=49Π*0.1%=0.15，r<0.4,L<4
        for ce in cells:
            # 左上：ce.jingwei
            # 左下：[ce.jingwei[0],ce.jingwei[1]-l/10]
            # 右上：[ce.jingwei[0]+l/10,ce.jingwei[1]]
            # 右下：[ce.jingwei[0]+l/10,ce.jingwei[1]-l/10]
            # 四个顶点全在
            if ce.state != 1:
                if ((judge(ce.jingwei[0], ce.jingwei[1], centerx, centery, 49.07)) and (
                        judge(ce.jingwei[0], ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) and (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) and (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1], centerx, centery, 49.07))):
                    if (ce.state == 2):
                        ce.smallcell = []  # 若之前为部分在，将其小格子清空
                    ce.state = 1
                    datatmp = str(ce.jingwei[0]) + ',' + str(ce.jingwei[0]) + ';' + str(ce.jingwei[0]) + ',' + str(
                        ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                        ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                        ce.jingwei[1]) + ';' + str(ce.jingwei[0]) + ',' + str(ce.jingwei[1])
                    Area1 += getArea(datatmp)
                    continue
                # 不确定在不在
                if ((judge(ce.jingwei[0], ce.jingwei[1], centerx, centery, 49.07)) or (
                        judge(ce.jingwei[0], ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) or (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) or (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1], centerx, centery, 49.07))):
                    if (ce.state == 0):  # 若之前全不在，分小格子，之前部分在，无需再分格用原来的格子即可
                        ce.state = 2
                        ce.smallcell.append(cell([ce.lt[0], ce.lt[1]], ce.l / 2, 0, []))
                        ce.smallcell.append(cell([ce.lt[0] + ce.l / 2, ce.lt[1]], ce.l / 2, 0, []))
                        ce.smallcell.append(cell([ce.lt[0] + ce.l / 2, ce.lt[1] + ce.l / 2], ce.l / 2, 0, []))
                        ce.smallcell.append(cell([ce.lt[0], ce.lt[1] + ce.l / 2], ce.l / 2, 0, []))
                    if (ce.l < 7):
                        datatmp = str(ce.jingwei[0]) + ',' + str(ce.jingwei[1]) + ';' + str(ce.jingwei[0]) + ',' + str(
                            ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                            ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                            ce.jingwei[1]) + ';' + str(ce.jingwei[0]) + ',' + str(ce.jingwei[1])
                        Area1 += getArea(datatmp)
                    getall(ce.smallcell, x, y)





def four_tree(cells,centerx,centery):#格子，覆盖圆经度，覆盖圆维度
    global Area,accuracy,accuracy1,Areashow#area是总面积，accuracy是经度
    x=centerx
    y=centery
    if(cells[0].l>accuracy):#S=49Π*0.1%=0.15，r<0.4,L<4 49*3.1415*accuracy/100
        for ce in cells:
            # 左上：ce.jingwei[0],ce.jingwei[1]
            # 右下：[ce.jingwei[0]+l/10,ce.jingwei[1]-l/10]
            # 四个顶点全在
            if ce.state!=1:
                if ((judge(ce.jingwei[0], ce.jingwei[1], centerx, centery, 49.07)) and (
                        judge(ce.jingwei[0], ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) and (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) and (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1], centerx, centery, 49.07))):
                    if(ce.state==2):
                        ce.smallcell=[]#若之前为部分在，将其小格子清空
                    ce.state = 1
                    datatmp = str(ce.jingwei[0]) + ',' + str(ce.jingwei[0]) + ';' + str(ce.jingwei[0]) + ',' + str(
                             ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                             ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                             ce.jingwei[1]) + ';' + str(ce.jingwei[0]) + ',' + str(ce.jingwei[1])
                    Area+= getArea(datatmp)
                    Areashow += getArea1(ce.jingwei[0], ce.jingwei[1], ce.jingwei[0] + ce.l / 10, ce.jingwei[1] - ce.l / 10)
                    canvas.create_rectangle(ce.lt[0], ce.lt[1], ce.lt[0] + ce.l, ce.lt[1] + ce.l, fill='green')
                    continue
                # 不确定在不在
                if ((judge(ce.jingwei[0], ce.jingwei[1], centerx, centery, 49.07)) or (
                        judge(ce.jingwei[0], ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) or (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1] - ce.l / 10, centerx, centery, 49.07)) or (
                        judge(ce.jingwei[0] + ce.l / 10, ce.jingwei[1], centerx, centery, 49.07))):
                    if (ce.state == 0):#若之前全不在，分小格子，之前部分在，无需再分格用原来的格子即可
                        ce.state = 2
                        ce.smallcell.append(cell([ce.lt[0], ce.lt[1]], ce.l / 2, 0, []))
                        ce.smallcell.append(cell([ce.lt[0] + ce.l / 2, ce.lt[1]], ce.l / 2, 0, []))
                        ce.smallcell.append(cell([ce.lt[0] + ce.l / 2, ce.lt[1] + ce.l / 2], ce.l / 2, 0, []))
                        ce.smallcell.append(cell([ce.lt[0], ce.lt[1] + ce.l / 2], ce.l / 2, 0, []))
                    if (ce.l <= accuracy1):
                        canvas.create_rectangle(ce.lt[0], ce.lt[1], ce.lt[0] + ce.l, ce.lt[1] + ce.l, fill='red')
                        datatmp = str(ce.jingwei[0]) + ',' + str(ce.jingwei[0]) + ';' + str(ce.jingwei[0]) + ',' + str(
                            ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                            ce.jingwei[1] - ce.l / 10) + ';' + str(ce.jingwei[0] + ce.l / 10) + ',' + str(
                            ce.jingwei[1]) + ';' + str(ce.jingwei[0]) + ',' + str(ce.jingwei[1])
                        Area+= getArea(datatmp)
                    four_tree(ce.smallcell, x, y)#递归调用判断更小四个格子



#画图开始的按钮
def drawbegin():
    global time1,time2,timenow,timestep,accuracy,accuracy1
    time=et5.get()
    timestep=int(et5.get())
    accuracy = float(et7.get())
    accuracy=math.sqrt(49*3.1415*accuracy/100)*10
    ttt=25
    while(ttt>accuracy):
        ttt=ttt/2
    accuracy1=ttt*2
    time1=datetime.strptime(et1.get(), '%Y/%m/%d,%H:%M:%S')
    time1=time1.hour*3600+time1.minute*60+time1.second
    time2 = datetime.strptime(et2.get(), '%Y/%m/%d,%H:%M:%S')
    time2 = time2.hour * 3600 + time2.minute * 60 + time2.second
    timenow = time1
    bt1.after(1000, drawcircle())
#画图开始循环调用的函数
def drawcircle():
    global timenow,hanshu,cellset,timestep,Area,allarea,et4,et6,Areashow
    timeform='2022/01/01,'+str(timedelta(seconds=timenow))
    et3.delete(0,END)
    et3.insert(0, timeform)
    canvas.delete("all")
    initcanvas()
    hanshu = bt1.after(1000, drawcircle)
    Area=0
    Areashow=0
    for sat in dict_circle:
        centerx = dict_circle[sat][timenow][1]
        centery = dict_circle[sat][timenow][2]
        four_tree(cellset, centerx, centery)
    timenow += timestep
    et6.delete(0, END)
    et6.insert(0, Areashow)
    rate=Area/allarea*100
    et4.delete(0, END)
    et4.insert(0, str(rate)+'%')
    cellset = inicell(cellset)#更新cellset进入下一秒
    if (timenow > time2 ):
        bt1.after_cancel(hanshu)
def initcanvas():
    # 初始化网格
    for i in range(50, 675, 25):
        canvas.create_line(i, 30, i, 620)
    for t in range(50, 625, 25):
        canvas.create_line(30, t, 670, t)
    jingdu = 75
    weidu = 55
    for i in range(50, 675, 100):
        canvas.create_text(i, 20, text=str(jingdu) + 'E', font=("PUrisa", 13))
        jingdu += 10
    for t in range(50, 625, 100):
        canvas.create_text(15, t, text=str(weidu) + 'N', font=("PUrisa", 13))
        weidu -= 10

def stop():
    bt1.after_cancel(hanshu)




satgap={"sat0":30,"sat1":30,"sat2":30,"sat3":35,"sat4":35,"sat5":35,"sat6":25,"sat7":25,"sat8":25}
tasktime=[['2022/01/01,11:00:00', '2022/01/01,12:30:00'],['2022/01/01,00:00:00','2022/01/01,06:00:00'],['2022/01/01,11:00:00','2022/01/01,15:00:00'],['2022/01/01,16:00:00','2022/01/01,19:00:00'],['2022/01/01,00:00:00','2022/01/01,12:00:00']]
tasksat=[['sat6','sat0'],['sat0','sat1','sat2'],['sat0','sat1','sat3','sat4','sat5'],['sat6','sat7','sat8','sat3','sat4','sat5'],['sat6','sat7','sat8','sat0','sat1','sat2','sat3','sat4','sat5']]
def read(i):
    global addresstmp
    addresstmp = {}
    file = open('Data/TargetInfo/target' +str(i+1)+ '.txt',encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        linetmp = []
        line=line.split()
        name=line[0]
        for t in range(1,5):
            if(t==1 and float(line[t])<0):
                linetmp.append(float(line[t])+360)#数据格式统一
            else:
                linetmp.append(float(line[t]))
        addresstmp[name]=linetmp
    return(addresstmp)

# sattmp：传入相关的卫星和地点坐标，卫星只需要传入[’sat0‘,’sat1‘]
# positmp：地点坐标示例：{‘鞍山’:[122.98,41.12,14,9]}
#timetmp:时间窗口示例：['2022-01-01,11:00:00', '2022-01-01,12:30:00']
def getwindow(sattmp,positmp,timetmp):
    global dict_circle,timewindow_kaddreess,timewindow_ksat
    start1=date2second(timetmp[0])
    end1=date2second(timetmp[1])
    timewindow_kaddreess = {}#以地点为key
    timewindow_ksat = {}  # 以卫星为key
    for address in positmp:
        timewindow_kaddreess[address]=[]
    for circle in sattmp:
        timewindow_ksat[circle]=[]
    start = 0
    end = 0
    # 地点经度：address_position[address][0]，地点纬度：address_position[address][1]
    # 卫星覆盖圆心：dict_circle[circle][t][1],dict_circle[circle][t][2]
    # 半径：dict_circle[circle][t][3]
    for address in positmp:
        timewindow_kaddreess[address].append(positmp[address][3] / positmp[address][2])
        timewindow_kaddreess[address].append(positmp[address][2])
        for circle in sattmp:
            for t in range(start1, end1+1):
                if (start == 0):  # 还没找到开始的时间窗口
                    if ((positmp[address][0] - dict_circle[circle][t][1]) ** 2 +
                        (positmp[address][1] - dict_circle[circle][t][2]) ** 2) <= 49.07:
                        start = dict_circle[circle][t][0]
                elif ((start != 0) and (end == 0)):  # 还没找到结束的时间窗口
                    if ((positmp[address][0] - dict_circle[circle][t][1]) ** 2 +
                        (positmp[address][1] - dict_circle[circle][t][2]) ** 2) > 49.07:
                        end = dict_circle[circle][t][0]
                        # 如果这个时间段小于观测所需时间，则没有意义
                        if (getshijiancha(end,start)>positmp[address][2]):
                            timewindow_kaddreess[address].append([circle, date2second(start), date2second(end),getshijiancha(end,start)])
                            timewindow_ksat[circle].append([address,date2second(start), date2second(end),getshijiancha(end,start)])
                        start = end = 0
    for sat in timewindow_ksat:
        timewindow_ksat[sat]= sorted(timewindow_ksat[sat], key=lambda x: x[1], reverse=False)
    print(timewindow_kaddreess)
    print(timewindow_ksat)

#地点集合
def getjustaddre(dataraw):
    alist = []
    for name in dataraw:
        alist.append(name)
    return alist


def greedy(dataraw,task):
    score=0
    global satgap,flag,result
    result={}
    # 按照“性价比”从高到低排列
    datarank=sorted(dataraw.items(), key=lambda x: x[1][0], reverse=True)
    #按照“性价比”依次给城市分配事件和卫星
    for itemtmp in datarank:
        item=itemtmp[0]
        resultmp = []
        if(len(dataraw[item])==2):#如果该地点无时间窗口，则录入空数组
            result[item] = resultmp
            continue
        sattmp=dataraw[item][2][0]#对应卫星
        timestarttmp=dataraw[item][2][1]#开始时间
        timeendtmp = dataraw[item][2][1] + dataraw[item][1]#结束时间
        gaptmp = satgap[sattmp]
        timenexttmp=timeendtmp+gaptmp#下一窗口时间
        resultmp.append(sattmp)
        resultmp.append(dataraw[item][2][1])
        resultmp.append(timeendtmp)
        score += addresstmp[item][3]
        del dataraw[item]
        result[item]=resultmp#将【卫星，开始时间，结束时间】格式的分配结果保存
        #更新每个地点的时间窗口
        for item1 in dataraw:
            #item1为地点
            for i in range((len(dataraw[item1])-1),1,-1):
                if(dataraw[item1][i][0]==sattmp):#如果是同一颗卫星，则需要更新时间窗口
                    if(dataraw[item1][i][1]<=timestarttmp and dataraw[item1][i][2]>=timestarttmp
                            and dataraw[item1][i][2]<=timenexttmp):#时间窗口去尾
                        if((timestarttmp-dataraw[item1][i][1])>dataraw[item1][1]):#如果时间窗口仍然大于所需时间
                            dataraw[item1][i][2]=timestarttmp#更新时间窗口的结束时间
                        else:#否则删除该时间窗口
                            del dataraw[item1][i]
                    elif(dataraw[item1][i][1]>=timestarttmp and dataraw[item1][i][1]<=timenexttmp
                         and dataraw[item1][i][2]>=timenexttmp):#去头
                        if ((dataraw[item1][i][2]-timenexttmp) > dataraw[item1][1]):  # 如果时间窗口仍然大于所需时间
                            dataraw[item1][i][1] = timenexttmp#更新时间窗口的开始时间
                        else:  # 否则删除该时间窗口
                            del dataraw[item1][i]
                    elif (dataraw[item1][i][1] >= timestarttmp and dataraw[item1][i][2] <= timenexttmp):#全部删除
                        del dataraw[item1][i]
                    elif (dataraw[item1][i][1]<=timestarttmp and dataraw[item1][i][2]>=timenexttmp):#劈两半去身子
                        flag=0
                        addtmp1=copy.deepcopy(dataraw[item1][i])
                        addtmp2=copy.deepcopy(dataraw[item1][i])
                        if (timestarttmp-dataraw[item1][i][1])>dataraw[item1][1]:
                            addtmp1[2]=timestarttmp
                        if (dataraw[item1][i][2]-timenexttmp)>dataraw[item1][1]:
                            addtmp2[1]=timenexttmp
                        if addtmp1!=dataraw[item1][i]:
                            dataraw[item1].insert(i,addtmp1)#插入一个新的时间窗口
                            flag+=1
                        if addtmp2 != dataraw[item1][i]:
                            dataraw[item1].insert(flag+i,addtmp2)#插入一个新的时间窗口
                            flag+=1
                        del dataraw[item1][i+flag]#去掉原时间窗口
    print(result)
    print(score)
    et9.delete(0, END)
    et9.insert(0, "最终结果为"+str(score))

#新建卫星可用窗口记录
def sattimewindow(sats,timewindow_ksat):
    # print(timewindow_ksat)
    # print(sats)
    sattimefree={}
    for sat in sats:
        atfirst = timewindow_ksat[sat][0][1]
        atend = timewindow_ksat[sat][-1][2]
        sattimefree[sat]=[[atfirst,atend]]
    return(sattimefree)



def GA(task):
    global maxscore,timewindow_ksat,resultga,sattimefree,citys
    maxscore=0
    maxgen=800#遗传代数
    popsize=130#个体总数
    sattimefree=sattimewindow(tasksat[task],timewindow_ksat)
    citys=getjustaddre(addresstmp)#获取地点列表
    population=initpopulation(citys,tasksat[task],popsize)#初始化
    for gen in range(1,maxgen+1):
        population = mutate(population, popsize, len(citys), 0.9, 0.15)#进化
        population = select(population, citys, sattimefree, popsize)#选择
        if gen%10==0:
            print("种群已经进化到第"+str(gen)+"代,最优策略得分为"+str(maxscore))#打印结果
    resultga=population[0]
    et9.delete(0, END)
    et9.insert(0, "最终结果为" + str(maxscore))



#初始化种群
def initpopulation(alist,slist,psize):#地点列表，卫星列表，种群数量
    population=[]#种群
    for t in range(0,psize):#循环种群，得到对于每个个体
        indivisual = []
        for i in range(0, len(alist)):
            sat=random.choice(slist)#选择卫星
            atfirst=timewindow_ksat[sat][0][1]
            atend=timewindow_ksat[sat][-1][2]
            time=random.randint(atfirst,atend)#在atfirst和atend间随机选择一个数
            indivisual.append([sat,time])  # 每个地点对应的卫星调度
        population.append(indivisual)#个体基因插入种群
    return(population)


#种群迭代，交叉时绑定卫星和时间，变异只变时间
def mutate(population,popsize,citynum,jiaocha,bianyi):#种群，个体总数，城市总个数，交叉概率，变异概率
    # 交叉
    i=0
    for i in range(0,popsize):
        if (random.random() < jiaocha):  #符合交叉概率
            indivisualnew = copy.deepcopy(population[i])
            id = random.randint(0, popsize - 1)# 随机选择一个个体
            aa = random.randint(0, citynum - 1)  # 在基因中随机选择一个断点
            bb = random.randint(0, citynum - 1)  # 再选一个
            change1 = min(aa, bb)
            change2 = max(aa, bb)
            for j in range(change1,change2):
                indivisualnew[j]=(population[id][j])
            population.append(indivisualnew)#新个体加入种群
    # print(len(population))
    # 变异
    for i in range(0,len(population)):
        if (random.random() < jiaocha):#符合变异概率
            # for numbianyi in range(0,2):#一次变三个基因
            aa = random.randint(0, citynum - 1)  # 随机选择一个基因
            selectedsat = population[i][aa][0]  # 该基因对应的卫星
            atfirst = timewindow_ksat[selectedsat][0][1]
            atend = timewindow_ksat[selectedsat][-1][2]
            time = random.randint(atfirst, atend)
            population[i][aa][1] = time
    # print(len(population))
    return population

#选择
def select(population,cityss,sattimefree1,popsize):#种群，城市，卫星时间,个体数量
    global addresstmp,maxscore
    newpopulation=[]
    scores = []
    index = 0
    for indivisual in population:#population=[卫星，时间]遍历每个个体
        score = 0
        sattimefree=copy.deepcopy(sattimefree1)
        for i in range(0,len(indivisual)):#遍历每个城市
            city = cityss[i]  # 城市
            sat = indivisual[i][0]  # 分配卫星
            starttime = indivisual[i][1]  # 开始时间
            endtime = indivisual[i][1] + addresstmp[city][2]  # 结束时间
            nexttime = endtime + satgap[sat]  # 该卫星下一窗口
            for j in range(2, len(timewindow_kaddreess[city])):  # 遍历该城市的卫星窗口
                if timewindow_kaddreess[city][j][0] == sat:  # 如果卫星对应
                    if starttime >= timewindow_kaddreess[city][j][1] and endtime <= timewindow_kaddreess[city][j][2]:  # 判断基因时间是否在时间窗口内
                        for t in range(len(sattimefree[sat])-1, -1, -1):  # 在空闲时间窗口中搜索
                            if (sattimefree[sat][t][0] < starttime and sattimefree[sat][t][1] > endtime):  # 有空闲时间窗口可用
                                flag = 0
                                if (starttime - sattimefree[sat][t][0] >= 3):  # 新的时间窗口大于3
                                    tmp = copy.deepcopy(sattimefree[sat][t])
                                    tmp[1] = starttime
                                    sattimefree[sat].insert(t + 1, tmp)  # 插入一个新的窗口（前）
                                    flag += 1
                                if (sattimefree[sat][t][1] - nexttime >= 3):
                                    tmp = copy.deepcopy(sattimefree[sat][t])
                                    tmp[0] = nexttime
                                    sattimefree[sat].insert(t + 1 + flag, tmp)
                                    flag += 1
                                if (flag != 0):
                                    del sattimefree[sat][t]
                                score += addresstmp[city][3]
        scores.append([index,score])
        index+=1
    scores= sorted(scores, key=lambda x: x[1], reverse=True)
    maxscore=max(maxscore,scores[0][1])
    for p in range(0,popsize):#排名前列的进入下一代
        newpopulation.append(population[scores[p][0]])
    return newpopulation

def ui():
    global tu, et1, et2, et3,et4,et5,et6,et7,et8,et9,canvas,bt1,bt2,bt3,bt4,bt5,bt6,bt7,bt8,bt9,bt10
    root = Tk()
    root.geometry('940x650+350+70')#宽度，高度，距离屏幕左边的距离，距离屏幕上面的距离
    root.title('实时覆盖率')
    root.resizable(False, False)
    canvas = Canvas(root, width=700, height=650,background='white')
    canvas.pack(side='left')

    initcanvas()
    lable1 = Label(root, text='起始时间')
    lable1.place(x=720, y=10)
    et1 = Entry(root, width=20)
    et1.place(x=780, y=10)
    et1.insert(0, '2022/01/01,11:25:00')
    lable2=Label(root,text='结束时间')
    lable2.place(x=720, y=40)
    et2 = Entry(root, width=20)
    et2.place(x=780, y=40)
    et2.insert(0, '2022/01/01,11:28:00')
    bt1 = Button(root, text=' 开始绘制 ', command=drawbegin)
    bt1.place(x=720, y=80)
    bt2 = Button(root, text=' 结束 ', command=stop)
    bt2.place(x=820, y=80)

    lable3 = Label(root, text='当前时间')
    lable3.place(x=720, y=130)
    et3 = Entry(root, width=20)
    et3.place(x=780, y=130)

    lable6 = Label(root, text='覆盖面积')
    lable6.place(x=720, y=160)
    et6 = Entry(root, width=20)
    et6.place(x=780, y=160)


    lable4 = Label(root, text='覆盖率')
    lable4.place(x=720, y=190)
    et4 = Entry(root, width=20)
    et4.place(x=780, y=190)


    lable5 = Label(root, text='速度')
    lable5.place(x=720, y=220)
    et5 = Entry(root, width=20)#速度
    et5.place(x=780, y=220)
    et5.insert(0, '2')

    lable6 = Label(root, text='精度/%')
    lable6.place(x=720, y=250)
    et7 = Entry(root, width=20)  # 速度
    et7.place(x=780, y=250)
    et7.insert(0, 0.1)

    bt10 = Button(root, text=' 保存数据 ', command=save)
    bt10.place(x=720, y=280)

    bt3 = Button(root, text=' 时间窗口甘特图 ', command=draw1)
    bt3.place(x=720, y=320)
    bt4 = Button(root, text=' 时间间隙柱形图 ', command=draw2)
    bt4.place(x=720, y=360)

    bt5 = Button(root, text='覆盖率折线图', command=getall2)
    bt5.place(x=720, y=400)

    lable7 = Label(root, text='选择任务')
    lable7.place(x=720, y=440)
    et8 = Entry(root, width=20)
    et8.place(x=780, y=440)
    et8.insert(0, 1)

    et9 = Entry(root, width=20)
    et9.place(x=720, y=480)
    et9.insert(0, "等待选择任务和算法")

    bt6 = Button(root, text='贪心法', command=usergreedy)
    bt6.place(x=720, y=510)

    bt7 = Button(root, text='遗传法', command=useGA)
    bt7.place(x=820, y=510)

    bt8 = Button(root, text='贪心可视化', command=showgreedy)
    bt8.place(x=720, y=550)

    bt9 = Button(root, text='遗传可视化', command=showGA)
    bt9.place(x=820, y=550)

    root.mainloop()

def usergreedy():
    task = int(et8.get())-1
    getwindow(tasksat[task], read(task), tasktime[task])
    greedy(timewindow_kaddreess,task)


def useGA():
    task = int(et8.get())-1
    getwindow(tasksat[task], read(task), tasktime[task])
    GA(task)

def showgreedy():
    color={'sat0':'lightblue','sat1':'lightcoral','sat2':'lightgreen','sat3':'lightgray','sat4':'lightpink','sat5':'lightyellow','sat6':'orange','sat7':'purple','sat8':'blue'}
    color2 = {'sat0': 'blue', 'sat1': 'coral', 'sat2': 'lightgreen', 'sat3': 'lightgray', 'sat4': 'lightpink',
             'sat5': 'orange', 'sat6': 'yellow', 'sat7': 'purple', 'sat8': 'blue'}

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示正负号
    plt.rcParams['font.family'] = "SimHei"  # 设置字体
    for sat in timewindow_ksat:
        for window in timewindow_ksat[sat]:
            plt.barh(y=window[0],width=window[3],left=window[1],color="lightgray")
    for address in result:
        if(result[address]):
            plt.barh(y=address, width=result[address][2]-result[address][1], left=result[address][1],color=color[result[address][0]])
    plt.title('贪心算法下的时间分布')
    plt.show()

def showGA():
    global addresstmp,sattimefree,citys
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 正常中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 显示正负号
    plt.rcParams['font.family'] = "SimHei"  # 设置字体
    color = {'sat0': 'lightblue', 'sat1': 'lightcoral', 'sat2': 'lightgreen', 'sat3': 'lightgray', 'sat4': 'lightpink',
             'sat5': 'lightyellow', 'sat6': 'orange', 'sat7': 'purple', 'sat8': 'blue'}

    result1=[]
    result2=[]
    index = 0
    sattimefreetmp = copy.deepcopy(sattimefree)
    for i in range(0, len(resultga)):  # 遍历每个城市
        city = citys[i]  # 城市
        sat = resultga[i][0]  # 分配卫星
        starttime = resultga[i][1]  # 开始时间
        endtime = resultga[i][1] + addresstmp[city][2]  # 结束时间
        nexttime = endtime + satgap[sat]  # 该卫星下一窗口
        for j in range(2, len(timewindow_kaddreess[city])):  # 遍历该城市的卫星窗口
            if timewindow_kaddreess[city][j][0] == sat:  # 如果卫星对应
                if starttime >= timewindow_kaddreess[city][j][1] and endtime <= timewindow_kaddreess[city][j][
                    2]:  # 判断基因时间是否在时间窗口内
                    for t in range(len(sattimefree[sat]) - 1, -1, -1):  # 在空闲时间窗口中搜索
                        if (sattimefree[sat][t][0] < starttime and sattimefree[sat][t][1] > endtime):  # 有空闲时间窗口可用
                            flag = 0
                            result1.append(city)
                            result2.append(resultga[i])
                            if (starttime - sattimefree[sat][t][0] >= 3):  # 新的时间窗口大于3
                                tmp = copy.deepcopy(sattimefree[sat][t])
                                tmp[1] = starttime
                                sattimefree[sat].insert(t + 1, tmp)  # 插入一个新的窗口（前）
                                flag += 1
                            if (sattimefree[sat][t][1] - nexttime >= 3):
                                tmp = copy.deepcopy(sattimefree[sat][t])
                                tmp[0] = nexttime
                                sattimefree[sat].insert(t + 1 + flag, tmp)
                                flag += 1
                            if (flag != 0):
                                del sattimefree[sat][t]

    i = 0
    for sat in timewindow_ksat:
        for window in timewindow_ksat[sat]:
            plt.barh(y=window[0],width=window[3],left=window[1],color="lightgray")
    for address in result1:
        plt.barh(y=address, width=addresstmp[address][3], left=result2[i][1],color=color[result2[i][0]])
        i+=1
    plt.title('遗传算法下的时间分布')
    plt.show()

def save():
    global address_timewindow
    file_path1 = 'D:/save/single_timewindow.txt'
    file_path2 = 'D:/save/double_timewindow.txt'
    file_path_dir1 = os.path.dirname(file_path1)
    file_path_dir2 = os.path.dirname(file_path2)
    # 判断目录是否存在
    if not os.path.exists(file_path_dir1):
        # 目录不存在创建，makedirs可以创建多级目录
        os.makedirs(file_path_dir1)
    try:
        # 保存数据到文件
        with open(file_path1, 'w', encoding='utf-8') as f:
            for sth in address_timewindow:
                f.write(str(sth))
                f.write('\n')
                for sth2 in address_timewindow[sth]:
                    f.write(str(sth2))
                    f.write('\n')
        return True, '保存成功'
    except Exception as e:
        return False, '保存失败:{}'.format(e)



if __name__ == '__main__':
    dataprocessing()
    cellset = inicell(cellset)
    ui()
