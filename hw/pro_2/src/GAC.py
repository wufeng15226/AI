#  -*-  coding:utf-8  -*-
import copy
import sys
import time
import numpy as np
from timeit import default_timer as timer

def load(i):
    file = open("data" + str(i) + ".txt", 'r')
    msg = []
    for i in file:
        tem = []
        for j in i:
            if j != ' ' and j != '\n':
                tem.append(j)
        msg.append(tem)
    # print(msg)
    maps = []
    less_constraints = []
    for i in range(len(msg[0])):
        tem = []
        for j in msg[i]:
            tem.append(int(j))
        maps.append(tem)
    for i in range(len(msg) - len(msg[0])):
        tem = []
        for j in msg[len(msg[0]) + i]:
            tem.append(int(j))
        less_constraints.append(tem)
    return maps, less_constraints
    file.close()

def show(maps):
    for i in maps:
        for j in i:
            print(j, end='')
            print(' ', end='')
        print()
    print()

def show_cst(less_constraints):
    for i in less_constraints:
        print('('+str(i[0])+","+str(i[1])+")<("+str(i[2])+","+str(i[3])+")")
    print()

def show_domain(domain):
    # print(domain)
    size = len(domain[0])
    for i in range(size):
        for j in range(size):
            print('(' + str(i) + "," + str(j) + "):", end=' ')
            if not len(domain[i][j]):
                print("Empty",end='')
            for k in domain[i][j]:
                print(k, end=' ')
            print(";", end=' ')
        print()
    print()

class Forward_Checking:
    def __init__(self, maps, less_constraints):
        self.maps = maps
        self.less_constraints = []
        for i in less_constraints:
            self.less_constraints.append(((i[0],i[1]),(i[2],i[3])))
        self.domain = []
        self.size = len(maps[0])
        self.nodes = 0
        self.inference = 0
        # 根据maps初始化域
        for i in range(self.size):
            tem = []
            for j in range(self.size):
                if self.maps[i][j]:
                    tem.append([self.maps[i][j]])
                else:
                    tem.append(list(range(1, self.size + 1))) #range是不可变list，不能使用remove
            self.domain.append(tem)
        # 初始化即进行FC_Check
        for i in range(self.size):
            for j in range(self.size):
                self.FC_Check(i, j)

    def FC_Check(self, i, j):
        if self.maps[i][j]: # 未填值不检查
            val = self.maps[i][j]
        else:
            return [[], True]
        begin = timer()
        tem = []
        # 根据已填的值筛去行列中的变量域值
        for m in range(self.size):
            if m != j and val in self.domain[i][m]:
                self.domain[i][m].remove(val)
                tem.append((i,m,val))
            if m != i and val in self.domain[m][j]:
                self.domain[m][j].remove(val)
                tem.append((m,j,val))
        # 根据已填的值及约束筛去约束中的变量域值
        for m in self.less_constraints:
            if (i, j) == m[0]:
                for k in range(1, self.maps[i][j]):
                    if k in self.domain[m[1][0]][m[1][1]]:
                        self.domain[m[1][0]][m[1][1]].remove(k)
                        tem.append((m[1][0],m[1][1],k))
            if (i, j) == m[1]:
                for k in range(self.maps[i][j] + 1, self.size + 1):
                    if k in self.domain[m[0][0]][m[0][1]]:
                        self.domain[m[0][0]][m[0][1]].remove(k)
                        tem.append((m[0][0],m[0][1],k))
        # 检查是否有空集
        empty = False
        for m in range(self.size):
            if not empty:
                for n in range(self.size):
                    if self.domain[m][n] == []:
                        empty = True
                        break
        end = timer()
        self.inference += end - begin
        return [tem, not empty]

    def FC(self, i, j):
        self.nodes += 1
        if i==self.size-1 and j ==self.size-1: # 终止
            if not self.maps[i][j]: # 无值时设定值
                self.maps[i][j] = self.domain[i][j][0]
            return True
        ni = i + (j + 1) // self.size
        nj = (j + 1) % self.size
        if self.maps[i][j]: # 已有值
            return self.FC(ni, nj)
        tem = copy.deepcopy(self.domain[i][j])
        for val in tem:
            rst = self.FC_Set(i, j, val) #rst第一个元素是被删除的域值（三元组的列表，位置+值），第二个元素是T/F
            if rst[1] and self.FC(ni, nj):
                return True
            self.FC_Reset(i, j, rst[0])
        return False

    def FC_Set(self, i, j, val):
        tem = []
        self.maps[i][j] = val
        for k in self.domain[i][j]:
            if k != val:
                self.domain[i][j].remove(k)
                tem.append((i,j,k))
        rst = self.FC_Check(i ,j)

        return [tem + rst[0], rst[1]]

    def FC_Reset(self,i, j,tem):
        self.maps[i][j] = 0
        for i in tem:
            self.domain[i[0]][i[1]].append(i[2])

class Generalized_Arc_Consistency:
    def __init__(self, maps, less_constraints):
        self.size = len(maps[0])
        self.maps = maps
        self.less_constraints = []
        self.cons_index = {}
        self.que = []
        self.nodes = 0
        self.inference = 0
        for i in range(self.size):
            for j in range(self.size):
                self.cons_index[(i, j)] = []
        # 添加约束表和约束索引
        for i in less_constraints:
            self.less_constraints.append((0, (i[0], i[1]), (i[2], i[3]))) # 不等式约束为三元组(0, (i1, j1), (i2, j2))
            self.cons_index[(i[0], i[1])].append(((i[0], i[1]), (i[2], i[3]))) # 索引下标为位置元组(i, j)， 返回值为一列表
            self.cons_index[(i[2], i[3])].append(((i[0], i[1]), (i[2], i[3])))
        self.domain = []
        self.size = len(maps[0])
        # 根据maps初始化域
        for i in range(self.size):
            tem = []
            for j in range(self.size):
                if self.maps[i][j]:
                    tem.append([self.maps[i][j]]) # 被赋值后域内仅一个值
                else:
                    tem.append(list(range(1, self.size + 1)))  # range是不可变list，不能使用remove
            self.domain.append(tem)
        # 初始化进行一次全面的GAC_Enforce
        self.add_all_cons()
        self.GAC_Enforce()

    def add_all_cons(self):
        for i in range(self.size):
            for j in range(self.size):
                self.add_cons_pos(i, j)

    def add_cons_pos(self, i, j):
        for c in self.cons_index[(i, j)]:  # 添加不等式约束
            self.add_cons((0, c[0], c[1]))
        self.add_cons((i + 1, -(j + 1))) # 添加不等约束
        self.add_cons((-(i + 1), j + 1))

    def add_cons(self, cons):
        if cons in self.que:
            return
        else:
            self.que.append(cons)

    def check_empty(self, i ,j):
        if self.domain[i][j] == []:
            self.que = []
            return True
        return False

    def check_end(self):
        count = 0
        hold = []
        for i in range(self.size):
            for j in range(self.size):
                if not self.maps[i][j]:
                    count += 1
                    hold.append((i,j))
                    if count > 1:
                        return False
        i,j = hold[0][0],hold[0][1]
        self.maps[i][j] = self.domain[i][j][0]
        return True

    def min_domain_branch(self):
        # 选取最小域的变量拓展
        size = 1
        while(1):
            for i in range(self.size):
                for j in range(self.size):
                    if not self.maps[i][j]:
                        if size == len(self.domain[i][j]):
                            return i, j
            size += 1

    def GAC_Enforce(self):
        begin = timer()
        del_list = []
        empty = False
        while(self.que):
            curr = self.que[0]
            if curr[0] == 0: # 不等式约束
                v1 = curr[1]
                v2 = curr[2]
                if not empty and not self.maps[v1[0]][v1[1]]: # 对第一个变量，未赋值才考虑
                    tem = copy.deepcopy(self.domain[v1[0]][v1[1]])
                    for i in tem:
                        satisfy = False
                        for j in self.domain[v2[0]][v2[1]]:
                            if i < j:
                                satisfy = True
                                break
                        if not satisfy:
                            self.domain[v1[0]][v1[1]].remove(i)
                            # print((v1[0], v1[1], i))
                            del_list.append((v1[0], v1[1], i))
                            if self.check_empty(v1[0], v1[1]):
                                empty = True
                                break
                            self.add_cons_pos(v1[0], v1[1])
                if not empty and not self.maps[v2[0]][v2[1]]:  # 对第二个变量，未赋值才考虑
                    tem = copy.deepcopy(self.domain[v2[0]][v2[1]])
                    for j in tem:  # 对第二个变量
                        satisfy = False
                        for i in self.domain[v1[0]][v1[1]]:
                            if i < j:
                                satisfy = True
                                break
                        if not satisfy:
                            self.domain[v2[0]][v2[1]].remove(j)
                            # print((v2[0],v2[1],j))
                            del_list.append((v2[0], v2[1], j))
                            if self.check_empty(v2[0], v2[1]):
                                empty = True
                                break
                            self.add_cons_pos(v2[0], v2[1])
            else:
                if curr[0] < 0: #行约束
                    i = -curr[0] - 1
                    j = curr[1] - 1
                    if not self.maps[i][j]: # 每个未赋值变量
                        tem = copy.deepcopy(self.domain[i][j])
                        for p in tem: # 每个可能值
                            if not empty:
                                for k in range(self.size):  # 行内每一个位置
                                    if k != j:  # 自己不和自己比
                                        flag = False
                                        for m in self.domain[i][k]:
                                            if p != m:  # 找到一个可能值
                                                flag = True
                                                break
                                        if not flag:
                                            self.domain[i][j].remove(p)
                                            del_list.append((i, j, p))
                                            if self.check_empty(i, j):
                                                empty = True
                                                break
                                            self.add_cons_pos(i, j)
                                            break
                    for k in range(self.size): # 检查行内其它变量
                        if not empty and k != j and not self.maps[i][k]:
                            tem = copy.deepcopy(self.domain[i][k])
                            for p in tem:
                                flag = False
                                for m in self.domain[i][j]:
                                    if p != m:
                                        flag = True
                                        break
                                if not flag:
                                    self.domain[i][k].remove(p)
                                    del_list.append((i, k, p))
                                    if self.check_empty(i, k):
                                        empty = True
                                        break
                                    self.add_cons_pos(i, k)
                                    break
                else: # 列约束
                    i = curr[0] - 1
                    j = -curr[1] - 1
                    if not self.maps[i][j]:  # 每个未赋值变量
                        tem = copy.deepcopy(self.domain[i][j])
                        for p in tem:  # 每个可能值
                            if not empty:
                                for k in range(self.size):  # 行内每一个位置
                                    if k != i:  # 自己不和自己比
                                        flag = False
                                        for m in self.domain[k][j]:
                                            if p != m:  # 找到一个可能值
                                                flag = True
                                                break
                                        if not flag:
                                            self.domain[i][j].remove(p)
                                            del_list.append((i, j, p))
                                            if self.check_empty(i, j):
                                                empty = True
                                                break
                                            self.add_cons_pos(i, j)
                                            break
                    for k in range(self.size): # 检查列内其它变量
                        if not empty and k != i and not self.maps[k][j]:
                            tem = copy.deepcopy(self.domain[k][j])
                            for p in tem:
                                flag = False
                                for m in self.domain[i][j]:
                                    if p != m:
                                        flag = True
                                        break
                                if not flag:
                                    self.domain[k][j].remove(p)
                                    del_list.append((k, j, p))
                                    if self.check_empty(k, j):
                                        empty = True
                                        break
                                    self.add_cons_pos(k, j)
                                    break
            if not empty:
                self.que.remove(curr)
        end = timer()
        self.inference += end - begin
        return [del_list, not empty]

    def GAC(self, i, j):
        self.nodes += 1
        if self.check_end():
            return True
        # original version
        # if i==self.size-1 and j ==self.size-1: # 终止
        #     if not self.maps[i][j]: # 无值时设定值
        #         self.maps[i][j] = self.domain[i][j][0]
        #     return True
        # ni = i + (j + 1) // self.size
        # nj = (j + 1) % self.size
        ni,nj = self.min_domain_branch()

        if self.maps[i][j]: # 已有值
            return self.GAC(ni, nj)
        tem = copy.deepcopy(self.domain[i][j])
        for val in tem:
            rst = self.GAC_Set(i, j, val) #rst第一个元素是被删除的域值（三元组列表，位置+值），第二个元素是T/F
            if rst[1]:
                if self.GAC(ni, nj):
                    return True
            self.GAC_Reset(i, j, rst[0])
        return False

    def GAC_Set(self, i, j, val):
        self.maps[i][j] = val
        del_list = []
        tem = copy.deepcopy(self.domain[i][j])
        for m in tem:
            if m != val:
                self.domain[i][j].remove(m)
                del_list.append((i,j,m))

        self.add_cons_pos(i, j)
        rst = self.GAC_Enforce()
        return [del_list + rst[0],rst[1]]

    def GAC_Reset(self, i, j, tem):
        self.maps[i][j] = 0
        for k in tem:
            self.domain[k[0]][k[1]].append(k[2])

def GAC_Test(maps, less_constraints):
    GAC_begin = timer()
    gac = Generalized_Arc_Consistency(maps, less_constraints)
    rst = gac.GAC(0, 0)
    GAC_end = timer()
    show(gac.maps)
    print("GAC Total Time:", GAC_end - GAC_begin, 's')
    print('Number of Nodes Searched:', gac.nodes)
    print("Average Inference Time Per Node: ", gac.inference/gac.nodes*1000, 'ms')
    print()
    print()

def FC_Test(maps, less_constraints):
    FC_begin = timer()
    fc = Forward_Checking(maps, less_constraints)
    rst = fc.FC(0, 0)
    FC_end = timer()
    show(fc.maps)
    print("FC Total Time:", FC_end - FC_begin, 's')
    print('Number of Nodes Searched:', fc.nodes)
    print("Average Inference Time Per Node: ", fc.inference/fc.nodes*1000, 'ms')
    print()
    print()

def main():
    if sys.argv[1] == 'test_all': # 一次性测试
        for i in range(1,6):
            maps, less_constraints = load(i)
            show(maps)
            tem = copy.deepcopy(maps)
            GAC_Test(maps, less_constraints)
            FC_Test(tem, less_constraints)
    else: # 单次测试
        maps, less_constraints = load(int(sys.argv[2]))
        show(maps)
        tem = copy.deepcopy(maps)
        if sys.argv[1] == 'gac':
            GAC_Test(maps, less_constraints)
        elif sys.argv[1] == 'fc':
            FC_Test(maps, less_constraints)
        elif sys.argv[1] == 'cmp':
            GAC_Test(maps, less_constraints)
            FC_Test(tem, less_constraints)

if __name__ == "__main__":
    main()