#include<iostream>
#include<fstream>
#include<string>
#include<vector>
#include<queue>
#include<deque>
#include<iomanip>
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
	vector<vector<int>> map;
	pair<int, int> s;
	pair<int, int> e;
	int j = 0;
	while (1)
	{
		string curr;
		getline(inFile, curr);
		vector<int> vec(curr.begin(), curr.end());
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
	
	queue<pair<int, int>> que;
	queue<pair<int, int>> emp;
	queue<pair<int, int>> hold;
	que.push(s);
	vector<pair<int, int>> row(map[0].size(), pair<int, int>(0, 0));
	vector<vector<pair<int, int>>> fa(map.size(),row);
	
	int len = 0;
	bool sign = 0;
	while (!que.empty())
	{
		while (!que.empty())
		{
			pair<int, int> curr = que.front();
			que.pop();
			if (map[curr.first][curr.second] == 'E')
			{
				sign = true;
				break;
			}
			map[curr.first][curr.second] = '1';
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
		len++;
		que = hold;
		hold = emp;
	}

	deque<pair<int, int>> rst;
	pair<int, int> curr = e;
	while (curr != s)
	{
		rst.push_back(curr);
		curr = fa[curr.first][curr.second];
	}
	cout << "len:" << rst.size() << endl;
	while (curr != e)
	{
		cout << "(" << curr.first << "," << curr.second << ")" << "->";
		curr = rst.back();
		rst.pop_back();
	}
	cout << "END" << endl;
	
	return 0;
}