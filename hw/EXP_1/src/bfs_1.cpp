#include<iostream>
#include<fstream>
#include<string>
#include<vector>
#include<queue>
#include<deque>
#include<iomanip>
#define VISITED -1
#define PATH '*'
using namespace std;

int main()
{
	ifstream inFile;
	inFile.open("MazeData.txt", ifstream::in);
	if (!inFile)
	{
		cout << "FILE OPEN ERROE!" << endl;
		return 0;
	}
	vector<vector<char>> map;
	pair<int, int> s;
	pair<int, int> e;
	int j = 0;
	while (1)
	{
		string curr;
		getline(inFile, curr);
		vector<char> vec(curr.begin(), curr.end());
		map.push_back(vec);
		if (curr.empty()) break;
		for (int i = 0; i < vec.size(); i++)
		{
			if (vec[i] == 'S')
			{
				s.first = j;
				s.second = i;
			}
			if (vec[i] == 'E')
			{
				e.first = j;
				e.second = i;
				map[j][i] = '0';
			}
		}
		j++;
	}
	inFile.close();
	
	vector<pair<int, int>> row(map[0].size(), pair<int, int>(0, 0));
	vector<vector<pair<int, int>>> fa(map.size(), row);
	queue<pair<int, int>> que;
	queue<pair<int, int>> emp;
	queue<pair<int, int>> hold;
	que.push(s);
	
	bool sign = 0;
	while (!que.empty())
	{
		while (!que.empty())
		{
			pair<int, int> curr = que.front();
			que.pop();
			if (curr == e)
			{
				sign = true;
				break;
			}
			map[curr.first][curr.second] = VISITED;
			if (map[curr.first + 1][curr.second] == '0') 
			{
				hold.push(pair<int, int>(curr.first + 1, curr.second));
				fa[curr.first + 1][curr.second] = pair<int, int>(curr.first, curr.second);
			}
			if (map[curr.first - 1][curr.second] == '0')
			{
				hold.push(pair<int, int>(curr.first - 1, curr.second));
				fa[curr.first - 1][curr.second] = pair<int, int>(curr.first, curr.second);
			}
			if (map[curr.first][curr.second + 1] == '0')
			{
				hold.push(pair<int, int>(curr.first, curr.second + 1));
				fa[curr.first][curr.second + 1] = pair<int, int>(curr.first, curr.second);
			}
			if (map[curr.first][curr.second - 1] == '0')
			{
				hold.push(pair<int, int>(curr.first, curr.second - 1));
				fa[curr.first][curr.second - 1] = pair<int, int>(curr.first, curr.second);
			}
		}
		if (sign) break;
		que = hold;
		hold = emp;
	}

	pair<int, int> curr = e;
	int len = 0;
	while (curr != s)
	{
		map[curr.first][curr.second] = PATH;
		len++;
		curr = fa[curr.first][curr.second];
	}
	cout << "Length:" << len << endl;
	
	for (auto i : map)
	{
		for (auto j : i)
		{
			if (j == VISITED) cout << '0';
			else cout << j;
		}
		puts("");
	}
	
	return 0;
}