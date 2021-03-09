#include<iostream>
#include<fstream>
#include<string>
#include<vector>
#include<queue>
#define MAX 999
using namespace std;

vector<pair<int,int>> rst;
int min_len = MAX;


void dfs(vector<vector<int>> map, vector<vector<bool>> visit,pair<int,int> curr,int len,vector<pair<int,int>> path)
{
	if (map[curr.first][curr.second] == 'E')
	{
		if (len < min_len)
		{
			rst = path;
			min_len = len;
		}
	}
	else if(map[curr.first][curr.second]=='0'&& visit[curr.first][curr.second]==false){
		path.push_back(curr);
		visit[curr.first][curr.second] = true;
		dfs(map, visit, pair<int, int>(curr.first + 1, curr.second), len + 1, path);
		dfs(map, visit, pair<int, int>(curr.first, curr.second + 1), len + 1, path);
		dfs(map, visit, pair<int, int>(curr.first - 1, curr.second), len + 1, path);
		dfs(map, visit, pair<int, int>(curr.first, curr.second - 1), len + 1, path);
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
	vector<vector<int>> map;
	vector<vector<bool>> visited;
	pair<int, int> s;
	int j = 0;
	while (1)
	{
		string curr;
		getline(inFile, curr);
		visited.push_back(vector<bool>(curr.size(),false));
		vector<int> vec(curr.begin(), curr.end());
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
	/*for (int i = 0; i < map.size(); i++)
	{
		for (int j = 0; j < map[0].size(); j++)
		{
			cout << (char)map[i][j];
		}
		puts("");
	}*/
	inFile.close();
	vector<pair<int, int>> tem;
	dfs(map, visited, s, 0, tem);
	cout << min_len;
	return 0;
}