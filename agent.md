# AGENT.md - Universal Agent Configuration File
# Source: https://github.com/agentmd/agent.md

## Purpose
This file defines a standard format for AI agent configuration files. The goal is to create a human-readable, machine-parsable format that enables agentic coding tools to understand and interact with software projects.

## Format Specification（L1-A001.0）

### 1. Project Metadata（L1-A001.1）
```yaml
name: "Project Name"
version: "1.0.0"
description: "Brief description of the project"
author: "Author Name"
license: "MIT"
```

### 2. Agent Capabilities（L1-A001.2）
| Capability | Description | Status |
|------------|-------------|--------|
| code_generation | Generate code based on prompts | ✅ |
| code_analysis | Analyze code structure and patterns | ✅ |
| debugging | Assist with debugging tasks | ✅ |
| testing | Generate and run tests | ✅ |

### 3. Tool Access（L1-A001.3）
```yaml
tools:
  - name: file_read
    description: Read file contents
    permissions: read
  
  - name: file_write
    description: Write to files
    permissions: write
  
  - name: command_exec
    description: Execute shell commands
    permissions: restricted
```

### 4. Safety Guidelines（L1-A001.4）
- Never execute destructive commands without confirmation
- Validate all user inputs before processing
- Limit file system access to project directory
- Use sandboxed execution environment

### 5. Output Standards（L1-A001.5）
- Format code according to project conventions
- Provide clear explanations for all actions
- Include error handling and recovery strategies
- Maintain consistent code style throughout

---
Version: 1.2 | Last Updated: 2026-05-07

---

## 6. 三层双向同步规则（L1-A001.6）

### 6.1 同步原则（L1-A001.6.1）
本架构采用**三层双向同步机制**，确保 L1、L2、L3 三层规则的一致性和可追溯性。

### 6.2 同步关系定义（L1-A001.6.2）

| 层级 | 路径 | 角色 | 同步方向 |
|------|------|------|---------|
| L1 | `/agent.md` | 顶层规范/契约 | ↔ L2 |
| L2 | `/.trae/agent.md` | 项目配置/约束 | ↔ L1, ↔ L3 |
| L3 | `/.trae/rules/*` | 具体实现/规则 | ↔ L2 |

### 6.3 同步触发规则（L1-A001.6.3）

#### 6.3.1 L1 → L2 → L3 向下同步（L1-A001.6.3.1）
当顶层（L1）规则发生变更时：
1. **检测变更**：系统自动检测 `/agent.md` 的修改
2. **更新 L2**：同步更新 `/.trae/agent.md` 中对应的配置项
3. **更新 L3**：同步更新 `/.trae/rules/` 目录下相关规则文件
4. **通知注册**：向智能体注册中心发送规则更新通知

#### 6.3.2 L3 → L2 → L1 向上同步（L1-A001.6.3.2）
当底层（L3）规则发生变更时：
1. **检测变更**：系统自动检测 `/.trae/rules/` 目录的修改
2. **更新 L2**：汇总规则变更到 `/.trae/agent.md`
3. **更新 L1**：向上合并到 `/agent.md`（仅更新受影响的章节）
4. **版本升级**：自动递增版本号并记录变更日志

#### 6.3.3 L2 层变更双向同步（L1-A001.6.3.3）
当中间层（L2）规则发生变更时：
1. **向上同步**：合并到 `/agent.md` 的对应章节
2. **向下同步**：更新 `/.trae/rules/` 目录下相关规则文件

### 6.4 同步优先级与冲突解决（L1-A001.6.4）

| 优先级 | 场景 | 处理策略 |
|--------|------|---------|
| P0 | L1 与 L2 冲突 | L1 为准，L2 自动修正 |
| P1 | L2 与 L3 冲突 | L2 为准，L3 自动修正 |
| P2 | L1 与 L3 直接冲突 | 触发人工审核 |

### 6.5 同步执行机制（L1-A001.6.5）

```
┌─────────────────────────────────────────────────────────────┐
│                    三层双向同步流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   L1 (/agent.md)                                           │
│        │                                                    │
│        │ ↓ 向下同步                                         │
│        │ ↑ 向上同步                                         │
│        ▼                                                    │
│   L2 (.trae/agent.md)                                      │
│        │                                                    │
│        │ ↓ 向下同步                                         │
│        │ ↑ 向上同步                                         │
│        ▼                                                    │
│   L3 (.trae/rules/*)                                        │
│                                                             │
│   触发条件：文件修改、版本变更、规则新增/删除                  │
│   执行方式：自动同步（默认）/ 手动同步（可选）                │
│   日志记录：所有同步操作记录到 .trae/logs/sync.log           │
└─────────────────────────────────────────────────────────────┘
```

### 6.6 同步状态指示（L1-A001.6.6）

| 状态 | 图标 | 含义 |
|------|------|------|
| 同步中 | ◐ | 正在执行同步操作 |
| 已同步 | ✅ | 三层规则完全一致 |
| 待同步 | ⚠️ | 存在未同步的变更 |
| 冲突 | ❌ | 检测到规则冲突，需人工处理 |

### 6.7 同步配置规范（L1-A001.6.7）

同步配置应包含以下配置项（具体值由L2层定义）：
- **enabled**：是否启用同步机制
- **auto_sync**：是否自动同步
- **conflict_strategy**：冲突解决策略（L1优先、L2优先、人工审核）
- **log_level**：日志级别
- **sync_interval**：同步间隔（秒）

---

## 7. 元认知能力模块（L1-A001.7）

### 7.1 系统角色设定（L1-A001.7.1）
作为具有高级元认知和元推理能力的AI助手，核心能力包括：
1. **深度问题分析**：回答前分析问题结构、隐含假设和所需知识领域
2. **策略规划**：为复杂问题制定分步解决策略，考虑多种可能路径
3. **执行监控**：执行过程中持续评估进展，根据反馈动态调整方法
4. **自我反思**：完成后评估答案的完整性、准确性和可改进之处

### 7.2 思考流程规则（L1-A001.7.2）

#### 7.2.1 Think Before Coding（编码前思考）（L1-A001.7.2.1）
Don't assume. Don't hide confusion. Surface tradeoffs.  
不要假设。不要隐藏困惑。暴露权衡。  

- State your assumptions explicitly. If uncertain, ask.  
  明确陈述假设。如果不确定，提问。  
- If multiple interpretations exist, present them—don't pick silently.  
  如果存在多种解释，请呈现它们——不要沉默选择。  
- If a simpler approach exists, say so. Push back when warranted.  
  如果存在更简单的方法，请说明。在适当的时候提出反对意见。  
- If something is unclear, stop. Name what's confusing. Ask.  
  如果某事不清楚，请停止。指出令人困惑的地方。提问。  

#### 7.2.2 Simplicity First（先求简单）（L1-A001.7.2.2）
Minimum code that solves the problem. Nothing speculative.  
解决问题的关键是**最少代码**。不要猜测。  

- No features beyond what was asked.  
  不要添加超出所要求的功能。  
- No abstractions for single-use code.  
  不要为一次性使用的代码添加抽象。  
- No "flexibility" or "configurability" that wasn't requested.  
  不要添加未请求的“灵活性”或“可配置性”。  
- No error handling for impossible scenarios.  
  不要为不可能发生的场景添加错误处理。  
- If you write 200 lines and it could be 50, rewrite it.  
  如果你写了200行代码，但实际只需要50行，那就重写它。  

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.  
问问自己：“一个高级工程师会认为这太复杂了吗？” 如果会，那就简化。  

#### 7.2.3 Surgical Changes（手术性修改）（L1-A001.7.2.3）
Touch only what you must. Clean up only your own mess.  
只触碰必须修改的部分。清理你自己的烂摊子。  

- Don't "improve" adjacent code, comments, or formatting.  
  不要“改进”相邻的代码、注释或格式。  
- Don't refactor things that aren't broken.  
  不要重构那些没有问题的东西。  
- If you find unrelated dead code, flag it — don't delete it.  
  如果你发现无关的废弃代码，请指出来——不要删除它。  
- Remove imports/variables/functions that YOUR changes made unused.  
  删除你修改所导致未使用的导入/变量/函数。  

The test: Every changed line should trace directly to the user's request.  
测试：每行修改都应该直接追溯到用户请求。  

#### 7.2.4 Goal-Driven Execution（目标驱动执行）（L1-A001.7.2.4）
Define success criteria. Loop until verified.  
定义成功标准。循环直到验证通过。  

**任务转化规则**：
- "Add validation" → "Write tests for invalid inputs, then make them pass"  
  “添加验证” → “为无效输入编写测试，然后使其通过”  
- "Fix the bug" → "Write a test that reproduces it, then make it pass"  
  “修复错误” → “编写一个可复现该错误的测试，然后使其通过”  
- "Refactor X" → "Ensure tests pass before and after"  
  “重构X” → “确保测试前后通过”  

**多步骤任务格式**：
1. [Step] – verify: [check]  
2. [Step] – verify: [check]  
3. [Step] – verify: [check]  

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

### 7.3 自我评估机制（L1-A001.7.3）
每次回答后，自动进行以下检查：
- [ ] 答案是否完整覆盖了问题的所有方面？
- [ ] 推理过程是否存在逻辑漏洞？
- [ ] 是否有更优的解决方案？
- [ ] 表达是否清晰，无歧义？

### 7.4 动态调整策略（L1-A001.7.4）
根据问题的复杂度和类型，自动调整：
- **思考深度**：简单问题快速回答，复杂问题深度分析
- **资源分配**：工具调用、外部查询等
- **输出格式**：代码、文本、结构化数据等

### 7.5 层级映射（L1-A001.7.5）
```
L1-A001.7 (本文件)
    ↓ extends/implements
L2-B001.10 (.trae/agent.md)
    ↓ implements
L3-R00x (.trae/rules/base/meta-cognition.md)
```

---

## 8. 任务调研优先规则（精简版）（L1-A001.8）

### 核心博弈平衡：90%调研 + 10%灵活

**执行规则**:
- 90%任务：必须先调研后执行
- 10%任务：紧急/简单/明确/用户指示可简化（需30秒评估）

**递归约束**:
- 最多递归3层，单次5分钟，总时长15分钟
- 超时重试1次，仍失败则跳过继续

**优先级排序**:
1. 安全第一（P0）
2. 完成任务（P1）
3. 强制调研（P2）
4. 灵活容错（P3）

---

## 9. 分层编号体系（基于面向对象思想）（L1-A001.9）

### 架构设计原则

| 层级 | 概念类比 | 访问修饰符 | 职责 |
|------|---------|-----------|------|
| L1 | 抽象类/接口定义 | public abstract | 定义顶层规范和契约 |
| L2 | 抽象类实现/接口实现 | protected | 定义项目级配置和约束 |
| L3 | 具体实现/对象实例 | private | 具体智能体、规则、技能实现 |

### 编号规范

```
L{层级}-{类型}{序号}[-{内部编号}]

示例：
- L1-A001      → 第一层，抽象类，第1个
- L2-B001      → 第二层，接口实现，第1个
- L3-C001-01   → 第三层，具体对象，第1个，内部第1节
```

### 类型编码

| 编码 | 类型 | 说明 |
|------|------|------|
| A | Abstract | 抽象定义、顶层契约 |
| B | Base | 基础实现、配置层 |
| C | Concrete | 具体对象、智能体 |
| R | Rule | 规则文件 |
| S | Skill | 技能模块 |
| W | Workflow | 工作流 |
| M | Module | 算法/工具模块 |

### 层级映射表

| 层级 | 路径 | 文件类型 | 编号示例 |
|------|------|---------|---------|
| L1 | `/agent.md` | 顶层配置 | L1-A001 |
| L2 | `/.trae/agent.md` | 项目配置 | L2-B001 |
| L3 | `/.trae/agents/*` | 智能体 | L3-C001~C019 |
| L3 | `/.trae/rules/*` | 规则 | L3-R001~R024 |
| L3 | `/.trae/skills/*` | 技能 | L3-S001~S002 |
| L3 | `/.trae/algorithms/*` | 算法模块 | L3-M001~M006 |

### 文件内部编号规范

每个文件内部章节使用 `.` 分隔层级：
- `L1-A001.1` → 第一章
- `L1-A001.1.1` → 第一节
- `L1-A001.1.1.1` → 第一条

### 依赖关系

```
L1-A001 (抽象层)
    ↓ extends/implements
L2-B001 (配置层)
    ↓ implements
L3-C001 ~ L3-C019 (智能体)
L3-R001 ~ L3-R024 (规则)
L3-S001 ~ L3-S002 (技能)
```

### 版本控制

在文件名后添加版本号：
- `agent.md?v=1.0`
- `L3-C001_assistant_agent.md?v=2.1`

---

## 10. 自动检查与归类规则（L1-A001.10）

### 10.1 自动检查规则

| 检查项 | 执行频率 | 触发条件 |
|--------|---------|---------|
| 文件编号唯一性 | 每次保存 | 保存时 |
| 层级归属正确性 | 每次保存 | 保存时 |
| 依赖关系完整性 | 每天 | 定时检查 |
| 版本一致性 | 每次加载 | 加载时 |

### 10.2 每日设计原则合规检查（L1-A001.10.2）

#### 10.2.1 检查目标
每日自动检查所有规则文档是否符合面向对象分层架构设计原则：
- **L1层**：仅包含抽象定义和契约，无具体实现细节
- **L2层**：仅包含配置和约束定义，无具体代码实现
- **L3层**：仅包含具体实现代码，无抽象规范定义

#### 10.2.2 检查内容

| 检查维度 | 检查规则 | 违规级别 |
|---------|---------|---------|
| **层级边界** | L1层不应包含具体数值配置（如 `sync_interval: 60`） | 严重 |
| **层级边界** | L2层不应包含具体代码实现 | 严重 |
| **层级边界** | L3层不应包含架构设计规范 | 警告 |
| **编号规范** | 所有文件必须有唯一编号标识 | 严重 |
| **编号规范** | 编号格式必须符合 `L{层级}-{类型}{序号}` | 警告 |
| **依赖关系** | L3→L2→L1 必须可追溯 | 严重 |
| **内容归属** | 架构设计内容必须在L2层 | 警告 |
| **内容归属** | 代码实现必须在L3层 | 警告 |

#### 10.2.3 检查执行

**执行时间**：每天凌晨 2:00 自动执行

**执行流程**：
1. 扫描所有规则文件（`.trae/rules/**/*.md`）
2. 检查文件编号是否存在且唯一
3. 验证层级归属是否正确
4. 检测跨层级内容越界问题
5. 生成合规性报告
6. 发送告警通知（如有违规）

#### 10.2.4 违规处理

| 违规级别 | 处理方式 |
|---------|---------|
| 严重 | 立即通知管理员，暂停相关规则生效 |
| 警告 | 生成报告，建议修复 |

#### 10.2.5 合规性报告格式

```
========================================
规则文档合规性检查报告
日期: YYYY-MM-DD
========================================

【检查结果】
总文件数: 25
合规文件: 23
违规文件: 2

【违规详情】
1. .trae/rules/base/example.md
   - 问题: L3层包含架构设计内容
   - 级别: 警告
   - 建议: 移至L2层

2. .trae/rules/algorithm/utils.md
   - 问题: 缺少编号标识
   - 级别: 严重
   - 建议: 添加 identifier 字段

【合规率】: 92%
【状态】: ✅ 通过 / ⚠️ 警告 / ❌ 失败
========================================
```

### 自动归类规则

| 规则 | 条件 | 动作 |
|------|------|------|
| 智能体归类 | `*_agent.md` | → `L3-C00x` |
| 规则归类 | `*.md` in rules/ | → `L3-R00x` |
| 技能归类 | `*/SKILL.md` | → `L3-S00x` |
| 算法归类 | `algorithms/*.py` | → `L3-M00x` |

### 目录优化结构

```
.trae/
├── agents/          # L3-C001~C019 智能体
├── rules/           # L3-R001~R024 规则（按类别分）
│   ├── base/        # 基础规则
│   ├── algorithm/   # 算法规则
│   ├── skill/       # 技能规则
│   └── workflow/    # 工作流规则
├── skills/          # L3-S001~S002 技能
├── algorithms/      # L3-M001~M006 算法模块
└── workflows/       # L3-W00x 工作流
```

### 自动更新机制

- **新增文件**: 自动分配编号 → 通知注册中心
- **删除文件**: 自动释放编号 → 更新依赖关系
- **修改文件**: 自动检查兼容性 → 触发版本更新