# -*- coding: utf-8 -*-
"""
示例 02: 简单梁的静力分析（完整流程）
=====================================
本脚本演示从建模到提交计算的完整流程：
  - 创建矩形截面梁零件
  - 定义钢材材料
  - 划分网格
  - 施加固定约束和集中力
  - 提交计算

模型描述：
  - 悬臂梁，长度 200mm，截面 20mm × 20mm
  - 材料：钢（E=210000 MPa，ν=0.3）
  - 约束：左端完全固定
  - 载荷：右端顶面中心施加集中力 F=1000N（向下）
  - 单元类型：C3D8R（8节点六面体减缩积分）

运行方式：
  abaqus cae noGUI=02_simple_beam.py
"""

from abaqus import *
from abaqusConstants import *
import regionToolset
import mesh
import job

# ============================================================
# 参数定义区（修改此处可改变模型参数）
# ============================================================
MODEL_NAME  = 'BeamModel'
PART_NAME   = 'Beam'
JOB_NAME    = 'BeamJob'

BEAM_LENGTH = 200.0   # 梁长度 (mm)
BEAM_WIDTH  = 20.0    # 截面宽度 (mm)
BEAM_HEIGHT = 20.0    # 截面高度 (mm)

YOUNGS_MOD  = 210000.0  # 杨氏模量 (MPa)
POISSON_R   = 0.3       # 泊松比
DENSITY     = 7.85e-9   # 密度 (ton/mm³)

MESH_SIZE   = 5.0       # 全局网格尺寸 (mm)
APPLIED_FORCE = -1000.0 # 集中力 (N)，负号表示向下（Y 方向）

# ============================================================
# Step 1: 创建新模型
# ============================================================
print('[1/7] 创建模型...')

# 如果同名模型已存在则先删除
if MODEL_NAME in mdb.models.keys():
    del mdb.models[MODEL_NAME]

mdb.Model(name=MODEL_NAME)
myModel = mdb.models[MODEL_NAME]

# ============================================================
# Step 2: 创建零件（草图 + 拉伸）
# ============================================================
print('[2/7] 创建梁零件...')

# 绘制矩形截面草图（在 XY 平面）
mySketch = myModel.ConstrainedSketch(name='BeamSection', sheetSize=300.0)
mySketch.rectangle(
    point1=(0.0, 0.0),
    point2=(BEAM_WIDTH, BEAM_HEIGHT)
)

# 拉伸生成三维实体零件（沿 Z 轴拉伸，即梁轴线为 Z 方向）
myPart = myModel.Part(
    name=PART_NAME,
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY
)
myPart.BaseSolidExtrude(sketch=mySketch, depth=BEAM_LENGTH)

print('    零件尺寸：%g x %g x %g mm' % (BEAM_WIDTH, BEAM_HEIGHT, BEAM_LENGTH))

# ============================================================
# Step 3: 定义材料和截面属性
# ============================================================
print('[3/7] 定义材料和截面...')

# 创建钢材
myMaterial = myModel.Material(name='Steel')
myMaterial.Elastic(table=((YOUNGS_MOD, POISSON_R),))
myMaterial.Density(table=((DENSITY,),))

# 创建实体截面
myModel.HomogeneousSolidSection(
    name='SolidSection',
    material='Steel',
    thickness=None
)

# 将截面赋予零件所有单元区域
cellRegion = myPart.Set(cells=myPart.cells, name='AllCells')
myPart.SectionAssignment(region=cellRegion, sectionName='SolidSection')

# ============================================================
# Step 4: 创建装配体
# ============================================================
print('[4/7] 创建装配体...')

myAssembly = myModel.rootAssembly
myAssembly.DatumCsysByDefault(CARTESIAN)

# 实例化零件
myInstance = myAssembly.Instance(
    name=PART_NAME + '-1',
    part=myPart,
    dependent=ON
)

# ============================================================
# Step 5: 划分网格
# ============================================================
print('[5/7] 划分网格...')

# 设置全局种子
myPart.seedPart(size=MESH_SIZE, deviationFactor=0.1, minSizeFactor=0.1)

# 设置单元类型为 C3D8R（六面体主单元）
# setElementType 接受三个单元类型，分别对应：
#   elemTypes[0] - 三维实体主单元（六面体优先使用 C3D8R）
#   elemTypes[1] - 退化楔形单元（六面体退化为楔形时使用 C3D6 作为过渡）
#   elemTypes[2] - 退化四面体单元（楔形退化为四面体时使用 C3D4 作为后备）
elemType = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)
myPart.setElementType(
    regions=(myPart.cells,),
    elemTypes=(elemType, mesh.ElemType(C3D6), mesh.ElemType(C3D4))
)

# 生成网格
myPart.generateMesh()

print('    节点数：%d，单元数：%d' % (len(myPart.nodes), len(myPart.elements)))

# ============================================================
# Step 6: 创建分析步、边界条件和载荷
# ============================================================
print('[6/7] 设置分析步、边界条件和载荷...')

# 创建静力分析步
myModel.StaticStep(
    name='LoadStep',
    previous='Initial',
    timePeriod=1.0,
    initialInc=0.1,
    minInc=1e-5,
    maxInc=0.5,
    maxNumInc=100,
    description='Apply concentrated force at beam tip'
)

# ---- 施加固定约束（左端面，Z=0 处）----
# 使用 findAt() 通过坐标查找左端面
fixedFace = myInstance.faces.findAt(
    ((BEAM_WIDTH / 2.0, BEAM_HEIGHT / 2.0, 0.0),)
)
fixedRegion = myAssembly.Set(faces=fixedFace, name='FixedFace')

myModel.EncastreBC(
    name='FixedBC',
    createStepName='Initial',
    region=fixedRegion
)

# ---- 施加集中力（右端顶点，Z=BEAM_LENGTH）----
# 选取右端顶面中心点（通过顶点 findAt）
tipVertex = myInstance.vertices.findAt(
    ((BEAM_WIDTH / 2.0, BEAM_HEIGHT, BEAM_LENGTH),)
)
loadRegion = myAssembly.Set(vertices=tipVertex, name='LoadPoint')

myModel.ConcentratedForce(
    name='TipForce',
    createStepName='LoadStep',
    region=loadRegion,
    cf2=APPLIED_FORCE   # Y 方向施加集中力（负号向下）
)

# ---- 设置场输出请求 ----
myModel.fieldOutputRequests['F-Output-1'].setValues(
    variables=('U', 'S', 'MISES', 'RF', 'E')
)

# ---- 设置历程输出（监控加载点位移）----
myModel.HistoryOutputRequest(
    name='TipDisp',
    createStepName='LoadStep',
    region=loadRegion,
    variables=('U1', 'U2', 'U3')
)

# ============================================================
# Step 7: 创建作业并提交
# ============================================================
print('[7/7] 创建作业并提交...')

myJob = mdb.Job(
    name=JOB_NAME,
    model=MODEL_NAME,
    description='Simple cantilever beam analysis',
    numCpus=1,
    numDomains=1
)

# 写入输入文件（可在 Abaqus 外部查看）
myJob.writeInput(consistencyChecking=OFF)
print('    输入文件已写入：%s.inp' % JOB_NAME)

# 提交并等待计算完成
myJob.submit(consistencyChecking=OFF)
myJob.waitForCompletion()

if myJob.status == COMPLETED:
    print('\n✓ 计算完成！结果文件：%s.odb' % JOB_NAME)
    print('  请参考 examples/04_post_processing.py 提取结果。')
else:
    print('\n✗ 计算失败，状态：%s。请检查 %s.dat 和 %s.msg 文件。' % (
        myJob.status, JOB_NAME, JOB_NAME))
