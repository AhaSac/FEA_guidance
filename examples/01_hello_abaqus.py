# -*- coding: utf-8 -*-
"""
示例 01: Hello Abaqus
=====================
这是第一个 Abaqus Python 脚本，用于验证脚本环境是否正常。
演示内容：
  - 访问 mdb 对象
  - 打印模型信息
  - 在 Abaqus Message Area 输出文本

运行方式：
  abaqus cae noGUI=01_hello_abaqus.py
  或在 Abaqus/CAE 中：File → Run Script → 选择本文件
"""

from abaqus import *
from abaqusConstants import *

# -------------------------------------------------------
# 1. 打印欢迎信息
# -------------------------------------------------------
print('=' * 50)
print('Hello, Abaqus！欢迎使用 FEA Python 二次开发指南。')
print('=' * 50)

# -------------------------------------------------------
# 2. 查看当前数据库中的模型
# -------------------------------------------------------
print('\n当前数据库中的模型：')
for modelName in mdb.models.keys():
    model = mdb.models[modelName]
    print('  - 模型名称：%s' % modelName)
    print('    零件数量：%d' % len(model.parts))
    print('    材料数量：%d' % len(model.materials))
    print('    分析步数量：%d' % len(model.steps))

# -------------------------------------------------------
# 3. 在默认模型中创建一个简单草图（演示 API 调用）
# -------------------------------------------------------
myModel = mdb.models['Model-1']

# 创建一个约束草图
sketch = myModel.ConstrainedSketch(name='HelloSketch', sheetSize=100.0)

# 绘制一个矩形
sketch.rectangle(point1=(0.0, 0.0), point2=(50.0, 30.0))

print('\n草图 HelloSketch 已创建，包含 %d 条线段' % len(sketch.geometry))

# -------------------------------------------------------
# 4. 常用常量演示
# -------------------------------------------------------
print('\n常用 Abaqus 常量示例：')
print('  ON  =', ON)
print('  OFF =', OFF)
print('  THREE_D =', THREE_D)
print('  DEFORMABLE_BODY =', DEFORMABLE_BODY)

# -------------------------------------------------------
# 5. 完成
# -------------------------------------------------------
print('\n脚本执行完毕！请参考 docs/01_introduction.md 了解更多。')
