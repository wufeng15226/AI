## GAC

+ 一次性使用GAC和FC测试5个例子

``` cmake
python GAC.py test_all
```

+ 单次测试

``` cmake
# -gac 只测试GAC
# -fc 只测试FC
# -cmp 同时测试两者
# num 1~5 选择测例
python GAC.py -gac num
python GAC.py -fc num
python GAC.py -cmp num
```

## KRR

+ 一次性测试3个例子

``` cmake
python KRR.py
```

+ 单次测试

```cmake
# num 1~3 选择测例
python KRR.py num
```

## 数据文件说明

+ data*.txt：CSP问题矩阵及约束，共5个
+ kb*.txt：一阶逻辑数据，共3个，注意和助教数据不同的是这里把$\neg$换成了$!$