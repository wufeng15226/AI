#include <iostream>
#include <fstream>
#include <string>
#define SIZE 4
using namespace std;

enum TURN
{
	L,
	R,
	U,
	D,
	E
};
int mat[SIZE][SIZE];
TURN sta[100];
int dx[4] = {0, 0, -1, 1};
int dy[4] = {-1, 1, 0, 0};
TURN wr[4] = {R, L, D, U};
bool flag;

void print()
{
	for (int i = 0; i < SIZE; i++)
	{
		for (int j = 0; j < SIZE; j++)
		{
			cout << mat[i][j] << ' ';
		}
		puts("");
	}
}

inline int point_dis(int x, int y)
{
	return abs((mat[x][y] - 1) / SIZE - x) + abs((mat[x][y] - 1) % SIZE - y);
}

int dfs(int g, int h, int depth, int x, int y, TURN T)
{
	if (!h)
	{
		flag = true;
		return 0;
	}
	if (g + h > depth)
		return g + h;
	int rst = INT_MAX;

	for (int i = 0; i < SIZE; i++)
	{
		if (T == wr[i])
			continue;
		int nx = x + dx[i];
		int ny = y + dy[i];
		if (nx >= 0 && ny >= 0 && nx < SIZE && ny < SIZE)
		{
			int hold = h;
			h -= point_dis(nx, ny);
			mat[x][y] = mat[nx][ny];
			mat[nx][ny] = 0;
			h += point_dis(x, y);
			int ret = dfs(g + 1, h, depth, nx, ny, TURN(i));
			if (flag)
			{
				sta[g] = TURN(i);
				return ret;
			}
			h = hold;
			mat[nx][ny] = mat[x][y];
			mat[x][y] = 0;
			rst = ret < rst ? ret : rst;
		}
	}
	return rst;
}

int main()
{
	ifstream inFile;
	inFile.open("data.txt", ifstream::in);
	int num, x, y;
	inFile >> num;
	for (int i = 0; i < num; i++)
	{
		int h = 0;
		flag = false;
		for (int i = 0; i < SIZE; i++)
		{
			for (int j = 0; j < SIZE; j++)
			{
				inFile >> mat[i][j];
				if (!mat[i][j])
				{
					x = i;
					y = j;
				}
				else
				{
					h += point_dis(i, j);
				}
			}
		}
		print();
		int re = 0;
		for (int i = 0; i < SIZE * SIZE; i++)
		{
			for (int j = 0; j < i; j++)
			{
				if (!mat[i / SIZE][i % SIZE])
					continue;
				if (mat[i / SIZE][i % SIZE] < mat[j / SIZE][j % SIZE])
					re++;
			}
		}
		if ((re + SIZE - 1 - x) % 2 != 0)
		{
			cout << "No answer!" << endl;
			continue;
		}
		int depth = h;
		while (1)
		{
			int rst = dfs(0, h, depth, x, y, E);
			if (rst)
			{
				depth = rst;
			}
			else
			{
				cout << "Length:" << depth << endl;
				for (int i = 0; i < depth; i++)
				{
					char curr;
					switch (sta[i])
					{
					case 0:
						curr = 'L';
						break;
					case 1:
						curr = 'R';
						break;
					case 2:
						curr = 'U';
						break;
					case 3:
						curr = 'D';
						break;
					default:
						curr = 'E';
						break;
					}
					cout << curr;
				}
				puts("");
				break;
			}
		}
	}
	inFile.close();
	return 0;
}
