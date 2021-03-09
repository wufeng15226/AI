import copy
class VariableElimination:
    def printFactors(factorList):
        for factor in factorList:
            factor.printInf()

    def inference(factorList, queryVariables,
    orderedListOfHiddenVariables, evidenceList):
        for ev in evidenceList:
            #Your code here
            for pos, factor in enumerate(factorList):
                factorList[pos] = factor.restrict(ev, str(evidenceList[ev])) # 注意这里需要转成str
        print()
        for var in orderedListOfHiddenVariables:
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
        print("RESULT:")
        res = factorList[0]
        for factor in factorList[1:]:
            res = res.multiply(factor)
        total = sum(res.cpt.values())
        res.cpt = {k: v/total for k, v in res.cpt.items()}
        res.printInf()

class Util:
    def to_binary(num, len):
        return "{0:0>{1:}b}".format(num,len)
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
        new_cpt = {}
        length = len(newList)
        len1 = len(self.varList)
        len2 = len(factor.varList)
        map1 = {}
        map2 = {}
        for pos, i in enumerate(self.varList):
            map1[pos] = Util.lfind(newList, i)
        for pos, i in enumerate(factor.varList):
            map2[pos] = Util.lfind(newList, i)
        for i in range(pow(2, length)):
            curr = Util.to_binary(i, length)
            str1 = ''
            str2 = ''
            for i in range(len1):
                str1 += curr[map1[i]]
            for i in range(len2):
                str2 += curr[map2[i]]
            new_cpt[curr] = self.cpt[str1]*factor.cpt[str2]
        new_node = Node("f" + str(newList), newList)
        new_node.setCpt(new_cpt)
        return new_node
    def sumout(self, variable):
        """function that sums out a variable given a factor"""
        #Your code here
        node0 = self.restrict(variable,'0')
        node1 = self.restrict(variable,'1')
        new_var_list = copy.deepcopy(node0.varList)
        new_cpt = copy.deepcopy(node0.cpt)
        for key,p in new_cpt.items():
            new_cpt[key] += node1.cpt[key]

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
        for i in range(pow(2, length)):
            new_cpt[Util.to_binary(i, length)] = 0
        for key, p in self.cpt.items():
            if key[pos] == value:
                key = key[0:pos]+key[pos+1:]
                new_cpt[key] = p
        new_node = Node("f" + str(new_var_list), new_var_list)
        new_node.setCpt(new_cpt)
        return new_node

# create nodes for Bayes Net
B = Node("B", ["B"])
E = Node("E", ["E"])
A = Node("A", ["A", "B","E"])
J = Node("J", ["J", "A"])
M = Node("M", ["M", "A"])

# Generate cpt for each node
B.setCpt({'0': 0.999, '1': 0.001})
E.setCpt({'0': 0.998, '1': 0.002})
A.setCpt({'111': 0.95, '011': 0.05, '110':0.94,'010':0.06,
'101':0.29,'001':0.71,'100':0.001,'000':0.999})
J.setCpt({'11': 0.9, '01': 0.1, '10': 0.05, '00': 0.95})
M.setCpt({'11': 0.7, '01': 0.3, '10': 0.01, '00': 0.99})

print("P(A) **********************")
VariableElimination.inference([B,E,A,J,M], ['A'], ['B','E','J','M'], {})

print("P(J~M) **********************")
VariableElimination.inference([B,E,A,J,M], ['J','M'], ['B','E','A'], {})

print("P(A | J~M) **********************")
VariableElimination.inference([B,E,A,J,M], ['A'], ['B','E'], {'J':1,'M':0})

print("P(B | A) **********************")
VariableElimination.inference([B,E,A,J,M], ['B'], ['E','J','M'], {'A':1})

print("P(B | J~M) **********************")
VariableElimination.inference([B,E,A,J,M], ['B'], ['E','A'], {'J':1,'M':0})

print("P(J~M | ~B) **********************")
VariableElimination.inference([B,E,A,J,M], ['J','M'], ['E','A'], {'B':0})
