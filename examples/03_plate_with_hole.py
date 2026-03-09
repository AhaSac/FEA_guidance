# -*- coding: utf-8 -*-
"""
示例 03: 含圆孔矩形板的参数化应力分析
======================================
本脚本演示：
  - 二维平面应力模型的建立
  - 含圆孔矩形板的草图绘制
  - 通过参数化循环分析不同孔径对应力集中的影响
  - 提取各工况的最大 Von Mises 应力并汇总

模型描述：
  - 矩形平板，200mm × 100mm，厚度 10mm（平面应力）
  - 板中心有一个圆孔，孔径从 10mm 到 30mm 变化（步长 10mm）
  - 材料：钢（E=210000 MPa，ν=0.3）
  - 约束：左端固定
  - 载荷：右端面施加均布压力 50 MPa（拉伸）
  - 单元类型：CPS4R（4节点平面应力减缩积分）

理论背景：
  对于无限大平板中的圆孔，在均匀拉伸载荷下，
  理论应力集中系数 Kt = 3（孔边环向应力 = 3 × 远场应力）。

运行方式：
  abaqus cae noGUI=03_plate_with_hole.py
"""

from abaqus import *
from abaqusConstants import *
import regionToolset
import mesh
import job

# ============================================================
# 全局参数
# ============================================================
PLATE_WIDTH  = 200.0   # 板宽（X 方向，mm）
PLATE_HEIGHT = 100.0   # 板高（Y 方向，mm）
PLATE_THICK  = 10.0    # 板厚（mm，平面应力模型中作为截面厚度）

YOUNGS_MOD  = 210000.0  # 杨氏模量 (MPa)
POISSON_R   = 0.3       # 泊松比

PRESSURE    = 50.0      # 右端拉伸压力 (MPa)

# 孔径参数化列表（mm）
HOLE_RADII = [5.0, 10.0, 15.0]

# 结果汇总列表
results = []

# ============================================================
# 参数化循环
# ============================================================
for radius in HOLE_RADII:

    model_name = 'PlateHole_R%g' % radius
    job_name   = 'Job_PlateHole_R%g' % radius

    print('\n' + '=' * 55)
    print('正在分析：孔半径 R = %g mm' % radius)
    print('=' * 55)

    # ----------------------------------------------------------
    # Step 1: 创建模型
    # ----------------------------------------------------------
    if model_name in mdb.models.keys():
        del mdb.models[model_name]
    mdb.Model(name=model_name)
    myModel = mdb.models[model_name]

    # ----------------------------------------------------------
    # Step 2: 创建含圆孔矩形板草图
    # ----------------------------------------------------------
    mySketch = myModel.ConstrainedSketch(name='PlateSketch', sheetSize=300.0)

    # 绘制矩形外边框
    mySketch.rectangle(
        point1=(0.0, 0.0),
        point2=(PLATE_WIDTH, PLATE_HEIGHT)
    )

    # 绘制圆孔（圆心在板中心）
    cx = PLATE_WIDTH / 2.0   # 100.0 mm
    cy = PLATE_HEIGHT / 2.0  # 50.0 mm
    mySketch.CircleByCenterPerimeter(
        center=(cx, cy),
        point1=(cx + radius, cy)
    )

    # 创建二维平面零件
    myPart = myModel.Part(
        name='Plate',
        dimensionality=TWO_D_PLANAR,
        type=DEFORMABLE_BODY
    )
    myPart.BaseShell(sketch=mySketch)

    # ----------------------------------------------------------
    # Step 3: 材料和截面
    # ----------------------------------------------------------
    myMaterial = myModel.Material(name='Steel')
    myMaterial.Elastic(table=((YOUNGS_MOD, POISSON_R),))

    # 平面应力壳截面
    myModel.HomogeneousShellSection(
        name='ShellSection',
        material='Steel',
        thickness=PLATE_THICK
    )

    faceRegion = myPart.Set(faces=myPart.faces, name='AllFaces')
    myPart.SectionAssignment(region=faceRegion, sectionName='ShellSection')

    # ----------------------------------------------------------
    # Step 4: 装配体
    # ----------------------------------------------------------
    myAssembly = myModel.rootAssembly
    myAssembly.DatumCsysByDefault(CARTESIAN)
    myInstance = myAssembly.Instance(
        name='Plate-1',
        part=myPart,
        dependent=ON
    )

    # ----------------------------------------------------------
    # Step 5: 网格划分
    # ----------------------------------------------------------
    # 在圆孔附近加密（全局网格尺寸取孔半径的 1/3 或最大 8mm，以较小值为准）
    globalSize = min(radius / 3.0, 8.0)
    myPart.seedPart(size=globalSize, deviationFactor=0.05, minSizeFactor=0.1)

    # 设置单元类型：CPS4R（平面应力四边形减缩积分）
    elemType = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD)
    triType  = mesh.ElemType(elemCode=CPS3,  elemLibrary=STANDARD)
    myPart.setElementType(
        regions=(myPart.faces,),
        elemTypes=(elemType, triType)
    )

    # 网格控制：四边形为主，中轴线算法
    myPart.setMeshControls(
        regions=myPart.faces,
        elemShape=QUAD_DOMINATED,
        algorithm=MEDIAL_AXIS
    )

    myPart.generateMesh()
    print('  网格：节点 %d，单元 %d' % (len(myPart.nodes), len(myPart.elements)))

    # ----------------------------------------------------------
    # Step 6: 分析步、边界条件和载荷
    # ----------------------------------------------------------
    myModel.StaticStep(
        name='LoadStep',
        previous='Initial',
        timePeriod=1.0,
        initialInc=0.1,
        maxInc=1.0,
        maxNumInc=100
    )

    # 左端固定（X=0 处的边）
    leftEdge = myInstance.edges.findAt(
        ((0.0, PLATE_HEIGHT / 2.0, 0.0),)
    )
    fixedRegion = myAssembly.Set(edges=leftEdge, name='FixedEdge')
    myModel.EncastreBC(
        name='FixedBC',
        createStepName='Initial',
        region=fixedRegion
    )

    # 右端施加拉伸压力（X=PLATE_WIDTH 处的边）
    rightEdge = myInstance.edges.findAt(
        ((PLATE_WIDTH, PLATE_HEIGHT / 2.0, 0.0),)
    )
    loadSurface = myAssembly.Surface(
        side1Edges=rightEdge,
        name='RightEdge'
    )
    # 负号表示压力方向向右（即拉伸）
    myModel.ShellEdgeLoad(
        name='TensileLoad',
        createStepName='LoadStep',
        region=loadSurface,
        magnitude=PRESSURE,
        directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    )

    # 场输出
    myModel.fieldOutputRequests['F-Output-1'].setValues(
        variables=('U', 'S', 'MISES')
    )

    # ----------------------------------------------------------
    # Step 7: 创建并提交作业
    # ----------------------------------------------------------
    myJob = mdb.Job(
        name=job_name,
        model=model_name,
        description='Plate with hole, R=%g mm' % radius,
        numCpus=1,
        numDomains=1
    )

    myJob.writeInput(consistencyChecking=OFF)
    myJob.submit(consistencyChecking=OFF)
    myJob.waitForCompletion()

    # ----------------------------------------------------------
    # Step 8: 提取结果（最大 Von Mises 应力）
    # ----------------------------------------------------------
    if myJob.status == COMPLETED:
        from odbAccess import openOdb
        odb = openOdb(path=job_name + '.odb', readOnly=True)
        lastFrame = odb.steps['LoadStep'].frames[-1]
        misesField = lastFrame.fieldOutputs['MISES']
        maxMises = max(v.data for v in misesField.values)
        odb.close()

        # 理论应力集中系数（近似：Kt ≈ 3 对于无限大板）
        Kt_num = maxMises / PRESSURE

        results.append({
            'radius': radius,
            'max_mises': maxMises,
            'Kt': Kt_num
        })

        print('  ✓ 孔半径 R=%g mm，最大 Mises 应力 = %.2f MPa，Kt = %.3f' % (
            radius, maxMises, Kt_num))
    else:
        print('  ✗ 计算失败（R=%g mm），状态：%s' % (radius, myJob.status))

# ============================================================
# 汇总结果
# ============================================================
print('\n' + '=' * 55)
print('参数化分析结果汇总')
print('=' * 55)
print('%-15s %-20s %-15s' % ('孔半径 (mm)', '最大 Mises 应力 (MPa)', '应力集中系数 Kt'))
print('-' * 55)
for r in results:
    print('%-15g %-20.2f %-15.3f' % (r['radius'], r['max_mises'], r['Kt']))
print('=' * 55)
print('\n理论值参考：对于无限大板中的小圆孔，Kt ≈ 3.0')
print('分析完成！')
