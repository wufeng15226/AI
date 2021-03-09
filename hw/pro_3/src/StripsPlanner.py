import re
import copy
from timeit import default_timer as timer

# 测试时使用的，实际上搜索树很浅
MAX_DEPTH = 50

def parser(file_name):
    str = open(file_name, 'r').read()

    # https://github.com/pucrs-automated-planning/pddl-parser/blob/master/PDDL.py
    stack = []
    list = []
    for t in re.findall(r'[()]|[^\s()]+', str):
        if t == '(':
            stack.append(list)
            list = []
        elif t == ')':
            if stack:
                l = list
                list = stack.pop()
                list.append(l)
            else:
                raise Exception('Missing open parentheses')
        else:
            list.append(t)
    return list[0]

class Action:
    def __init__(self, init_list, types):
        self.name = init_list[1]
        self.parameters = {}

        if types != ['AnyType']:
            for i in range(0, len(init_list[3]), 3):
                if init_list[3][i+2] in types:
                    self.parameters[init_list[3][i][1:]] = init_list[3][i + 2]
        else:
            for i in init_list[3]:
                self.parameters[i[1:]] = 'AnyType'
        self.precondition = []
        for i in init_list[5]:
            if type(i) is list:
                if i[0] != 'not':
                    self.precondition.append([True, [i[0]] + [j[1:] for j in i[1:]]])
                else:
                    self.precondition.append([False, [i[1][0]] + [j[1:] for j in i[1][1:]]])
        self.effect = []
        for i in init_list[7]:
            if type(i) is list:
                if i[0] != 'not':
                    self.effect.append([True, [i[0]] + [j[1:] for j in i[1:]]])
                else:
                    self.effect.append([False, [i[1][0]] + [j[1:] for j in i[1][1:]]])

    # 寻找可能的动作实例，返回 [[动作名, add_list, del_list]...]
    # 一种动作也有多种可能，这个bug找了一年
    def do(self, objects, kb):
        rst = []
        mapping_list = []
        self.crearte_mapping(objects, {}, 0, mapping_list)
        for i in mapping_list:
            precondition = self.assign_precondition(i)
            flag = True
            for j in precondition:
                if (j[0] and j[1] not in kb) or (not j[0] and j[1] in kb):
                    flag = False
                    break
            if flag:
                rst.append(self.assign_effect(i))
        return rst

    # 启发式函数的辅助，返回 [[肯定的precondition, add]...]
    def relax_do(self, objects, kb):
        rst = []
        mapping_list = []
        self.crearte_mapping(objects, {}, 0, mapping_list)
        for i in mapping_list:
            precondition = self.assign_precondition(i)
            flag = True
            for j in precondition:
                if (j[0] and j[1] not in kb) or (not j[0] and j[1] in kb):
                    flag = False
                    break
            if flag:
                pre = []
                for j in range(len(precondition)):
                    if precondition[j][0]:
                        pre.append(precondition[j][1])
                rst.append([pre, self.assign_effect(i)[1]])
        return rst

    # 创建对象间的映射以实现实例化，返回映射的列表
    def crearte_mapping(self, objects, curr, depth, rst):
        if depth == len(self.parameters):
            rst.append(copy.deepcopy(curr))
            return
        ind, val = list(self.parameters.items())[depth]
        for i in objects[val]:
            if i not in curr.values(): # 不能反复用，可能会有问题
                curr[ind] = i
                self.crearte_mapping(objects, curr, depth+1, rst)
                curr.pop(ind)

    # 实例化条件
    def assign_precondition(self, mapping):
        precondition = copy.deepcopy(self.precondition)
        for i in range(len(precondition)):
            for j in range(1, len(precondition[i][1])):
                precondition[i][1][j] = mapping[precondition[i][1][j]]
        return precondition

    # 实例化效果
    def assign_effect(self, mapping):
        effect = copy.deepcopy(self.effect)
        add = []
        delete = []
        for i in range(len(effect)):
            for j in range(1, len(effect[i][1])):
                effect[i][1][j] = mapping[effect[i][1][j]]
            if effect[i][0]:
                add.append(effect[i][1])
            else:
                delete.append(effect[i][1])
        return [[self.name]+list(mapping.values()), add, delete]

    def printInfo(self):
        print("\t{" + self.name + "}")
        print("\tparameters:", self.parameters)
        print("\tprecondition:", self.precondition)
        print("\teffect:", self.effect)


class Strips:
    def __init__(self, domain_filename, problem_filename):
        domain = parser(domain_filename)
        problem = parser(problem_filename)
        self.types = ['AnyType']  # 没有类型时
        self.actions = []
        for i in domain:
            if type(i) is list:
                if i[0] == ':types':
                    self.types = i[1:]
                if i[0] == ':action':
                    self.actions.append(Action(i, self.types))
        self.objects = {}
        object = problem[3][1:]
        tail = 0
        if self.types != ['AnyType']:
            for ind, i in enumerate(object):
                if i == '-':
                    self.objects[object[ind+1]] = object[tail:ind]
                    tail = ind + 2
        else:
            self.objects['AnyType'] = object
        self.kb = problem[4][1:]
        self.goal = []
        goal = problem[5][1][1:]
        for i in goal:
            if i[0] != 'not':
                self.goal.append([True, i])
            else:
                self.goal.append([False, i[1:]])
        self.path = []

    # 解决问题，返回拓展结点数和路径
    def search(succ):
        if len(succ) == 0:
            return 1, []
        state, action, effect = min(succ, key=lambda x: x[2][3]+x[2][4])
        if effect[3] > MAX_DEPTH: # 限制深度
            return 1, []
        succ.remove((state, action, effect))
        state.step(effect)
        if state.achive():
            return 1, state.path
        for i in state.observe():
            if not Strips.inverse(effect, i[2]): # 组织搜索在两点间反复踏步
                succ.append(i)
            # succ.append(i)

        rst = Strips.search(succ)
        return rst[0]+1, rst[1]

    # 观察周围，获取动作信息，返回[(状态, 动作, [动作名, add_list, del_list, g, h])...]
    def observe(self):
        tem = []
        for i in self.actions:
            for can in i.do(self.objects, self.kb):
                can.append(len(self.path))  # g
                h = self.heuristic(can)
                can.append(self.heuristic(can)) # h
                tem.append((copy.deepcopy(self), i, can))
        return tem

    # 应用 reachability_analysis 和 count_actions，返回h
    def heuristic(self, action):
        curr_state = copy.deepcopy(self)
        curr_state.step(action)
        state_layer = [copy.deepcopy(curr_state.kb)]
        action_layer = []
        new_to_pre = {}
        while(not curr_state.achive()):
            actions = []
            for i in curr_state.actions:
                for can in i.relax_do(curr_state.objects, curr_state.kb):
                    can.append(i)
                    actions.append(can) # (pre, add, action)
            action_layer.append(copy.deepcopy(actions))
            for i in actions:
                for j in i[1]:
                    if j not in curr_state.kb:
                        new_to_pre[str(tuple(j))] = i
                        curr_state.kb.append(j)
            if curr_state.kb == state_layer[-1]: # kb不再变化
                return 100
            state_layer.append(copy.deepcopy(curr_state.kb))
        state_layer = [ [tuple(j) for j in i] for i in state_layer]

        return Strips.count_acts(new_to_pre, state_layer, action_layer, curr_state.goal, state_layer[-1])

    # 利用递归来h
    def count_acts(new_to_pre, state_layer, action_layer, G, S):
        if len(state_layer) == 1:
            return 0
        state_layer.remove(S)
        s1 = set(S)
        s2 = set(state_layer[-1])
        Gp = s1 & s2
        Gn = s1 - s2
        A = []
        for i in Gn:
            action = new_to_pre[str(i)]
            if action[2] not in A:
                A.append(action[2])
                Gp = Gp | set([tuple(j) for j in action[0]])
        return Strips.count_acts(new_to_pre, state_layer, action_layer, Gp, state_layer[-1]) + len(A)

    # 行动
    def step(self, action):
        self.path.append(action[0])
        for i in action[1]: # add
            self.kb.append(i)
        for i in action[2]: # del
            self.kb.remove(i)

    # 判断是否达到目标
    def achive(self):
        for i in self.goal:
            if not i[0]: # 否定的目标
                for j in self.kb:
                    if j == i[1]:
                        return False
            else: # 肯定的目标
                for j in self.kb:
                    find = False
                    if j == i[1]:
                        find = True
                        break
                if not find:
                    return False
        return True

    # 检查互逆动作以提升搜索效率
    def inverse(effect1, effect2):
        if effect1[0][0] != effect2[0][0]:
            return False
        for i in effect1[1]:
            if i not in effect2[2]:
                return False
        for i in effect2[1]:
            if i not in effect1[2]:
                return False
        return True

    def printInfo(self):
        print("{domain}")
        print("types:", self.types)
        print("actions: ")
        for curr in self.actions:
            curr.printInfo()
        print("{problem}")
        print("objects:", self.objects)
        print("kb:", self.kb)
        print("goal:", self.goal)
        print()

def test(num):
    # str1, str2 = load(num)
    # strips = Strips(str1, str2)
    perfix = "pddl/test" + str(num) + "/test" + str(num)
    strips = Strips(perfix + "_domain.pddl", perfix + "_problem.pddl")
    begin = timer()
    count, path = Strips.search(strips.observe())
    end = timer()
    length = len(path)
    print("{test "+str(num)+"}")
    print()
    print("ANSWER:",end=" ")
    for i in range(length):
        print(path[i],end="->" if i != length-1 else "")
        if (i+1) % 3 == 0 and i != length-1:
            print("\n\t",end="")
    print()
    print("Time Cost: "+str(end-begin)+"s")
    print("Node Expended:", count)
    print()

def main():
    for i in range(5):
        test(i)

if __name__== "__main__":
    main()