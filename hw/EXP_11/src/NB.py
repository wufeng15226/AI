import csv
import math
import numpy as np
from collections import Counter


def load(file_name):
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        rows = []
        for row in reader:
            if row != [] and len(row) == 15:
                tem = []
                for ind, word in enumerate(row):
                    if ind == 0:
                        tem.append(word)
                    elif ind == len(row) - 1 and word[-1]=='.':
                        tem.append(word[1:-1])
                    else:
                        tem.append(word[1:])
                rows.append(tem)
        return  rows


def load_attributes(file_name):
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader if row != []]
        attributes = {}
        con_list = []
        dis_map = {}
        for row in rows:
            if row[0][0] != '|':
                row[-1] = row[-1][:-1]
                if row[0].find(':') == -1:
                    labels = row
                else:
                    tem = row[0].split(':')
                    attribute = tem[0]
                    row[0] = tem[1]
                    attributes[attribute] = [word[1:] for word in row]
        for ind, (attribute, val) in enumerate(attributes.items()):
            if val == ['continuous']:
                con_list.append(ind)
            else:
                dis_map[ind] = val
        return labels, con_list, dis_map


class NB():
    def __init__(self, labels, con_list, dis_map, train):

        train_data = [i[:-1] for i in train]
        train_label = [i[-1] for i in train]

        # 处理标签
        self.label_cpt = {}
        count = Counter(train_label)
        data_size = len(train)
        for i in count:
            self.label_cpt[i] = count[i]/data_size

        # 处理连续数据
        self.con_list = {}
        for i in con_list:
            for j in self.label_cpt:
                # self.con_list[(i,j)] = (np.mean([float(k[i]) for k in train if int(k[i]) != 0 and k[-1] == j]), math.sqrt(np.var([float(k[i]) for k in train if int(k[i]) != 0  and k[-1] == j])))
                self.con_list[(i,j)] = (np.mean([float(k[i]) for k in train if k[-1] == j]), math.sqrt(np.var([float(k[i]) for k in train if k[-1] == j])))
        # 处理离散数据
        self.dis_cpt = {}
        for i in dis_map:
            count = dict(Counter([j[i] for j in train_data]))
            unknow = count.get('?', 0)
            for j in count:
                if j != '?':
                    count[j] = count[j] / (data_size - unknow)
            for j in dis_map[i]:
                if count.get(j, "") == "":
                    count[j] = 0
            if count.get('?', "") != "":
                count.pop('?')
            self.dis_cpt[i] = count

    def test(self, test_data):
        rst = []
        # print(self.con_list)
        for test in test_data:
            ph = {}
            for label in self.label_cpt:
                ph[label] = self.label_cpt[label]
                for ind, i in enumerate(test):
                    if ind not in [k[0] for k in self.con_list]:
                        if i != '?':
                            ph[label] *= self.dis_cpt[ind][i]
                        else:
                            ph[label] *= max(self.dis_cpt[ind].items(), key=lambda x:x[1])[1]
                    else:
                        if float(i) != 0:
                            u = self.con_list[(ind,label)][0]
                            sig = self.con_list[(ind,label)][1]
                            ph[label] *= np.exp(-(float(i) - u) ** 2 /(2* sig **2))/(math.sqrt(2*math.pi)*sig)
                        # else:
                        #     sig = self.con_list[(ind, label)][1]
                        #     ph[label] *= np.exp(0) / (math.sqrt(2 * math.pi) * sig)
            rst.append(max(ph.items(), key=lambda x:x[1])[0])
        return rst

def main():
    train = load('dataSet/adult.data')
    labels, con_list, dis_map = load_attributes('dataSet/adult.names')

    nb = NB(labels, con_list, dis_map, train)

    test = load('dataSet/adult.test')
    test_label = nb.test([i[:-1] for i in test])
    length = len(test)
    count = 0
    for i in zip(test_label, [i[-1] for i in test]):
        if i[0]==i[1]:
            count += 1
    print("Accuracy:", count/length)


if __name__== "__main__":
    main()