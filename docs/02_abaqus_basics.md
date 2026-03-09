# 第二章 Abaqus Python 脚本基础

## 2.1 Abaqus 对象模型概览

Abaqus 的 Python API 采用**面向对象**的设计，所有操作都通过操作对象的属性和方法来实现。核心对象有两个：

| 对象 | 说明 | 访问方式 |
|------|------|---------|
| `mdb` | Model Database，前处理数据库，包含几何、材料、边界条件等信息 | `from abaqus import mdb` |
| `odb` | Output Database，后处理数据库，包含分析结果 | `openOdb('job.odb')` |

### mdb 对象层次结构

```
mdb
└── models['Model-1']                    # 模型对象
    ├── parts['Part-1']                  # 零件对象
    │   ├── features                     # 特征（草图、拉伸等）
    │   ├── vertices / edges / faces     # 几何拓扑
    │   └── nodes / elements             # 网格节点和单元
    ├── materials['Steel']               # 材料对象
    ├── sections['BeamSection']          # 截面属性对象
    ├── rootAssembly                     # 装配体
    │   └── instances['Part-1-1']        # 零件实例
    ├── steps['Step-1']                  # 分析步
    │   ├── loads                        # 载荷
    │   └── boundaryConditions           # 边界条件
    └── jobs['Job-1']                    # 作业对象（在 mdb 层级）
```

---

## 2.2 访问和操作模型

```python
from abaqus import *
from abaqusConstants import *

# 访问当前数据库中的第一个模型（默认名为 'Model-1'）
myModel = mdb.models['Model-1']

# 查看模型中所有零件的名称
print(myModel.parts.keys())

# 查看模型中所有材料的名称
print(myModel.materials.keys())
```

---

## 2.3 常用 abaqusConstants 常量

在 Abaqus 脚本中，很多参数不是字符串或数字，而是**符号常量**，它们定义在 `abaqusConstants` 模块中：

```python
from abaqusConstants import *

# 常见常量示例
ON        # 开启（布尔型）
OFF       # 关闭（布尔型）
FIXED     # 固定约束
ENCASTRE  # 完全固定（固支）
ISOTROPIC # 各向同性
ELASTIC   # 弹性
THREE_D   # 三维
DEFORMABLE_BODY  # 可变形体
```

> 💡 **技巧**：不确定常量名称时，可以录制宏来查看 Abaqus 自动生成的脚本中使用了哪些常量。

---

## 2.4 字符串 vs. 符号常量

```python
# 错误示范：使用字符串代替常量
myModel.Material(name='Steel').Elastic(table=((210000, 0.3),), type='ISOTROPIC')  # 可能报错

# 正确示范：使用符号常量
myModel.Material(name='Steel').Elastic(table=((210000, 0.3),), type=ISOTROPIC)
```

---

## 2.5 容器（Repository）的使用

Abaqus 中的集合（如 `parts`、`materials`）是**字典式容器（Repository）**，支持：

```python
# 通过名称（键）访问
part = myModel.parts['Part-1']

# 遍历所有键（名称）
for name in myModel.parts.keys():
    print(name)

# 遍历所有值（对象）
for part in myModel.parts.values():
    print(part.name)

# 获取容器长度
print(len(myModel.parts))
```

---

## 2.6 常用模块汇总

| 模块 | 用途 | 常用函数/类 |
|------|------|------------|
| `abaqus` | 核心入口 | `mdb`, `session` |
| `abaqusConstants` | 常量定义 | `ON`, `OFF`, `FIXED`, ... |
| `odbAccess` | 访问 ODB 文件 | `openOdb()` |
| `visualization` | 可视化操作 | `session.viewports` |
| `regionToolset` | 区域定义 | `Region()` |
| `mesh` | 网格操作 | 单元类型常量 |

---

## 2.7 获取帮助：使用 Python 内置函数

```python
# 查看对象的所有属性和方法
dir(mdb.models['Model-1'])

# 查看方法的文档字符串
help(mdb.models['Model-1'].Part)

# 查看对象的类型
print(type(mdb.models['Model-1']))
```

---

## 2.8 脚本调试技巧

```python
# 在 Message Area 打印调试信息
print('当前零件数量：', len(mdb.models['Model-1'].parts))

# 使用 try-except 捕获错误
try:
    part = mdb.models['Model-1'].parts['Part-1']
except KeyError:
    print('零件 Part-1 不存在，请先创建零件。')
```

---

## 2.9 脚本模板

以下是推荐的脚本文件头模板：

```python
# -*- coding: utf-8 -*-
"""
脚本名称: my_script.py
作    者: Your Name
创建日期: 2024-01-01
描    述: 本脚本用于...
"""

from abaqus import *
from abaqusConstants import *
import regionToolset

# ---- 参数定义区 ----
MODEL_NAME = 'Model-1'
PART_NAME  = 'MyPart'
JOB_NAME   = 'MyJob'

# ---- 主逻辑区 ----
myModel = mdb.models[MODEL_NAME]

# ... 在此处添加建模代码 ...
```

---

## 小结

- Abaqus Python API 以 `mdb`（前处理）和 `odb`（后处理）为核心
- 参数常量来自 `abaqusConstants` 模块，不能用字符串替代
- 容器（Repository）支持字典式访问和遍历
- 使用 `dir()` 和 `help()` 可以在运行时查阅 API

下一章：[模型创建](03_model_creation.md)
