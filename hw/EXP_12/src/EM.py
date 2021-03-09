import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

EPOCH = 50

def load_data():
    with open("iris.data","r") as f:
        reader = list(csv.reader(f))
        return [[float(j) for j in  i[:-1]] for i in reader[:-1]], [j[-1] for j in reader[:-1]]


def N(x, mu, sigma):
    D = len(x[0])
    delta = x - mu
    return (1/(((2*np.pi)**(D/2))*(np.linalg.det(sigma)**0.5))*(np.exp(-1/2*delta*(sigma.I)*delta.T)))[0][0]


def likelihood(data, pi, mu, sigma, n, K):
    _sum = 0
    for i in range(n):
        sum = 0
        for j in range(K):
            sum += pi[j] * N(data[i], mu[j], sigma[j])
        _sum += np.log(sum)
    return _sum[0, 0]


def EM(data, K):
    paint = [[],[]]
    # print((np.pi*2)**(-0.5))
    # print(N(np.matrix([[1,1]]), np.matrix([[1,1]]), np.matrix([[1, 0], [0,1]])))
    data = np.matrix(data)
    n, m = np.shape(data)
    # print(data)

    # 初始化
    pi = [1/K for i in range(K)]
    mu = [data[np.random.randint(0, n)] for i in range(K)]
    # mu = [data[0], data[50], data[100]]
    sigma = [np.matrix(np.eye(m)) for i in range(K)]
    gamma = np.matrix(np.zeros((n,K)))
    hold = likelihood(data, pi, mu, sigma, n, K)
    _likelihood = 0
    # print(hold)

    epoch = 0
    while(epoch < EPOCH and abs(hold-_likelihood)>np.exp(-3)):
        hold = _likelihood
        # E
        for i in range(n):
            sum = 0
            for j in range(K):
                gamma[i , j] = pi[j] * N(data[i], mu[j], sigma[j])
                sum += gamma[i, j]
            for j in range(K):
                gamma[i, j] /= sum

        sum_gamma = np.sum(gamma, axis=0) # N_new
        # print(gamma)
        # print(sum_gamma)
        # M
        for i in range(K):
            mu[i] = np.matrix(np.zeros((1, m)))
            sigma[i] = np.matrix(np.zeros((m,m)))

            for j in range(n):
                mu[i] += gamma[j, i] * data[j]
            mu[i] /= sum_gamma[0, i] # mu_new

            for j in range(n):
                sigma[i] += gamma[j, i] * (data[j] - mu[i]).T * (data[j] - mu[i])
            sigma[i] /= sum_gamma[0, i] # sigma_new

            pi[i] = sum_gamma[0 , i] / n # pi_new
        _likelihood = likelihood(data, pi, mu, sigma, n, K)
        epoch += 1
        paint[0].append(epoch)
        paint[1].append(_likelihood)
        # print("EPOCH:",epoch)
        # print(Counter([np.argmax(gamma[i]) + 1 for i in range(n)]))
        # print(_likelihood)
    print("gamma:\n", gamma)
    print("mu:\n", mu)
    print("sigma:\n", sigma)
    print("likelihood:", _likelihood)
    return [np.argmax(gamma[i]) + 1 for i in range(n)], paint

def main():
    data, labels = load_data()
    rst_labels, paint =  EM(data, len(Counter(labels)))
    # print(rst_labels)
    # print(paint)
    plt.scatter(paint[0], paint[1])
    plt.show()
    count = 0
    # print(labels)
    # print(rst_labels)
    map1 = {}
    for i, label in enumerate(labels):
        if map1.get(label, 0):
            map1[label].append(i)
        else:
            map1[label] = [i]
    set_list1 = [set(i) for i in map1.values()]
    # print(set_list1)
    map2 = {}
    for i, label in enumerate(rst_labels):
        if map2.get(label, 0):
            map2[label].append(i)
        else:
            map2[label] = [i]
    set_list2 = [set(i) for i in map2.values()]
    # print(set_list2)
    for _set in set_list2:
        count += max([len(_set & __set) for __set in set_list1])

    print("Accuracy:",count/len(labels))

if __name__== "__main__":
    main()