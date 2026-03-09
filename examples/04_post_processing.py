# -*- coding: utf-8 -*-
"""
示例 04: 后处理 — ODB 结果提取与导出
======================================
本脚本演示如何读取 Abaqus 计算结果文件（ODB），提取工程数据，
并将结果导出为 CSV 文件，以便进一步分析或绘图。

演示内容：
  1. 打开 ODB 文件并查看基本信息
  2. 提取全模型的位移和应力场结果
  3. 提取指定节点集合的结果
  4. 提取历程输出（时间-位移曲线数据）
  5. 找到最大/最小值及其位置
  6. 将结果导出为 CSV 文件

适用场景：
  配合 examples/02_simple_beam.py 生成的 BeamJob.odb 使用。
  也可修改 ODB_PATH 指向任意 ODB 文件。

运行方式：
  abaqus python 04_post_processing.py
  （注意：使用 'abaqus python' 而非 'abaqus cae noGUI'，
         以便访问 odbAccess 模块并在计算完成后单独运行）
"""

from odbAccess import *
import csv
import os

# ============================================================
# 配置参数（根据实际情况修改）
# ============================================================
ODB_PATH  = 'BeamJob.odb'    # ODB 文件路径
STEP_NAME = 'LoadStep'       # 要读取的分析步名称

OUTPUT_DIR = '.'             # 输出目录（当前目录）

# ============================================================
# 辅助函数
# ============================================================

def check_odb_exists(path):
    """检查 ODB 文件是否存在。"""
    if not os.path.exists(path):
        raise IOError(
            'ODB 文件不存在：%s\n'
            '请先运行 02_simple_beam.py 生成计算结果。' % path
        )

def save_csv(filename, header, rows):
    """将数据保存为 CSV 文件。"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print('  已保存：%s（共 %d 行数据）' % (filepath, len(rows)))
    return filepath

# ============================================================
# Step 1: 打开 ODB 文件并查看基本信息
# ============================================================
print('=' * 55)
print('Abaqus ODB 后处理脚本')
print('=' * 55)

check_odb_exists(ODB_PATH)
odb = openOdb(path=ODB_PATH, readOnly=True)

print('\n[信息] ODB 文件：%s' % ODB_PATH)
print('[信息] 包含的分析步：%s' % list(odb.steps.keys()))

step = odb.steps[STEP_NAME]
totalFrames = len(step.frames)
print('[信息] 分析步 %s 共有 %d 帧' % (STEP_NAME, totalFrames))

# 列出可用的场输出变量
firstFrame = step.frames[0]
availableFields = list(firstFrame.fieldOutputs.keys())
print('[信息] 可用场输出变量：%s' % availableFields)

# ============================================================
# Step 2: 提取最后一帧的全模型位移结果
# ============================================================
print('\n[2/5] 提取全模型位移结果（最后一帧）...')

lastFrame = step.frames[-1]
print('  分析帧时间：%.4f s' % lastFrame.frameValue)

dispField = lastFrame.fieldOutputs['U']

# 找到最大合位移
rows_disp = []
maxMagU = 0.0
maxMagNodeLabel = -1

for v in dispField.values:
    u1 = v.data[0]
    u2 = v.data[1]
    u3 = v.data[2]
    mag = (u1**2 + u2**2 + u3**2) ** 0.5
    rows_disp.append([v.nodeLabel, u1, u2, u3, mag])
    if mag > maxMagU:
        maxMagU = mag
        maxMagNodeLabel = v.nodeLabel

print('  最大合位移：%.4f mm（节点 %d）' % (maxMagU, maxMagNodeLabel))

# 保存位移结果
save_csv(
    'displacement_all.csv',
    ['NodeLabel', 'U1(mm)', 'U2(mm)', 'U3(mm)', 'UMag(mm)'],
    rows_disp
)

# ============================================================
# Step 3: 提取全模型应力结果
# ============================================================
print('\n[3/5] 提取全模型 Von Mises 应力结果（最后一帧）...')

misesField = lastFrame.fieldOutputs['MISES']

rows_mises = []
maxMises = 0.0
maxMisesElem = -1

for v in misesField.values:
    mises = v.data
    rows_mises.append([v.elementLabel, v.integrationPoint, mises])
    if mises > maxMises:
        maxMises = mises
        maxMisesElem = v.elementLabel

print('  最大 Von Mises 应力：%.2f MPa（单元 %d）' % (maxMises, maxMisesElem))

# 保存 Mises 应力
save_csv(
    'mises_stress_all.csv',
    ['ElementLabel', 'IntegrationPoint', 'MISES(MPa)'],
    rows_mises
)

# 提取完整应力张量
stressField = lastFrame.fieldOutputs['S']
rows_stress = []
for v in stressField.values:
    s = v.data  # [S11, S22, S33, S12, S13, S23]
    rows_stress.append([
        v.elementLabel, v.integrationPoint,
        s[0], s[1], s[2], s[3], s[4], s[5]
    ])

save_csv(
    'stress_tensor_all.csv',
    ['ElementLabel', 'IntegrationPoint', 'S11', 'S22', 'S33', 'S12', 'S13', 'S23'],
    rows_stress
)

# ============================================================
# Step 4: 提取历程输出（时间-位移曲线）
# ============================================================
print('\n[4/5] 提取历程输出...')

historyData = {}
for regionKey, histRegion in step.historyRegions.items():
    for varName, histOutput in histRegion.historyOutputs.items():
        if varName not in historyData:
            historyData[varName] = []
        historyData[varName].extend(histOutput.data)

if historyData:
    print('  可用历程变量：%s' % list(historyData.keys()))

    # 导出所有历程数据
    for varName, data in historyData.items():
        if data:
            # 去除文件名中各操作系统不允许的特殊字符
            _invalid = ('/', '\\', ':', '*', '?', '"', '<', '>', '|')
            safeVarName = varName
            for ch in _invalid:
                safeVarName = safeVarName.replace(ch, '_')
            save_csv(
                'history_%s.csv' % safeVarName,
                ['Time(s)', '%s' % varName],
                data
            )
else:
    print('  该 ODB 中无历程输出数据。')

# ============================================================
# Step 5: 按帧提取关键指标（时间历程中的最大 Mises 应力）
# ============================================================
print('\n[5/5] 按分析帧提取最大 Von Mises 应力（全时程）...')

rows_maxMises = []
for i, frame in enumerate(step.frames):
    if 'MISES' in frame.fieldOutputs.keys():
        mField = frame.fieldOutputs['MISES']
        maxVal = max(v.data for v in mField.values)
        rows_maxMises.append([frame.frameValue, maxVal])

if rows_maxMises:
    save_csv(
        'max_mises_vs_time.csv',
        ['Time(s)', 'MaxMISES(MPa)'],
        rows_maxMises
    )
    print('  全时程最大 Mises 应力范围：%.2f ~ %.2f MPa' % (
        min(r[1] for r in rows_maxMises),
        max(r[1] for r in rows_maxMises)
    ))

# ============================================================
# 关闭 ODB 文件
# ============================================================
odb.close()
print('\n✓ 后处理完成！所有结果已保存为 CSV 文件。')
print('  提示：可使用 Excel 或 Python matplotlib 进一步绘图分析。')

# ============================================================
# 附: 使用外部 Python 绘图的提示代码（在系统 Python 中运行）
# ============================================================
PLOT_HINT = '''
# 以下代码需在系统 Python 3（安装了 matplotlib）中运行，不在 Abaqus 中运行：

import csv
import matplotlib.pyplot as plt

times, mises_max = [], []
with open("max_mises_vs_time.csv") as f:
    reader = csv.reader(f)
    next(reader)  # 跳过表头
    for row in reader:
        times.append(float(row[0]))
        mises_max.append(float(row[1]))

plt.figure(figsize=(8, 5))
plt.plot(times, mises_max, "r-o", markersize=5)
plt.xlabel("Time (s)")
plt.ylabel("Max Von Mises Stress (MPa)")
plt.title("Maximum Von Mises Stress vs. Time")
plt.grid(True)
plt.tight_layout()
plt.savefig("max_mises_history.png", dpi=150)
plt.show()
'''

print('\n--- 绘图提示（在系统 Python 3 中运行）---')
print(PLOT_HINT)
