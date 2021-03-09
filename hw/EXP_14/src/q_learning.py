import random
import numpy as np

EPOCH = 2000

def choose(can_list, epsilon):
    if random.random() > epsilon:
        return np.argmax(can_list)
    else:
        return can_list[random.randint(0,len(can_list)-1)][0]


def q_learning(reward, q_table, alpha=0.1, gamma=0.8, epsilon=0.8):

    print("reward:\n", reward)
    print()
    print("q_table:\n", q_table)
    print()
    print("EPOCH:", EPOCH)
    print()

    for i in range(EPOCH):
        state = 2
        while(state != 5):
            can_list = []
            for ind, j in enumerate(reward[state]):
                if j >= 0:
                    can_list.append((ind, j))
            next_state = choose(can_list, epsilon)
            q_table[state, next_state] += alpha*(reward[state, next_state]+gamma*max(q_table[next_state])-q_table[state,next_state])
            state = next_state

    print("q_table:\n", q_table)
    print()

    path = [2]
    while(path[-1] != 5):
        path.append(np.argmax(q_table[path[-1]]))

    return path


def main():
    print(q_learning(np.array([
        [-1, -1, -1, -1, 0, -1],
        [-1, -1, -1, 0, -1, 100],
        [-1, -1, -1, 0, -1, -1],
        [-1, 0, 0, -1, 0, -1],
        [0, -1, -1, 0, -1, 100],
        [-1, 0, -1, -1, 0, 100]]), np.zeros((6, 6))))


if __name__ == '__main__':
    main()
