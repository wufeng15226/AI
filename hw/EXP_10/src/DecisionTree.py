import math
import copy
import random
from collections import Counter

# 超参数
MAX_LEFT_DEPTH = 6

# 读入并格式化数据
def load(file_name):
    f = open(file_name,'rt')
    adult_list = f.readlines()
    adult_msg = []
    for i in adult_list:
        curr = i.split(',')
        for j in range(1, len(curr)):
            curr[j] = curr[j][1:] # 去空格
        adult_msg.append(curr)
    # 检查是否有不合规的数据，数据只有最后一行多了一个回车，测试集还有第一行不是数据
    for i in adult_msg:
        if len(i) != 15:
            # print(i)
            adult_msg.remove(i)
    return [i[:-1] for i in adult_msg], [i[-1][:-1] for i in adult_msg] # 这里标签删去了回车符

class node:
    def __init__(self, leaf=False, label=None, attribute=None, son=[]):
        self.leaf = leaf
        self.attribute = attribute
        self.label = label
        self.son = son

    def add_son(self, son):
        if son[1] != None:
            self.son.append(son)

    # for test
    def printinf(self):
        if self.leaf:
            # print("leaf label: "+self.label, end=" ")
            print("leaf", end=" ")
        else:
            print(self.attribute, end=" ")

class DecisionTree:
    def __init__(self, train_data, train_label):
        # 预处理连续值数据
        self.con_attlist = [0, 2, 4, 10, 11, 12]
        # 预处理离散值数据
        tem_dis_list = [1, 3, 5, 6, 7, 8, 9, 13]
        self.dis_attlist = {}
        for j in tem_dis_list:
            self.dis_attlist[j] = list(set([i[j] for i in train_data]))
        # 预处理标签
        self.labelist = list(set(train_label))

    def treeLearn(self, data, label, attributes, entropy=1, option='TD3'):
        # 数据集是否空
        if data == []:
            # 数据缺失时，需要分配叶节点防止出现决策时找不到的情况
            # 策略一，随机，TD3下0.80
            return node(True, self.labelist[random.randint(0,len(self.labelist)-1)])
            # 策略二，硬分配一个，TD3下0.79~0.81
            # return node(True, self.labelist[0])
        # 是否全为同一标签
        same = True
        for i in label[1:]:
            if i != label[0]:
                same = False
                break
        if same:
            return node(True, label[0])
        # 是否没有属性
        if option == 'C4.5':
            # if len(attributes) < 7: # 为7时同id3
            if len(attributes) < MAX_LEFT_DEPTH:
                return node(True, Counter(label).most_common(1)[0][0])
        else: # TD3下变为是否无离散值属性
            flag = False
            for i in attributes:
                if i in self.dis_attlist:
                    flag = True
            if not flag:
                return node(True, Counter(label).most_common(1)[0][0])
        # 一般情况
        Entropys = [(i, self.calEntropy(data, label, i, entropy, option)) for i in attributes]
        if option == 'C4.5': # C4.5下比较增益率
            pickatt, entropy = max(Entropys, key=lambda x: x[1][2])
        else: # 比较信息熵
            pickatt, entropy = min(Entropys, key=lambda x: x[1][0])
        mid_val = entropy[1]
        curr_node = copy.deepcopy(node(False, attribute=pickatt)) # 这里有个bug，需要深复制
        par_map = self.partition(data, label, pickatt, mid_val)
        tem_attributes = copy.deepcopy(attributes)
        tem_attributes.remove(pickatt)
        for i in par_map:
            curr_node.add_son((i, self.treeLearn(par_map[i][0], par_map[i][1], tem_attributes, entropy[0], option)))
        return curr_node

    def calEntropy(self, data, label, attribute, fa_entropy, option='TD3'):
        att_data = [i[attribute] for i in data]
        length = len(data)
        true_label = self.labelist[0]
        sum = 0
        IV = 0
        if attribute in self.con_attlist:
            # print(option)
            if option=='C4.5':
                # 二分法
                att_data = [int(i) for i in att_data]
                max_val = max(att_data)
                min_val = max_val
                for i in att_data:
                    # 考虑到该数据集中有大量无用的0，做了一点优化，效果不大
                    if i != 0 and i < min_val:
                        min_val = i
                mid_val = (max_val+min_val)//2
                true_count = false_count = [0, 0]
                for i in zip(att_data, label):
                    ind = i[0] > mid_val
                    if i[1] == true_label:
                        true_count[ind] += 1
                    else:
                        false_count[ind] += 1
                for i in range(2):
                    ci = true_count[i] + false_count[i]
                    pi = ci / length
                    if true_count[i]:  # 防止出现数学错，这里不会影响熵的结果
                        px = true_count[i] / ci
                        sum += pi * (-px * math.log(px))
                IV -= pi * math.log2(pi) if pi != 0 else 0
                gain_ratio = (fa_entropy - sum) / IV if IV != 0 else 2 # IV小是较好的分类
                return sum, mid_val, gain_ratio                        # 2这里只是一个相对较大的数
            # td3下连续值属性不考虑，直接返回一个较大的熵2
            return 2, None, None
        else:
            true_count = dict([(i, 0) for i in self.dis_attlist[attribute]])
            false_count = dict([(i, 0) for i in self.dis_attlist[attribute]])
            for i in zip(att_data, label):
                if i[1] == true_label:
                    true_count[i[0]] += 1
                else:
                    false_count[i[0]] += 1
            for i in self.dis_attlist[attribute]:
                ci = true_count[i] + false_count[i]
                pi = ci / length
                if true_count[i]: # 防止出现数学错，这里不会影响熵的结果
                    px = true_count[i] / ci
                    sum += pi * (-px*math.log2(px))
                IV -= pi * math.log2(pi) if pi != 0 else 0
                gain_ratio = (fa_entropy - sum) / IV if IV != 0 else 2
            return sum, None, gain_ratio

    def partition(self, data, label, attribute, mid_val):
        par_map = {}
        if attribute in self.dis_attlist:
            for i in self.dis_attlist[attribute]:
                par_map[i] = [[], []]
            for i in range(len(data)):
                par_map[data[i][attribute]][0].append(data[i])
                par_map[data[i][attribute]][1].append(label[i])
        else:
            ind1 = ">"+str(mid_val)
            ind2 = "<="+str(mid_val)
            par_map[ind1] = [[], []]
            par_map[ind2] = [[], []]
            for i in range(len(data)):
                ind = ind1 if int(data[i][attribute])>mid_val else ind2
                par_map[ind][0].append(data[i])
                par_map[ind][1].append(label[i])
        return par_map

# 没有考虑测试集出现训练集中未出现值的情况
    def test(self, root, test_data):
        rst = []
        for i in test_data:
            curr = root
            while(not curr.leaf):
                att = curr.attribute
                val = i[att]
                if att in self.dis_attlist:
                    for j in curr.son:
                        if j[0] == val:
                            curr = j[1]
                            break
                else:
                    num = int(curr.son[0][0][1:])
                    if int(val)>num:
                        curr = curr.son[0][1]
                    else:
                        curr = curr.son[1][1]
            rst.append(curr.label)
        return rst

    # for test
    def printinf(self,root):
        print("root:",end=" ")
        que = []
        que.append(root)
        while(len(que)):
            tem = []
            while(len(que)):
                curr = que[0]
                que.pop(0)
                curr.printinf()
                if not curr.leaf:
                    # print(curr.attribute, end=" ")
                    for i in curr.son:
                        tem.append(i[1])
                # else:
                    # print("leaf",end=" ")
            que = tem
            print("")

def main():
    # pre_train
    train_data, train_label = load('adult.data')
    test_data, test_label = load('adult.test')
    test_label = [i[:-1] for i in test_label] # test_label后面多了一个'.'
    tree = DecisionTree(train_data, train_label)

    # train
    root_1 = tree.treeLearn(train_data, train_label, list(range(14)))
    root_2 = tree.treeLearn(train_data, train_label, list(range(14)),option='C4.5')

    # test
    # DecisionTree.printinf(root)
    rst_label1 = tree.test(root_1, test_data)
    rst_label2 = tree.test(root_2, test_data)
    testlen = len(test_label)
    count1 = count2 = 0
    for i in range(testlen):
        if rst_label1[i] == test_label[i]:
            count1 += 1
        if rst_label2[i] == test_label[i]:
            count2 += 1
    print("  ID3 accuracy: "+str(count1/testlen*100)+"%")
    print(" C4.5 accuracy: "+str(count2/testlen*100)+"%")
    print("with MAX_DEPTH:", 14 - MAX_LEFT_DEPTH)

if __name__ == "__main__":
    main()