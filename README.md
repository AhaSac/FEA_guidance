# FEA_guidance —— 有限元分析 Python 二次开发指南

> Secondary Development Guide for FEA Software (Abaqus / Ansys APDL) using Python

本项目以 Markdown 文档配合可运行的 Python 示例代码，帮助初学者系统地学习有限元分析软件（主要以 **Abaqus** 为主，兼顾 Ansys APDL）的 Python 二次开发。

---

## 目录结构

```
FEA_guidance/
├── docs/                        # Markdown 文档
│   ├── 01_introduction.md       # 简介与环境配置
│   ├── 02_abaqus_basics.md      # Abaqus Python 脚本基础
│   ├── 03_model_creation.md     # 模型创建
│   ├── 04_mesh_generation.md    # 网格划分
│   ├── 05_boundary_conditions.md# 边界条件与载荷
│   ├── 06_analysis_and_job.md   # 分析步与作业提交
│   └── 07_post_processing.md    # 后处理与结果提取
└── examples/                    # Python 示例代码
    ├── 01_hello_abaqus.py       # 第一个 Abaqus 脚本
    ├── 02_simple_beam.py        # 简单梁单元分析
    ├── 03_plate_with_hole.py    # 含孔平板应力分析
    └── 04_post_processing.py    # 后处理：结果提取与导出
```

---

## 各章节简介

| 章节 | 文档 | 说明 |
|------|------|------|
| 第一章 | [简介与环境配置](docs/01_introduction.md) | Python 二次开发概念、Abaqus 内置 Python 与外部 Python 的区别、环境配置 |
| 第二章 | [Abaqus Python 脚本基础](docs/02_abaqus_basics.md) | Abaqus 对象模型（`mdb`/`odb`）、常用模块、脚本执行方式 |
| 第三章 | [模型创建](docs/03_model_creation.md) | 草图、零件、材料、截面属性、装配体的脚本创建 |
| 第四章 | [网格划分](docs/04_mesh_generation.md) | 种子布置、网格控制、单元类型选择、网格质量检查 |
| 第五章 | [边界条件与载荷](docs/05_boundary_conditions.md) | 固定约束、对称约束、集中力、面压力、温度载荷等 |
| 第六章 | [分析步与作业提交](docs/06_analysis_and_job.md) | 静力分析步、动力分析步、作业创建与提交、参数化扫描 |
| 第七章 | [后处理与结果提取](docs/07_post_processing.md) | 读取 ODB 文件、提取应力/位移、数据导出为 CSV |

---

## 快速开始

### 环境要求

- Abaqus 2019 及以上版本（自带 Python 2.7 内核）
- 或 Abaqus 2023 及以上（部分版本支持 Python 3）
- 外部后处理脚本需要：Python 3.x、`numpy`、`matplotlib`（可选）

### 在 Abaqus 中运行脚本

**方式一：通过 GUI 菜单运行**
```
File → Run Script → 选择 .py 文件
```

**方式二：通过命令行运行**
```bash
abaqus cae noGUI=your_script.py
```

**方式三：在 Abaqus Python 控制台中粘贴执行**
```
View → Command Line Interface (CLI)
```

---

## 参考资料

- [Abaqus Scripting User's Guide](https://help.3ds.com/2023/English/DSSIMULIA_Established/SIMACAECMDRefMap/simacmd-c-ov.htm)
- [Abaqus Scripting Reference Guide](https://help.3ds.com/2023/English/DSSIMULIA_Established/SIMACAESCRRefMap/simascr-c-ov.htm)
- [PyANSYS 官方文档](https://docs.pyansys.com/)

---

## 贡献与反馈

欢迎提交 Issue 或 Pull Request，共同完善本指南。

---

**Keywords:** FEA, Finite Element Analysis, Abaqus, Ansys APDL, Python, 有限元分析, Python 二次开发, 脚本编程
