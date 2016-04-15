# list 列表
Python内置的一种数据类型是列表：list。list是一种有序集合，可以删除其中的元素。

比如，列出班里所有同学的名字，就可以使用一个list表示：
```
>>> classmate = ['Michael', 'Bob', 'Tracy']
>>> classmate
['Michael', 'Bob', 'Tracy']
```
变量classmate就是一个list，用`len()` 函数可以获得list元素的个数。
```
>>> len(classmate)
3
```
* 索引访问list中的元素，索引从`0`开始
```
>>> classmates[0]
'Michael'
>>> classmates[1]
'Bob'
>>> classmates[2]
'Tracy'
>>> classmates[3]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: list index out of range
```
也可以倒着访问，下标从`-1`开始。
```
>>> classmates[-1]
'Tracy'
>>> classmates[-2]
'Bob'
>>> classmates[-3]
'Michael'
>>> classmates[-4]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: list index out of range
```
* 删除 `pop`方法
`pop()`删除末尾的元素，`pop(i)`，`i`是索引位置。

**list中的元素类型可以不同。**

构造一个空list：`L = []`

# tuple 元组
tuple和list非常相似，但是tuple一旦初始化就不能修改。所以所有修改的方法对tuple都不可用。比如同样是列出同学的名字：
```
>>> classmates = ('Michael', 'Bob', 'Tracy')
```
定义一个空的tuple：`t = ()`

**注意：**   
定义只有一个元素的tuple：`t = (1,)`。因为`()`，可以表示数学公式中的小括号，容易产生歧义，所以在定义个元素的tuple时，必须加一个逗号`,`。来消除歧义。
```
>>> t = (1,)
>>> t
(1,)
```
