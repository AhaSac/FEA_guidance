# 第五章 边界条件与载荷

在 Abaqus 中，边界条件（Boundary Conditions）和载荷（Loads）必须与**分析步（Step）**关联。本章介绍常用约束和载荷的脚本施加方法。

---

## 5.1 创建分析步（Step）

边界条件和载荷必须在分析步中定义。常用的静力分析步如下：

```python
from abaqus import *
from abaqusConstants import *

myModel = mdb.models['Model-1']

# 创建静力通用分析步（Static, General）
myModel.StaticStep(
    name='LoadStep',
    previous='Initial',          # 前一步（初始步为 'Initial'）
    description='Apply load',
    timePeriod=1.0,              # 分析步总时间（静力分析中通常归一化为 1）
    initialInc=0.1,              # 初始增量步
    minInc=1e-5,                 # 最小增量步
    maxInc=0.5,                  # 最大增量步
    maxNumInc=100                # 最大增量步数
)
```

---

## 5.2 施加位移边界条件（固定约束）

### 完全固定（Encastre / Clamped）

```python
myAssembly = myModel.rootAssembly

# 通过已创建的面集合施加固定约束
# 先创建或获取左端面集合
leftFace = myAssembly.instances['Block-1'].faces.findAt(((0.0, 10.0, 5.0),))
fixedRegion = myAssembly.Set(faces=leftFace, name='FixedFace')

# 在初始步施加固定边界条件（ENCASTRE 表示所有自由度为零）
myModel.EncastreBC(
    name='FixedBC',
    createStepName='Initial',
    region=fixedRegion
)
```

### 指定自由度的位移约束

```python
import regionToolset

# 创建约束区域（通过面上的点坐标查找）
symFace = myAssembly.instances['Block-1'].faces.findAt(((50.0, 0.0, 5.0),))
symRegion = regionToolset.Region(faces=symFace)

# 对称边界条件（Y 方向位移为零：U2=0）
# U1=U2=U3 对应 x、y、z 方向位移；UR1=UR2=UR3 对应转角
myModel.DisplacementBC(
    name='SymmetryBC',
    createStepName='Initial',
    region=symRegion,
    u1=UNSET,  # x 方向：不约束
    u2=SET,    # y 方向：约束为 0（SET 表示约束值为 0）
    u3=UNSET,  # z 方向：不约束
    ur1=UNSET,
    ur2=UNSET,
    ur3=UNSET
)

# 施加指定位移（非零位移）
# myModel.DisplacementBC(
#     name='PrescribedDisp',
#     createStepName='LoadStep',
#     region=region,
#     u1=5.0    # x 方向施加 5mm 位移
# )
```

---

## 5.3 施加集中力（Concentrated Force）

```python
# 在右端顶点施加集中力
rightVertex = myAssembly.instances['Block-1'].vertices.findAt(((100.0, 20.0, 10.0),))
loadRegion = myAssembly.Set(vertices=rightVertex, name='LoadPoint')

myModel.ConcentratedForce(
    name='PointLoad',
    createStepName='LoadStep',
    region=loadRegion,
    cf1=1000.0,   # x 方向力：1000 N
    cf2=0.0,      # y 方向力
    cf3=0.0       # z 方向力
)
```

---

## 5.4 施加压力载荷（Pressure Load）

```python
# 在右端面施加均布压力
rightFace = myAssembly.instances['Block-1'].faces.findAt(((100.0, 10.0, 5.0),))
pressureSurface = myAssembly.Surface(side1Faces=rightFace, name='PressureSurface')

myModel.Pressure(
    name='SurfacePressure',
    createStepName='LoadStep',
    region=pressureSurface,
    magnitude=10.0   # 压力大小：10 MPa（方向由面的法向量决定）
)
```

---

## 5.5 施加重力载荷（Gravity）

```python
# 施加重力（z 方向向下，加速度 9800 mm/s²）
myModel.Gravity(
    name='Gravity',
    createStepName='LoadStep',
    comp3=-9800.0   # z 方向分量（负号表示向下）
)
```

---

## 5.6 施加温度载荷（Predefined Field）

```python
# 对整个模型施加均匀温度场
allCells = myAssembly.Set(cells=myAssembly.instances['Block-1'].cells, name='AllCells')

myModel.Temperature(
    name='ThermalLoad',
    createStepName='LoadStep',
    region=allCells,
    distributionType=UNIFORM,   # 均匀温度场
    crossSectionDistribution=CONSTANT_THROUGH_THICKNESS,
    magnitudes=(200.0,)          # 温度：200°C
)
```

---

## 5.7 修改和删除边界条件

```python
# 在后续分析步中修改边界条件（如将力从 1000N 增加到 2000N）
myModel.loads['PointLoad'].setValuesInStep(
    stepName='LoadStep',
    cf1=2000.0
)

# 在后续分析步中停用边界条件
myModel.boundaryConditions['SymmetryBC'].deactivate(stepName='Step-2')

# 删除边界条件
del myModel.boundaryConditions['SymmetryBC']
```

---

## 5.8 查看已定义的载荷和边界条件

```python
# 查看所有边界条件
print('已定义的边界条件：', list(myModel.boundaryConditions.keys()))

# 查看所有载荷
print('已定义的载荷：', list(myModel.loads.keys()))
```

---

## 5.9 常用约束方法汇总

| 方法 | 说明 |
|------|------|
| `Model.EncastreBC()` | 完全固定（所有自由度为零） |
| `Model.DisplacementBC()` | 指定位移/转角约束 |
| `Model.PinnedBC()` | 铰支（位移为零，转角自由） |
| `Model.XsymmBC()` / `YsymmBC()` / `ZsymmBC()` | X/Y/Z 方向对称约束 |
| `Model.ConcentratedForce()` | 集中力 |
| `Model.Pressure()` | 面压力 |
| `Model.ShellEdgeLoad()` | 壳边缘载荷 |
| `Model.Gravity()` | 重力体力 |
| `Model.BodyHeatFlux()` | 体热通量 |
| `Model.Temperature()` | 温度场（预定义场） |

---

## 小结

- 所有边界条件和载荷必须与分析步（Step）关联
- 使用 `findAt()` 方法通过坐标查找几何实体（面、边、顶点）
- 位移约束用 `SET`（约束为 0）、`UNSET`（不约束）或具体数值
- 集合（`Set`）和面（`Surface`）是施加边界条件的载体

下一章：[分析步与作业提交](06_analysis_and_job.md)
