#  -*-  coding:utf-8  -*-
import sys
import re
import copy
import numpy as np

# 助教的代码，把¬改为了!，在每个子句前加上了序号成为新的列表
def deal(kb):
    clauses = []
    id = 1
    for i in kb:
        clause = []
        for item in re.findall(r'!*[a-zA-Z]+\([a-zA-Z,\s]*\)', i):
            items = re.findall(r'[!a-zA-Z]+', item)
            clause.append(items)
        clauses.append(clause)
        id += 1
    # print(clauses)
    return clauses

def load(i):
    file = open("kb" + str(i) + ".txt", 'r')
    kb = []
    for i in file:
        # print(i)
        kb.append(i)
    file.close()
    clauses = deal(kb)
    return clauses

def show(clauses):
    id = 1
    for i in clauses:
        print(id,":", i)
        id += 1

def val(str):
    # print(str)
    return len(str)==1

def clause_val(clause):
    length = len(clause)
    # print(length)
    for i in range(1, length):
        # print(i)
        if val(clause[i]):
            return True
    return False

def solve_end(clause1, clause2):
    # 两个单谓词项才有很可能结束
    c1 = clause1[0]
    c2 = clause2[0]
    if len(clause1)==1 and len(clause2)==1 and not clause_val(c1) and not clause_val(c2) and (('!' + c1[0]) == c2[0] or c1[0] == ('!' + c2[0])):
        for i in range(1, len(c1)):
            if c1[i] != c2[i]:
                return False
        return True
    return False

def MGU(clause_a, clause_b):
    # 不改原 kb
    clause1 = copy.deepcopy(clause_a)
    clause2 = copy.deepcopy(clause_b)
    sub_sigma = []
    new_clause = []
    len_1 = len(clause1)
    len_2 = len(clause2)
    pop_list = [] # 存应该被删去的谓词
    # 遍历两子句每一个谓词
    for i in range(len_1):
        for j in range(len_2):
            # i 不可能被反复合一，但j有可能会，需要考虑
            if clause2[j] in [k[1] for k in pop_list]:
                continue
            pre_1 = clause1[i][0]
            pre_2 = clause2[j][0]
            # 谓词差一个‘!’才考虑合一
            if (('!'+pre_1)==pre_2 or pre_1==('!'+pre_2)):
                # 若两谓词有不相等的对应项，不能合一
                flag = True
                for pos in range(1, len(clause1[i])):
                    str1 = clause1[i][pos]
                    str2 = clause2[j][pos]
                    if not val(str1) and not val(str2) and str1 != str2:
                        flag = False
                        break
                if not flag:
                    continue
                # 开始合一
                for pos in range(1, len(clause1[i])):
                    str1 = clause1[i][pos]
                    str2 = clause2[j][pos]
                    if str1 != str2: # 相等则不处理
                        if val(str1): # 子句1中的文字为变量，不论子句2中是什么都直接赋值
                            # 三元组，0表示子句0，1表示子句1；谓词位置；变化关系
                            sub_sigma.append([i, j, str1 + '=' + str2])
                            # 赋值
                            for m in range(len_1):
                                for n in range(1, len(clause1[m])):
                                    if clause1[m][n] == str1:
                                        clause1[m][n] = str2
                        elif val(str2):
                            sub_sigma.append([i, j, str2 + '=' + str1])
                            for m in range(len_2):
                                for n in range(1, len(clause2[m])):
                                    if clause2[m][n] == str2:
                                        clause2[m][n] = str1
                # 这两个子句已经互反了，把他们放到删除列表中
                pop_list.append((clause1[i], clause2[j]))
                break
    if sub_sigma == []: # 完全不能合一
        new_clause = []
    else:
        for i in pop_list:
            clause1.remove(i[0])
            clause2.remove(i[1])
        new_clause = clause1
        # 此处有bug，子句有可能一样，要一个一个添加
        for m in clause2:
            if m not in new_clause:
                new_clause.append(m)
    return new_clause, sub_sigma

def show_pros(ori_len, out, clauses):
    id = ori_len + 1
    map = {}
    for i in range(ori_len+1):
        map[i] = i+1
    for i in range(len(out)):
        s3 = str(out[i][5])
        s4 = str(clauses[out[i][0]])
        print()
        # ori_id output version
        # s1 = str(out[i][1]+1) + str("" if len(clauses[out[i][1]]) == 1 else chr(ord('a') + out[i][3]))
        # s2 = str(out[i][2]+1) + str("" if len(clauses[out[i][2]]) == 1 else chr(ord('a') + out[i][4]))
        # print("%d. R[%s,%s]%s   %s" % (out[i][0] + 1, s1, s2, s3, s4))
        s5 = str(map[out[i][1]]) + str("" if len(clauses[out[i][1]]) == 1 else chr(ord('a') + out[i][3]))
        s6 = str(map[out[i][2]]) + str("" if len(clauses[out[i][2]]) == 1 else chr(ord('a') + out[i][4]))
        print("%d. R[%s,%s]%s   %s" % (id, s5, s6, s3, s4))
        map[out[i][0]] = id
        id += 1

def pick_min(j_list, clauses):
    # print(j_list)
    length = len(j_list)
    size = 1
    while(1):
        pos = 0
        while (pos < length):
            j = j_list[pos]
            if len(clauses[j]) == size:
                j_list.pop(pos)
                return j
            pos += 1
        size += 1

def test(num):
    clauses = load(num)
    show(clauses)
    rst = []
    out = []
    que = []
    for i in range(len(clauses)):
        rst.append((i,-1,-1,-1,-1,[])) # 规则索引,i,j,a,b,变换
    ori_len = len(clauses)
    id = len(clauses)
    flag = False
    while(not flag):
        length = len(clauses)
        hold = []
        for i in range(length):
            if not flag:
                j_list = list(range(i+1, length))
                while(j_list):
                    j = pick_min(j_list, clauses)
                    new_clause, curr_sigma = MGU(clauses[i], clauses[j])
                    # 结束
                    if solve_end(clauses[i], clauses[j]):
                        hold.append([])
                        rst.append((id,i,j,0,0,[]))
                        que.append((id,i,j,0,0,[]))
                        id += 1
                        flag = True
                        break
                    # 有效合一
                    if new_clause != [] and new_clause not in clauses and new_clause not in hold:
                        hold.append(new_clause)
                        # 添加推理规则链
                        rst.append((id,i,j,curr_sigma[0][0],curr_sigma[0][1],[k[2] for k in curr_sigma]))
                        id += 1
        if hold == []:
            break
        clauses += hold
    # 层序遍历,找回推理依据
    while(que):
        hold = []
        while(que):
            curr = que.pop(0)
            if curr[1] != -1:
                out.append(curr)
            else:
                continue
            hold.append(rst[curr[2]])
            hold.append(rst[curr[1]])
        que = hold
    out = out[::-1]
    if flag:
        show_pros(ori_len, out, clauses)
    else:
        print("KB is Satisfiable.")

def main():
    DAT_NUM = 3
    if len(sys.argv) == 1:
        for i in range(DAT_NUM):
            print("TEST: ",i)
            test(i)
            print()
            print()
    else:
        test(int(sys.argv[1]))

if __name__ == "__main__":
    main()