# STM32 Debug Skill for AI Agents

这是一个专为 AI Agent（如基于大语言模型的编程助手）设计的 STM32 调试技能包（Skill）。它封装了常用的 STM32 固件编译、烧录、调试、寄存器查看以及变量实时监控功能，旨在让 AI 助手能够无缝、高效地协助开发者进行 STM32 嵌入式开发。

## ✨ 核心特性

- **一键烧录**: 封装 OpenOCD 烧录流程，支持快速部署。
- **实时监控 (无停机)**: 利用 GDB 和 OpenOCD TCL 接口，支持在程序运行期间实时读取全局变量（包括复杂的**结构体成员**、数组等）。
- **寄存器解析**: 内置 `read_svd.py` 脚本，可直接解析 `.svd` 文件，根据外设和寄存器名称查看寄存器位域定义和当前值。
- **SWO 日志捕获**: 自动配置并捕获通过 SWO (Serial Wire Output) 输出的 `printf` 调试信息。
- **开箱即用**: 提供预打包好的 `stm32-debug-skill.tar.gz`，解压即用。

## 📦 包含内容

解压 `stm32-debug-skill.tar.gz` 后，包含以下内容：

```text
stm32-debug-skill/
├── SKILL.md                  # AI Agent 读取的技能说明和使用指南
├── STM32F746.svd             # (示例) 芯片 SVD 文件，用于解析寄存器
└── scripts/
    ├── flash.sh              # 固件烧录脚本
    ├── monitor_swo.sh        # SWO 日志监听脚本
    ├── read_svd.py           # SVD 解析与寄存器读取脚本
    └── stm32_monitor.py      # GDB 符号解析与内存实时监控脚本
```

## 🛠️ 环境依赖

在使用此 Skill 前，主机环境需要安装以下工具：
- `arm-none-eabi-gcc` (用于编译)
- `openocd` (用于烧录和底层通信)
- `gdb-multiarch` (用于解析 ELF 符号和结构体类型)
- `python3` (运行监控脚本)

## 🚀 使用示例 (Agent 指令)

当将此 Skill 挂载到 AI Agent 后，你可以直接使用自然语言下达指令，Agent 会自动调用对应的脚本。

### 1. 烧录固件
```bash
# Agent 将执行：
./scripts/flash.sh build/firmware.elf
```

### 2. 实时监控结构体成员
```bash
# Agent 将执行：
./scripts/stm32_monitor.py --elf build/firmware.elf --var "sensor_data.temperature" --type float --interval 1
```

### 3. 查看外设寄存器
```bash
# Agent 将执行：
./scripts/stm32_monitor.py --svd STM32F746.svd --reg GPIOA MODER
```

### 4. 监听 printf 日志 (SWO)
```bash
# Agent 将执行：
./scripts/monitor_swo.sh
# 并在后台查看 swo.log
```

## 📝 如何集成到你的 Agent

1. 下载 `stm32-debug-skill.tar.gz`。
2. 解压到你的项目或 Agent 的 skills 目录下（例如 `.trae/skills/stm32-debug/`）。
3. 确保 `scripts/` 目录下的所有 `.sh` 和 `.py` 文件具有可执行权限 (`chmod +x scripts/*`)。
4. Agent 读取 `SKILL.md` 后即可习得这些调试能力。
