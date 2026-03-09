# 第四章 网格划分

网格质量直接影响有限元分析的精度和收敛性。本章介绍如何通过 Python 脚本控制 Abaqus 的网格划分过程。

---

## 4.1 网格划分的基本流程

1. 设置**种子（Seed）**：控制网格密度
2. 设置**网格控制（Mesh Controls）**：选择网格算法
3. 选择**单元类型（Element Type）**
4. 生成网格（`generateMesh`）
5. 检查网格质量

---

## 4.2 设置全局种子

```python
from abaqus import *
from abaqusConstants import *
import mesh

myModel = mdb.models['Model-1']
myPart = myModel.parts['Block']

# 设置全局种子大小（单位与模型一致）
# 种子大小越小，网格越密，计算越精确但耗时更长
myPart.seedPart(size=5.0, deviationFactor=0.1, minSizeFactor=0.1)
```

---

## 4.3 设置局部种子（边种子）

对重要区域（如应力集中处）进行网格加密：

```python
# 通过坐标查找边
refinedEdge = myPart.edges.findAt(((50.0, 0.0, 0.0),))

# 按数量设置局部种子：将该边等分为 20 份
myPart.seedEdgeByNumber(edges=refinedEdge, number=20)

# 按尺寸设置局部种子：该边上的最大网格尺寸为 2.0
# myPart.seedEdgeBySize(edges=refinedEdge, size=2.0)
```

---

## 4.4 设置网格控制

```python
# 为所有单元体设置网格控制
# algorithm: FREE（自由划分）、MEDIAL_AXIS（中轴线）
myPart.setMeshControls(
    regions=myPart.cells,           # 适用区域（实体）
    elemShape=HEX,                  # 单元形状：HEX（六面体）、TET（四面体）、WEDGE（楔形）
    algorithm=ADVANCING_FRONT       # 划分算法
)

# 二维壳单元的网格控制
# myPart.setMeshControls(
#     regions=myPart.faces,
#     elemShape=QUAD,               # QUAD（四边形）、TRI（三角形）、QUAD_DOMINATED
#     algorithm=MEDIAL_AXIS
# )
```

### 常用单元形状常量

| 常量 | 适用维度 | 说明 |
|------|---------|------|
| `HEX` | 三维 | 六面体（结构化，精度高） |
| `TET` | 三维 | 四面体（适合复杂几何） |
| `WEDGE` | 三维 | 楔形（过渡区域） |
| `QUAD` | 二维 | 四边形（精度高） |
| `TRI` | 二维 | 三角形（适合复杂形状） |

---

## 4.5 选择单元类型

```python
import mesh

# 三维减缩积分六面体单元 C3D8R
elemType1 = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)

# 三维完全积分六面体单元 C3D8
elemType2 = mesh.ElemType(elemCode=C3D8, elemLibrary=STANDARD)

# 三维四面体单元（二次）C3D10
elemType3 = mesh.ElemType(elemCode=C3D10, elemLibrary=STANDARD)

# 将单元类型赋予零件中的所有单元
myPart.setElementType(
    regions=(myPart.cells,),
    elemTypes=(elemType1, elemType2, elemType3)
    # elemTypes 按单元维度从高到低对应：3D实体、2D壳、1D线
)
```

### 常用单元类型

| 单元代码 | 说明 | 适用场景 |
|---------|------|---------|
| `C3D8R` | 8节点六面体，减缩积分 | 一般静力分析（最常用） |
| `C3D8` | 8节点六面体，完全积分 | 接触分析、不可压缩材料 |
| `C3D10` | 10节点四面体，二次 | 复杂几何自由网格 |
| `C3D4` | 4节点四面体，线性 | 简单快速计算（精度较低） |
| `S4R` | 4节点壳单元，减缩积分 | 薄壁结构 |
| `S8R` | 8节点壳单元，减缩积分 | 精度更高的壳分析 |
| `CPS4R` | 4节点平面应力，减缩积分 | 薄板平面问题 |
| `CPE4R` | 4节点平面应变，减缩积分 | 长构件截面问题 |
| `B31` | 2节点梁单元 | 梁柱结构 |

---

## 4.6 生成网格

```python
# 生成网格
myPart.generateMesh()

print('网格节点数：', len(myPart.nodes))
print('网格单元数：', len(myPart.elements))
```

---

## 4.7 网格质量检查

```python
# 获取网格质量统计信息
# Abaqus 的 getMeshStats() 返回网格统计对象
meshStats = myPart.getMeshStats(regions=(myPart.cells,))
print('单元数量：', meshStats.numElements)
print('节点数量：', meshStats.numNodes)

# 在 GUI 中高亮显示低质量单元（通过 Mesh → Verify 菜单操作）
# 脚本方式检查翻转单元数量：
badElements = myPart.verifyMeshQuality(criterion=ANALYSIS_CHECKS)
print('存在质量问题的单元数：', len(badElements['failedElements']))
```

---

## 4.8 对装配体实例进行网格划分

网格划分既可以在**零件级别**完成，也可以在**装配体实例级别**完成。对于依赖实例（`dependent=ON`），需在零件上划分网格；对于独立实例（`dependent=OFF`），则在实例上划分。

```python
# 独立实例（dependent=OFF）时，在实例上操作
myAssembly = myModel.rootAssembly
myInstance = myAssembly.instances['Block-1']

myInstance.seedPart(size=5.0)
myInstance.generateMesh()
```

---

## 4.9 分区（Partition）辅助网格划分

对于复杂几何体，需要先进行分区以便生成结构化网格：

```python
# 通过平面分区（将长方体沿中面切分）
myPart.PartitionCellByPlanePointNormal(
    point=myPart.InterestingPoint(myPart.edges[0], MIDDLE),
    normal=myPart.edges[0],
    cells=myPart.cells
)
```

---

## 小结

| 操作 | 关键 API |
|------|---------|
| 全局种子 | `Part.seedPart(size=...)` |
| 边局部种子 | `Part.seedEdgeByNumber()` / `seedEdgeBySize()` |
| 网格控制 | `Part.setMeshControls(elemShape=HEX, algorithm=...)` |
| 单元类型 | `mesh.ElemType(elemCode=C3D8R)` + `Part.setElementType()` |
| 生成网格 | `Part.generateMesh()` |
| 质量检查 | `Part.verifyMeshQuality()` |

下一章：[边界条件与载荷](05_boundary_conditions.md)
