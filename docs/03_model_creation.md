# 第三章 模型创建

本章介绍如何通过 Python 脚本在 Abaqus 中创建一个完整的几何模型，包括草图绘制、零件创建、材料定义、截面属性赋予和装配体搭建。

---

## 3.1 创建草图并定义零件

以创建一个长方体零件为例：

```python
# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *

# 获取模型引用
myModel = mdb.models['Model-1']

# 1. 在模型中创建零件草图（约束草图大小）
mySketch = myModel.ConstrainedSketch(name='RectSketch', sheetSize=200.0)

# 2. 在草图中绘制矩形（两个对角点坐标）
mySketch.rectangle(point1=(0.0, 0.0), point2=(100.0, 20.0))

# 3. 创建三维可变形零件，并通过拉伸草图生成实体
myPart = myModel.Part(
    name='Block',
    dimensionality=THREE_D,        # 三维
    type=DEFORMABLE_BODY           # 可变形体（与 ANALYTIC_RIGID_SURFACE 区分）
)
myPart.BaseSolidExtrude(sketch=mySketch, depth=10.0)  # 拉伸深度 10mm

print('零件创建成功：', myPart.name)
```

---

## 3.2 创建二维平面应力零件

```python
# 创建二维平面应力零件
mySketch2D = myModel.ConstrainedSketch(name='PlateSketch', sheetSize=200.0)
mySketch2D.rectangle(point1=(0.0, 0.0), point2=(100.0, 50.0))

myPart2D = myModel.Part(
    name='Plate',
    dimensionality=TWO_D_PLANAR,   # 二维平面
    type=DEFORMABLE_BODY
)
myPart2D.BaseShell(sketch=mySketch2D)  # 基于草图生成壳（面）
```

---

## 3.3 定义材料

```python
# 创建钢材材料
myMaterial = myModel.Material(name='Steel')

# 定义弹性属性：杨氏模量 210000 MPa，泊松比 0.3
myMaterial.Elastic(table=((210000.0, 0.3),))

# 如需定义密度（用于动力分析）
myMaterial.Density(table=((7.85e-9,),))  # 单位：ton/mm³

# 定义塑性（如需弹塑性分析）
# myMaterial.Plastic(table=((250.0, 0.0), (400.0, 0.2)))  # (应力, 等效塑性应变)
```

---

## 3.4 创建截面属性并赋予零件

### 实体截面（Solid Section）

```python
# 为三维实体零件创建截面
myModel.HomogeneousSolidSection(
    name='SolidSection',
    material='Steel',
    thickness=None  # 实体零件不需要指定厚度
)

# 将截面属性赋予零件的整个区域
region = myPart.Set(cells=myPart.cells, name='AllCells')
myPart.SectionAssignment(region=region, sectionName='SolidSection')
```

### 壳截面（Shell Section）

```python
# 为二维壳零件创建截面（需指定厚度）
myModel.HomogeneousShellSection(
    name='ShellSection',
    material='Steel',
    thickness=5.0   # 厚度 5mm
)

region2D = myPart2D.Set(faces=myPart2D.faces, name='AllFaces')
myPart2D.SectionAssignment(region=region2D, sectionName='ShellSection')
```

---

## 3.5 创建装配体（Assembly）

```python
# 获取装配体引用（一个模型只有一个根装配体）
myAssembly = myModel.rootAssembly

# 设置装配体坐标系为笛卡尔坐标系（通常不需要修改）
myAssembly.DatumCsysByDefault(CARTESIAN)

# 将零件实例化到装配体中
myInstance = myAssembly.Instance(
    name='Block-1',     # 实例名称
    part=myPart,        # 关联的零件
    dependent=ON        # ON: 依赖实例（推荐），OFF: 独立实例
)

print('装配体中的实例：', myAssembly.instances.keys())
```

---

## 3.6 移动和旋转实例

```python
# 平移实例（沿 X 轴移动 50mm）
myAssembly.translate(
    instanceList=('Block-1',),
    vector=(50.0, 0.0, 0.0)
)

# 旋转实例（绕 Z 轴旋转 90°）
import math
myAssembly.rotate(
    instanceList=('Block-1',),
    axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 0.0, 1.0),
    angle=90.0
)
```

---

## 3.7 创建集合（Set）和面（Surface）

集合（Set）和面（Surface）用于后续施加边界条件、载荷和提取结果。

```python
# 通过坐标范围选取几何体创建顶点集合
# 注意：使用 findAt() 方法通过坐标查找几何实体
leftFace = myInstance.faces.findAt(((0.0, 10.0, 5.0),))  # 传入坐标元组的元组
myAssembly.Set(faces=leftFace, name='LeftFace')

# 创建面（Surface），用于施加压力载荷
rightFace = myInstance.faces.findAt(((100.0, 10.0, 5.0),))
myAssembly.Surface(side1Faces=rightFace, name='RightSurface')
```

---

## 3.8 含孔矩形板的建模示例

```python
# 含圆孔的矩形板草图
mySketch = myModel.ConstrainedSketch(name='PlateWithHole', sheetSize=300.0)

# 绘制外边框
mySketch.rectangle(point1=(0.0, 0.0), point2=(200.0, 100.0))

# 绘制圆孔（圆心在板中心，半径 10mm）
mySketch.CircleByCenterPerimeter(
    center=(100.0, 50.0),
    point1=(110.0, 50.0)
)

# 创建零件
platePart = myModel.Part(
    name='PlateWithHole',
    dimensionality=TWO_D_PLANAR,
    type=DEFORMABLE_BODY
)
platePart.BaseShell(sketch=mySketch)
print('含孔矩形板创建成功')
```

---

## 小结

| 操作 | 关键 API |
|------|---------|
| 创建草图 | `Model.ConstrainedSketch()` |
| 创建三维实体零件 | `Model.Part()` + `Part.BaseSolidExtrude()` |
| 创建二维壳零件 | `Model.Part()` + `Part.BaseShell()` |
| 定义材料 | `Model.Material()` + `.Elastic()` |
| 定义截面 | `Model.HomogeneousSolidSection()` 或 `HomogeneousShellSection()` |
| 赋予截面 | `Part.SectionAssignment()` |
| 实例化到装配体 | `Assembly.Instance()` |
| 创建集合/面 | `Assembly.Set()` / `Assembly.Surface()` |

完整示例代码请参考 [`examples/02_simple_beam.py`](../examples/02_simple_beam.py) 和 [`examples/03_plate_with_hole.py`](../examples/03_plate_with_hole.py)。

下一章：[网格划分](04_mesh_generation.md)
