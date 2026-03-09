# 第七章 后处理与结果提取

后处理是有限元分析的最后一个环节，用于从计算结果中提取有用的工程数据。Abaqus 将计算结果存储在 **ODB（Output Database）文件**中，可以通过 Python 脚本读取和处理。

---

## 7.1 ODB 文件结构

```
ODB 文件
├── rootAssembly                   # 装配体信息
│   └── instances['Part-1-1']     # 零件实例（含节点、单元信息）
└── steps['Step-1']               # 分析步
    └── frames[0], frames[1], ... # 分析帧（每个增量步对应一帧）
        └── fieldOutputs           # 场输出对象
            ├── 'U'    → 位移
            ├── 'S'    → 应力
            └── 'MISES'→ Von Mises 应力
```

---

## 7.2 打开 ODB 文件

```python
# -*- coding: utf-8 -*-
from odbAccess import *

# 打开 ODB 文件（只读模式，避免修改结果）
odbPath = 'MyJob.odb'
odb = openOdb(path=odbPath, readOnly=True)

print('ODB 文件打开成功：', odbPath)
print('包含的分析步：', list(odb.steps.keys()))
```

---

## 7.3 访问分析步和帧

```python
# 获取指定分析步
step = odb.steps['Step-1']

# 查看该步中的帧数
print('Step-1 共有 %d 帧' % len(step.frames))

# 获取最后一帧（最终状态）
lastFrame = step.frames[-1]
print('最后一帧时间：', lastFrame.frameValue)
```

---

## 7.4 提取场输出：全模型结果

### 提取 Von Mises 应力

```python
# 从最后一帧中获取 Von Mises 应力场输出
stressField = lastFrame.fieldOutputs['S']
mises = lastFrame.fieldOutputs['MISES']

# 获取所有积分点的 Mises 应力值
misesValues = mises.values

# 找到最大 Mises 应力及其位置
maxMises = max(v.data for v in misesValues)
print('最大 Von Mises 应力：%.2f MPa' % maxMises)
```

### 提取位移场

```python
dispField = lastFrame.fieldOutputs['U']
dispValues = dispField.values

# 找到 X 方向最大位移
maxU1 = max(abs(v.data[0]) for v in dispValues)
print('最大 X 方向位移：%.4f mm' % maxU1)
```

---

## 7.5 提取节点集合结果

通过已命名的节点集合提取特定位置的结果：

```python
# 获取装配体实例
instance = odb.rootAssembly.instances['BLOCK-1']

# 获取节点集合（注意：ODB 中集合名称通常为大写）
nodeSet = odb.rootAssembly.nodeSets['MONITORPOINT']

# 提取该节点集合的位移结果
dispAtSet = lastFrame.fieldOutputs['U'].getSubset(region=nodeSet)
for value in dispAtSet.values:
    nodeLabel = value.nodeLabel
    u1, u2, u3 = value.data
    print('节点 %d：U1=%.4f, U2=%.4f, U3=%.4f mm' % (nodeLabel, u1, u2, u3))
```

---

## 7.6 提取历程输出（时间-历程数据）

历程输出存储在 `historyRegions` 中，适合提取载荷-位移曲线：

```python
# 获取历程输出区域（通过节点集合名称查找）
historyRegionKey = None
for key in step.historyRegions.keys():
    if 'MONITORPOINT' in key.upper():
        historyRegionKey = key
        break

if historyRegionKey:
    histRegion = step.historyRegions[historyRegionKey]

    # 获取位移历程数据（时间, 值）
    u1History = histRegion.historyOutputs['U1'].data
    print('时间历程数据点数：', len(u1History))

    for time, u1 in u1History:
        print('时间 %.3f s，U1 = %.4f mm' % (time, u1))
```

---

## 7.7 将结果导出为 CSV 文件

```python
import csv

# 提取所有节点的位移结果并保存为 CSV
dispField = lastFrame.fieldOutputs['U']

csvFileName = 'displacement_results.csv'
with open(csvFileName, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Node Label', 'U1 (mm)', 'U2 (mm)', 'U3 (mm)'])
    for v in dispField.values:
        writer.writerow([v.nodeLabel, v.data[0], v.data[1], v.data[2]])

print('位移结果已保存至：', csvFileName)

# 提取所有积分点的应力结果
stressField = lastFrame.fieldOutputs['S']
stressCsvFile = 'stress_results.csv'
with open(stressCsvFile, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Element Label', 'S11', 'S22', 'S33', 'S12', 'S13', 'S23'])
    for v in stressField.values:
        s = v.data  # 应力分量 [S11, S22, S33, S12, S13, S23]
        writer.writerow([v.elementLabel, s[0], s[1], s[2], s[3], s[4], s[5]])

print('应力结果已保存至：', stressCsvFile)
```

---

## 7.8 关闭 ODB 文件

```python
# 使用完毕后务必关闭 ODB 文件以释放资源
odb.close()
print('ODB 文件已关闭')
```

---

## 7.9 使用外部 Python（numpy/matplotlib）进行后处理

如果要使用 `numpy`、`matplotlib` 等库进行数据处理和绘图，推荐先用 Abaqus Python 脚本将结果导出为 CSV，再用外部 Python 脚本处理：

```python
# post_plot.py（外部 Python 3 环境运行，需安装 numpy 和 matplotlib）
import csv
import numpy as np
import matplotlib.pyplot as plt

times = []
u1_values = []

with open('history_u1.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # 跳过表头
    for row in reader:
        times.append(float(row[0]))
        u1_values.append(float(row[1]))

times = np.array(times)
u1_values = np.array(u1_values)

plt.figure(figsize=(8, 5))
plt.plot(times, u1_values, 'b-o', markersize=4)
plt.xlabel('时间 (s)')
plt.ylabel('U1 位移 (mm)')
plt.title('监控点 X 方向位移-时间曲线')
plt.grid(True)
plt.tight_layout()
plt.savefig('displacement_history.png', dpi=150)
plt.show()
```

---

## 7.10 常用场输出变量名称

| 变量名 | 说明 | 分量 |
|--------|------|------|
| `U` | 位移 | `U1`, `U2`, `U3` |
| `RF` | 反力 | `RF1`, `RF2`, `RF3` |
| `S` | 应力张量 | `S11`, `S22`, `S33`, `S12`, `S13`, `S23` |
| `E` | 应变张量 | `E11`, `E22`, `E33`, `E12`, `E13`, `E23` |
| `MISES` | Von Mises 等效应力 | 标量 |
| `PEEQ` | 等效塑性应变 | 标量 |
| `LE` | 对数应变（大变形） | 分量同 `E` |
| `NT11` | 节点温度 | 标量 |

---

## 小结

| 操作 | 关键 API |
|------|---------|
| 打开 ODB | `openOdb(path='job.odb', readOnly=True)` |
| 访问分析步 | `odb.steps['Step-1']` |
| 访问帧 | `step.frames[-1]`（最后一帧） |
| 提取场输出 | `frame.fieldOutputs['U']` |
| 按集合过滤 | `fieldOutput.getSubset(region=nodeSet)` |
| 提取历程输出 | `step.historyRegions[key].historyOutputs['U1'].data` |
| 导出 CSV | 使用 Python 内置 `csv` 模块 |
| 关闭 ODB | `odb.close()` |

完整示例请参考 [`examples/04_post_processing.py`](../examples/04_post_processing.py)。

---

**恭喜！** 您已学完本指南的全部章节。建议结合以下示例代码进行实践：

- [`examples/01_hello_abaqus.py`](../examples/01_hello_abaqus.py) — 验证脚本环境
- [`examples/02_simple_beam.py`](../examples/02_simple_beam.py) — 从建模到提交的完整流程
- [`examples/03_plate_with_hole.py`](../examples/03_plate_with_hole.py) — 含孔平板参数化分析
- [`examples/04_post_processing.py`](../examples/04_post_processing.py) — ODB 结果读取与导出
