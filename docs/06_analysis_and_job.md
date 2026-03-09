# 第六章 分析步与作业提交

本章介绍如何配置分析步、设置输出请求，以及通过 Python 脚本提交、监控和管理分析作业。

---

## 6.1 常用分析步类型

Abaqus 支持多种分析步，以下是脚本中最常用的几种：

| 分析步类型 | 方法 | 适用场景 |
|-----------|------|---------|
| 静力通用 | `Model.StaticStep()` | 线性/非线性静力分析 |
| 静力线弹性（摄动） | `Model.StaticLinearPerturbationStep()` | 线弹性静力分析 |
| 频率提取 | `Model.FrequencyStep()` | 固有频率/模态分析 |
| 显式动力 | `Model.ExplicitDynamicsStep()` | 冲击、爆炸等高速动态问题 |
| 稳态传热 | `Model.HeatTransferStep()` | 稳态热传导 |
| 热力耦合 | `Model.CoupledTempDisplacementStep()` | 热力耦合分析 |

---

## 6.2 创建静力分析步

```python
from abaqus import *
from abaqusConstants import *

myModel = mdb.models['Model-1']

# 创建静力通用分析步（非线性）
myModel.StaticStep(
    name='Step-1',
    previous='Initial',
    timePeriod=1.0,
    description='Static load application',
    nlgeom=OFF,       # ON: 考虑大变形（几何非线性）
    initialInc=0.1,
    minInc=1e-5,
    maxInc=0.5,
    maxNumInc=100
)
```

---

## 6.3 设置场输出请求（Field Output）

场输出用于在整个模型上输出结果，写入 ODB 文件，可在 Abaqus/Viewer 中可视化：

```python
# 修改默认的场输出请求（Abaqus 会自动创建名为 'F-Output-1' 的请求）
myModel.fieldOutputRequests['F-Output-1'].setValues(
    variables=(
        'S',    # 应力张量
        'E',    # 应变张量
        'U',    # 位移
        'RF',   # 反力
        'MISES' # Von Mises 应力
    ),
    frequency=1   # 每个增量步输出一次（1 表示每步都输出）
)

# 创建新的场输出请求
myModel.FieldOutputRequest(
    name='MyFieldOutput',
    createStepName='Step-1',
    variables=('S', 'U', 'MISES'),
    frequency=LAST_INCREMENT    # 只在最后一个增量步输出
)
```

---

## 6.4 设置历程输出请求（History Output）

历程输出用于在指定点/区域记录结果随时间的变化，适合绘制载荷-位移曲线等：

```python
# 先创建监控点集合
myAssembly = myModel.rootAssembly
monitorNode = myAssembly.instances['Block-1'].vertices.findAt(((100.0, 20.0, 10.0),))
monitorRegion = myAssembly.Set(vertices=monitorNode, name='MonitorPoint')

# 创建历程输出请求
myModel.HistoryOutputRequest(
    name='DispHistory',
    createStepName='Step-1',
    region=monitorRegion,
    variables=('U1', 'U2', 'U3', 'RF1', 'RF2', 'RF3'),
    frequency=1
)
```

---

## 6.5 创建分析作业（Job）

```python
import job

# 创建作业
myJob = mdb.Job(
    name='MyJob',
    model='Model-1',
    description='Simple static analysis',
    type=ANALYSIS,
    numCpus=4,           # 并行计算 CPU 数量
    numDomains=4,        # 并行域数量（通常与 numCpus 相同）
    memory=90,           # 内存占用百分比
    memoryUnits=PERCENTAGE,
    multiprocessingMode=DEFAULT,
    explicitPrecision=SINGLE,   # 显式分析精度（单精度/双精度）
    nodalOutputPrecision=SINGLE
)

print('作业已创建：', myJob.name)
```

---

## 6.6 提交作业

```python
# 提交作业并等待完成
myJob.submit(consistencyChecking=OFF)
myJob.waitForCompletion()

print('作业 %s 计算完成' % myJob.name)
```

> ⚠️ `waitForCompletion()` 会阻塞脚本直到作业完成，适合批处理脚本。如果只提交不等待，去掉该行即可。

---

## 6.7 检查作业状态

```python
# 查看作业状态（在 waitForCompletion() 之后）
print('作业状态：', myJob.status)
# 可能的状态：SUBMITTED、RUNNING、COMPLETED、ABORTED、TERMINATED
```

---

## 6.8 参数化分析（扫参）

以不同载荷大小进行参数化分析为例：

```python
# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *
import job

# 要扫描的载荷值列表（单位：N）
load_values = [500, 1000, 2000, 5000]

for load in load_values:
    # 为每个载荷值克隆原始模型
    model_name = 'Model_Load_%d' % load
    mdb.Model(name=model_name, objectToCopy=mdb.models['Model-1'])

    # 修改克隆模型中的载荷大小
    mdb.models[model_name].loads['PointLoad'].setValues(cf1=float(load))

    # 创建并提交对应作业
    job_name = 'Job_Load_%d' % load
    myJob = mdb.Job(name=job_name, model=model_name)
    myJob.submit()
    myJob.waitForCompletion()
    print('载荷 %d N 的作业已完成' % load)

print('所有参数化分析完成！')
```

---

## 6.9 写入输入文件（不提交）

如果只需要生成 Abaqus 输入文件（`.inp`）而不提交计算：

```python
# 写入 .inp 文件（在当前工作目录）
myJob.writeInput(consistencyChecking=OFF)
print('输入文件已写入：MyJob.inp')
```

---

## 6.10 修改求解器控制参数

```python
# 修改分析步的求解控制（如松散收敛准则用于非线性问题）
myModel.steps['Step-1'].control.setValues(
    allowPropagation=OFF,
    resetDefaultValues=OFF,
    timeIncrementation=FIXED
)
```

---

## 小结

| 操作 | 关键 API |
|------|---------|
| 创建静力步 | `Model.StaticStep()` |
| 设置场输出 | `Model.FieldOutputRequest()` |
| 设置历程输出 | `Model.HistoryOutputRequest()` |
| 创建作业 | `mdb.Job(name=..., model=...)` |
| 提交并等待 | `Job.submit()` + `Job.waitForCompletion()` |
| 生成输入文件 | `Job.writeInput()` |
| 参数化分析 | 循环创建模型 + 修改参数 + 提交作业 |

完整示例请参考 [`examples/02_simple_beam.py`](../examples/02_simple_beam.py)。

下一章：[后处理与结果提取](07_post_processing.md)
