#include<iostream>
#include<fstream>
#include<string>
#include<vector>
#include<queue>
#include<iomanip>
#define MAX 999
#define PATH '*'
#define VISITED -1
using namespace std;

vector<pair<int, int>> rst;
int min_len = MAX;


void dfs(vector<vector<char>> map, pair<int, int> curr, int len, vector<pair<int, int>> path)
{
	path.push_back(curr);
	if (map[curr.first][curr.second] == 'E')
	{
		if (len < min_len)
		{
			rst = path;
			min_len = len;
		}
	}
	else if (map[curr.first][curr.second] == '0') {
		map[curr.first][curr.second] = VISITED;
		dfs(map, pair<int, int>(curr.first + 1, curr.second), len + 1, path);
		dfs(map, pair<int, int>(curr.first, curr.second + 1), len + 1, path);
		dfs(map, pair<int, int>(curr.first - 1, curr.second), len + 1, path);
		dfs(map, pair<int, int>(curr.first, curr.second - 1), len + 1, path);
	}
}


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
				map[j][i] = '0';
			}
		}
		j++;
	}
	inFile.close();
	vector<pair<int, int>> tem;
	dfs(map, s, 0, tem);

	for (auto i : rst)
	{
		map[i.first][i.second] = PATH;
	}
	cout << "Length:" <<min_len;
	puts("");
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