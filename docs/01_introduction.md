# 第一章 简介与环境配置

## 1.1 什么是有限元分析（FEA）Python 二次开发？

有限元分析（Finite Element Analysis, FEA）软件（如 Abaqus、Ansys）内置了 Python 解释器，允许用户通过编写 Python 脚本来：

- **自动化建模**：批量创建几何模型、划分网格、施加载荷
- **参数化分析**：通过循环或参数扫描快速进行多工况计算
- **自动后处理**：从输出数据库（ODB）中提取结果、生成报告
- **定制化工作流**：将 FEA 流程集成到企业 CAE 流水线中

相比于手动操作 GUI，脚本化二次开发可以极大地提升效率、减少人为失误。

---

## 1.2 Abaqus Python 环境说明

Abaqus 自带的 Python 解释器版本：

| Abaqus 版本 | Python 版本 |
|------------|------------|
| 2019 ~ 2022 | Python 2.7 |
| 2023 及以上  | Python 3.x（部分版本） |

> ⚠️ **注意**：Abaqus 内置 Python 与系统安装的 Python 是独立的。不能直接 `import` 系统 Python 的第三方库（如 `numpy`）到 Abaqus 脚本中，除非进行特殊配置。

### Abaqus 核心模块

```python
# 用于前处理（建模、分析）的模块
from abaqus import *          # 包含 mdb（Model Database）
from abaqusConstants import * # 包含 Abaqus 常量，如 ON、OFF、FIXED 等

# 用于后处理（读取 ODB 文件）的模块
from odbAccess import *       # 提供 openOdb() 等函数
```

---

## 1.3 脚本执行方式

### 方式一：GUI 菜单运行

在 Abaqus/CAE 中：
```
File → Run Script → 选择 .py 文件 → OK
```

### 方式二：命令行无界面运行（推荐自动化使用）

```bash
# 运行建模脚本（前处理）
abaqus cae noGUI=my_model.py

# 运行后处理脚本
abaqus python my_postprocess.py
```

> `noGUI` 模式不打开图形界面，速度更快，适合批处理。
> `abaqus python` 模式调用 Abaqus 内置的 Python 解释器，可访问 `odbAccess` 等模块。

### 方式三：Abaqus CLI 控制台

在 Abaqus/CAE 界面底部的命令行界面（CLI）中直接输入并执行 Python 语句，适合调试。

---

## 1.4 开发工具推荐

| 工具 | 说明 |
|------|------|
| **Abaqus/CAE 自带 CLI** | 快速调试脚本片段 |
| **VS Code** | 配合 Python 插件，语法高亮与自动补全（需配置 Abaqus Python 解释器路径） |
| **PyCharm** | 功能强大的 Python IDE，同样需配置解释器路径 |
| **记事本 / Notepad++** | 轻量级文本编辑，适合简单脚本 |

### 配置 VS Code 使用 Abaqus Python

1. 找到 Abaqus 安装目录下的 Python 解释器，例如：
   ```
   C:\SIMULIA\EstProducts\2022\win_b64\tools\SMApy\python2.7\python.exe
   ```
2. 在 VS Code 中按 `Ctrl+Shift+P` → `Python: Select Interpreter` → 选择上述路径

---

## 1.5 第一个 Abaqus Python 脚本

以下是一个最简单的 Abaqus 脚本，用于在 Message Area 打印一条信息：

```python
# hello_abaqus.py
# 在 Abaqus/CAE 的 Message Area 打印信息

from abaqus import *

print('Hello, Abaqus!')
```

运行后，在 Abaqus 界面底部的 Message Area 或 CLI 中可以看到输出。

更完整的示例请参考 [`examples/01_hello_abaqus.py`](../examples/01_hello_abaqus.py)。

---

## 1.6 录制宏（Macro）

Abaqus 提供了**宏录制**功能，可以将 GUI 操作自动转换为 Python 脚本，非常适合初学者学习语法：

```
Macro Manager → Create → 执行 GUI 操作 → Stop Recording
```

录制的宏会保存到 `abaqusMacros.py` 文件中，可以直接阅读和修改。

---

## 小结

- FEA Python 二次开发可以自动化建模、分析和后处理流程
- Abaqus 内置 Python 与系统 Python 相互独立
- 推荐使用 `noGUI` 命令行模式进行批量处理
- 通过录制宏快速学习 Abaqus Python 语法

下一章：[Abaqus Python 脚本基础](02_abaqus_basics.md)
