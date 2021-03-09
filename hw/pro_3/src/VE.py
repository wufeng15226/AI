import copy
import random
import numpy as np
from timeit import default_timer as timer
num = 0

class VariableElimination:
    def printFactors(factorList):
        for factor in factorList:
            factor.printInf()

    def default_order(list, factorList):
        hold = []
        for i in list:
            hold.append(i)
            yield i
        print("default order:", hold)

    def random_order(list, factorList):
        length = len(list)
        hold = []
        for i in range(length):
            pick = random.choice(list)
            list.remove(pick)
            hold.append(pick)
            yield pick
        print("random order:", hold)

    def min_fill(list, factorList):
        pass

    def min_neighber(list, factorList):
        length = len(list)
        hold = []
        for i in range(length):
            var_list = [j.varList for j in factorList if len(j.varList)]
            pick = random.choice(min(var_list, key=len))
            hold.append(pick)
            yield pick
        print("min-neighber:", hold)

    def min_weight(list, factorList):
        length = len(list)
        hold = []
        for i in range(length):
            var_map = dict(zip(list, [0]*(length-i)))
            for node in factorList:
                for var in node.varList:
                    if var in list:
                        var_map[var] += 1
            pick = min(var_map.items(), key=lambda x: x[1])[0]
            hold.append(pick)
            list.remove(pick)
            yield pick
        print("min-weight:", hold)

    def inference(factorList, queryVariables,
    orderedListOfHiddenVariables, evidenceList, queryVal, f):
        for ev in evidenceList:
            #Your code here
            for pos, factor in enumerate(factorList):
                factorList[pos] = factor.restrict(ev, str(evidenceList[ev])) # 注意这里需要转成 str
        print()
        width = 0
        for var in f(orderedListOfHiddenVariables, factorList):
            #Your code here
            temList= []
            for pos, factor in enumerate(factorList):
                if var in factor.varList:
                    temList.append(factor)
            for factor in temList:
                factorList.remove(factor)
            curr = temList[0]
            for i in temList[1:]:
                curr = curr.multiply(i)
            curr = curr.sumout(var)
            factorList.append(curr)
            if factorList != []:
                # 消除宽为最大超图大小
                max_width = max([len(i.varList) for i in factorList])
                width = width if max_width <= width else max_width
        print("WIDTH:", width)
        print("RESULT:")
        res = factorList[0]
        for factor in factorList[1:]:
            res = res.multiply(factor)
        total = sum(res.cpt.values())
        res.cpt = {k: v/total for k, v in res.cpt.items()}
        # res.printInf()
        print(res.cpt[queryVal])

class Util:
    def lfind(l, val):
        for pos, i in enumerate(l):
            if i==val:
                return pos
        return -1

class Node:
    def __init__(self, name, var_list):
        self.name = name
        self.varList = var_list
        self.cpt = {}
    def setCpt(self, cpt):
        self.cpt = cpt
    def printInf(self):
        print("Name = " + self.name)
        print(" vars " + str(self.varList))
        for key in self.cpt:
            print("   key: " + str(key) + " val : " + str(self.cpt[key]))
        print()
    def multiply(self, factor):
        """function that multiplies with another factor"""
        #Your code here
        newList = list(set(self.varList+factor.varList))
        length = len(newList)
        new_cpt = {}
        if self.varList == []:
            for key, val in factor.cpt.items():
                new_cpt[key] = val*self.cpt['']
        elif factor.varList == []:
            for key, val in self.cpt.items():
                new_cpt[key] = val*factor.cpt['']
        else:
            map1 = {}
            map2 = {}
            for pos, i in enumerate(self.varList):
                map1[pos] = Util.lfind(newList, i)
            for pos, i in enumerate(factor.varList):
                map2[pos] = Util.lfind(newList, i)
            convex = list(set(self.varList) & set(factor.varList))
            test = convex != []
            if test:
                repeated_var = convex[0]
                pos1 = Util.lfind(self.varList, repeated_var)
                pos2 = Util.lfind(factor.varList, repeated_var)

            for key1, val1 in self.cpt.items():
                if test:
                    repeated_ins = key1[pos1]
                for key2, val2 in factor.cpt.items():
                    if test and repeated_ins == key2[pos2]:
                        key = np.zeros(length, dtype=int)
                        for ind, i in map1.items():
                            key[i] = key1[ind]
                        for ind, i in map2.items():
                            key[i] = key2[ind]
                        new_cpt["".join([str(num) for num in key])] = val1 * val2
        new_node = Node("f" + str(newList), newList)
        new_node.setCpt(new_cpt)
        return new_node
    def sumout(self, variable):
        """function that sums out a variable given a factor"""
        #Your code here
        if variable not in self.varList:
            return self
        pos = Util.lfind(self.varList, variable)
        node_list = []
        for i in set([j[pos] for j in self.cpt]):
            node_list.append(self.restrict(variable, i))
        new_var_list = copy.deepcopy(node_list[0].varList)
        new_cpt = copy.deepcopy(node_list[0].cpt)
        for node in node_list[1:]:
            for key, p in node.cpt.items():
                new_cpt[key] += node.cpt[key]

        new_node = Node("f" + str(new_var_list), new_var_list)
        new_node.setCpt(new_cpt)
        return new_node
    def restrict(self, variable, value):
        """function that restricts a variable to some value
        in a given factor"""
        #Your code here
        if variable not in self.varList:
            return self
        new_var_list = copy.deepcopy(self.varList) # 这里必须要用深复制
        new_var_list.remove(variable)
        length = len(new_var_list)
        new_cpt = {}
        pos = Util.lfind(self.varList, variable)
        for key, p in self.cpt.items():
            if key[pos] == value:
                key = key[0:pos]+key[pos+1:]
                new_cpt[key] = p
        new_node = Node("f" + str(new_var_list), new_var_list)
        new_node.setCpt(new_cpt)
        return new_node

def initBN():
    # create nodes for Bayes Net
    P = Node("PatientAge", ["P"])
    C = Node("CTScanResult", ["C"])
    MR = Node("MRIScanResult", ["MR"])
    A = Node("Anticoagulants", ["A"])
    S = Node("StrokeType", ["S", "C", "MR"])
    MO = Node("Mortality", ["MO", "S", "A"])
    D = Node("Disability", ["D", "S", "P"])

    # Generate cpt for each node
    P.setCpt({'0': 0.1, '1': 0.3, '2': 0.6})
    C.setCpt({'0': 0.7, '1': 0.3})
    MR.setCpt({'0': 0.7, '1': 0.3})
    A.setCpt({'0': 0.5, '1': 0.5})
    S.setCpt({'000': 0.8, '001': 0.5, '010': 0.5, '011': 0.0, \
              '100': 0.0, '101': 0.4, '110': 0.4, '111': 0.9, \
              '200': 0.2, '201': 0.1, '210': 0.1, '211': 0.1})
    MO.setCpt({'000': 0.28, '010': 0.99, '020': 0.1, '001': 0.56, '011': 0.58, '021': 0.05, \
               '100': 0.72, '110': 0.01, '120': 0.9, '101': 0.44, '111': 0.42, '121': 0.95})
    D.setCpt({'000': 0.80, '010': 0.70, '020': 0.90, '001': 0.60, '011': 0.50, '021': 0.40, '002': 0.30, '012': 0.20,
              '022': 0.10, \
              '100': 0.10, '110': 0.20, '120': 0.05, '101': 0.30, '111': 0.40, '121': 0.30, '102': 0.40, '112': 0.20,
              '122': 0.10, \
              '200': 0.10, '210': 0.10, '220': 0.05, '201': 0.10, '211': 0.10, '221': 0.30, '202': 0.30, '212': 0.60,
              '222': 0.80})
    return [P, C, MR, A, S, MO, D]

def test(factor_list, f):
    global num
    print("ORDER "+str(num)+":")
    num += 1
    begin1 = timer()
    VariableElimination.inference(copy.deepcopy(factor_list), ['A'], ['C', 'MR', 'S', 'MO', 'D'], {'P': 1}, '1', f)
    end1 = timer()
    print("time1:", (end1 - begin1)*1000, "ms")
    begin2 = timer()
    VariableElimination.inference(copy.deepcopy(factor_list), ['D'], ['P', 'C', 'MR', 'A', 'S', 'MO'], {}, '0', f)
    end2 = timer()
    print("time2:", (end2 - begin2)*1000, "ms")
    print()
    print()

def main():
    factor_list = initBN()

    # test
    # VariableElimination.inference(copy.deepcopy(factor_list), ['MO', 'C'], ['MR', 'A', 'S', 'D'], {'P': 1}, '10', VariableElimination.default_order)
    # VariableElimination.inference(copy.deepcopy(factor_list), ['D', 'C'], ['A', 'S', 'MO'], {'P': 2, 'MR': 1}, '11', VariableElimination.default_order)
    # VariableElimination.inference(copy.deepcopy(factor_list), ['S'], ['A', 'MO', 'D'], {'P': 2, 'C': 1, 'MR': 0}, '1', VariableElimination.default_order)
    # VariableElimination.inference(copy.deepcopy(factor_list), ['A'], ['C', 'MR', 'S', 'MO', 'D'], {'P': 1}, '1', VariableElimination.default_order)
    # VariableElimination.inference(copy.deepcopy(factor_list), ['D'], ['P', 'C', 'MR', 'A', 'S', 'MO'], {}, '0', VariableElimination.default_order)
    test(factor_list, VariableElimination.default_order)
    test(factor_list, VariableElimination.random_order)
    test(factor_list, VariableElimination.random_order)
    test(factor_list, VariableElimination.random_order)
    test(factor_list, VariableElimination.min_neighber)
    test(factor_list, VariableElimination.min_weight)


if __name__== "__main__":
    main()