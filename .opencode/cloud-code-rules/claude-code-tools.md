# Claude Code Tools Definition (Leaked)

> 来源: Claude Code 泄露源码
> 描述: Claude Code 使用的工具定义和说明

---

## 工具列表

Claude Code 使用以下工具：
- Bash
- Glob
- Grep
- LS
- exit_plan_mode
- Read
- Edit
- MultiEdit
- Write
- NotebookRead
- NotebookEdit
- WebFetch
- TodoRead
- TodoWrite
- WebSearch

---

## Task（任务代理）

启动一个可以访问以下工具的新代理：Bash, Glob, Grep, LS, exit_plan_mode, Read, Edit, MultiEdit, Write, NotebookRead, NotebookEdit, WebFetch, TodoRead, TodoWrite, WebSearch。

### 何时使用 Task 工具：

**推荐使用的情况：**
- 如果正在搜索关键词如 "config" 或 "logger"
- 对于问题如 "哪个文件包含 X?"
- 搜索范围较大，不确定能否在几次尝试中找到正确匹配时

**不推荐使用的情况：**
- 如果要读取特定文件路径，使用 Read 或 Glob 工具
- 如果要搜索特定类定义如 "class Foo"，使用 Glob 工具
- 如果要在特定文件或2-3个文件集合中搜索代码，使用 Read 工具
- 编写代码和运行 bash 命令（使用其他工具）

### 使用说明：

1. **并行启动多个代理**：尽可能使用单个消息并行启动多个代理，以最大化性能

2. **代理返回结果**：代理完成后会返回单个消息。结果不会直接显示给用户。要向用户显示结果，应该发送文本消息给用户，并附上结果的简洁摘要

3. **无状态调用**：每个代理调用都是无状态的。无法向代理发送额外消息，代理也无法在其最终报告之外与您通信。因此，提示应包含高度详细的任务描述，让代理自主执行，并准确指定代理应在最终消息中返回什么信息

4. **信任代理输出**：代理的输出通常可以信任

5. **明确任务类型**：清楚告诉代理是期望编写代码还是仅进行研究（搜索、文件读取、网络获取等），因为代理不知道用户的意图

### 参数格式：

```json
{
  "description": "简短描述（3-5个词）",
  "prompt": "代理要执行的任务"
}
```

---

## Bash

在持久 shell 会话中执行给定的 bash 命令，具有可选超时，确保正确处理和安全措施。

### 执行前步骤：

**1. 目录验证：**
- 如果命令将创建新目录或文件，首先使用 LS 工具验证父目录存在且是正确的位置
- 例如，在运行 "mkdir foo/bar" 之前，先用 LS 检查 "foo" 是否存在且是预期的父目录

**2. 命令执行：**
- 始终用双引号引用包含空格的文件路径（例如：cd "path with spaces/file.txt"）
- 正确引用示例：
  - `cd "/Users/name/My Documents"`（正确）
  - `cd /Users/name/My Documents`（错误 - 会失败）
  - `python "/path/with spaces/script.py"`（正确）
  - `python /path/with spaces/script.py`（错误 - 会失败）
- 确保正确引用后，执行命令
- 捕获命令输出

### 使用说明：

- `command` 参数是必需的
- 可以指定可选的超时时间（毫秒，最多600000ms/10分钟）。如果未指定，命令将在120000ms（2分钟）后超时
- 用5-10个词写清楚简洁的描述，说明此命令的作用，这很有帮助
- 如果输出超过30000个字符，输出将在返回给您之前被截断

**非常重要：**
- 必须避免使用 `find` 和 `grep` 等搜索命令。改用 Grep、Glob 或 Task 工具搜索
- 必须避免使用 `cat`、`head`、`tail`、`ls` 等读取工具，改用 Read 和 LS 工具读取文件
- 如果仍然需要运行 `grep`，先停止。始终先使用预装的 ripgrep `rg`
- 发出多个命令时，使用 `;` 或 `&&` 操作符分隔。不要使用换行符（引号字符串中可以使用换行符）
- 尽量在整个会话中保持当前工作目录，使用绝对路径并避免使用 `cd`。如果需要在特定目录中运行命令，可以将该目录作为参数传递给命令

---

## Glob

根据模式快速列出文件。支持任何代码库大小的 glob 模式。

### 使用说明：

- 模式必须遵循 `gitignore` 格式，而不是标准 shell glob 格式
- 如果模式以斜杠开头（例如 `/src`），它将匹配相对于当前工作目录的路径
- 如果模式不以斜杠开头（例如 `*.js`），它将递归匹配任何目录中的文件
- 模式可以包含 `*` 匹配任意字符（包括路径分隔符），或 `**` 递归匹配任意数量的目录

### 示例：

```javascript
// 查找所有 TypeScript 文件
const tsFiles = await glob("**/*.ts");

// 查找 src 目录下的所有文件
const srcFiles = await glob("src/**/*");

// 查找特定目录
const configFiles = await glob("/config/*");
```

---

## Grep

基于 ripgrep 构建的强大搜索工具。

### 使用说明：

- 永远不要将 `grep` 或 `rg` 作为 Bash 命令调用。Grep 工具已针对正确的权限和访问进行了优化
- 支持完整的正则表达式语法（例如 "log.*Error"、"function\s+\w+"）
- 使用 glob 参数过滤文件（例如 "*.js"、"**/*.tsx"）或 type 参数（例如 "js"、"py"、"rust"）
- 输出模式："content" 显示匹配行，"files_with_matches" 仅显示文件路径（默认），"count" 显示匹配计数
- 默认情况下，模式仅在单行内匹配。对于跨行模式，使用 multiline: true
- 优先使用 `SearchCodebase` 工具进行代码搜索，因为它对于高效的代码库探索更快，需要更少的工具调用

### 示例：

```javascript
// 搜索特定函数
const results = await grep({
  pattern: "function calculateTotal",
  glob: "*.ts"
});

// 搜索错误日志
const errors = await grep({
  pattern: "error|Error|ERROR",
  output_mode: "content",
  head_limit: 20
});
```

---

## LS

列出给定路径中的文件和目录。

### 使用说明：

- path 参数必须是绝对路径，不是相对路径
- 可以使用 ignore 参数提供 glob 模式数组以忽略

### 示例：

```javascript
// 列出当前目录
const files = await ls({ path: "/home/user/project" });

// 列出并忽略某些文件
const sourceFiles = await ls({
  path: "/home/user/project",
  ignore: ["*.test.js", "node_modules/**"]
});
```

---

## Read

从本地文件系统读取文件。

### 使用说明：

- file_path 参数必须是绝对路径，不是相对路径
- 默认情况下，读取最多 2000 行，从文件开头开始
- 可以指定行偏移量（对于大文件特别方便）
- 任何超过 2000 字符的行将被截断
- 结果使用 cat -n 格式返回，行号从1开始
- 能够每次调用查看最多 250 行，最少 200 行

### 示例：

```javascript
// 读取整个文件
const content = await read({
  file_path: "/home/user/project/src/index.ts"
});

// 读取文件的特定范围
const partialContent = await read({
  file_path: "/home/user/project/src/large-file.ts",
  offset: 100,
  limit: 50
});
```

---

## Edit

编辑现有文件。必须遵循 SEARCH/REPLACE 规则设置 old_str 和 new_str 参数。

### SEARCH/REPLACE 规则：

1. **old_str** 是搜索部分，应该是现有源代码中的连续行块
2. **new_str** 是替换部分，应该是要替换到源代码中的行
3. REPLACE 部分必须与 SEARCH 部分不同
4. 该工具将仅替换 SEARCH 部分的第一个匹配项

### 最佳实践：

- 在 SEARCH 部分中包含足够的行以唯一匹配需要更改的行集
- 保持 SEARCH 和 REPLACE 部分简洁
- 仅在需要更改的行中包含，以及少量周围行（如果需要唯一性）
- 不要在 SEARCH 或 REPLACE 部分中包含长串未更改的行

### 示例：

```javascript
// 替换函数实现
await edit({
  file_path: "/home/user/project/src/utils.ts",
  old_str: `function oldFunction() {
  return "old";
}`,
  new_str: `function newFunction() {
  return "new";
}`
});
```

---

## MultiEdit

在一次调用中编辑文件中的多个位置。有助于在一次操作中更改文件中的多个位置，这比多次调用 Edit 工具更快。

### 使用说明：

- 所有编辑必须应用于同一个文件
- 每个编辑必须遵循与 Edit 工具相同的 SEARCH/REPLACE 格式
- 编辑按顺序应用，因此一个编辑可能会影响后续编辑的搜索

### 示例：

```javascript
await multiEdit({
  file_path: "/home/user/project/src/config.ts",
  edits: [
    {
      old_str: "const API_URL = 'http://old-api.com';",
      new_str: "const API_URL = 'https://new-api.com';"
    },
    {
      old_str: "const TIMEOUT = 5000;",
      new_str: "const TIMEOUT = 10000;"
    }
  ]
});
```

---

## Write

写入文件到本地文件系统。

### 使用说明：

- 如果该路径已存在文件，此工具将覆盖它
- 如果父目录不存在，将自动创建
- 始终使用绝对路径

### 示例：

```javascript
await write({
  file_path: "/home/user/project/src/new-file.ts",
  content: `export function hello() {
  console.log("Hello, World!");
}`
});
```

---

## WebFetch

获取网页内容。

### 使用说明：

- 用于获取特定网页的内容
- 可以提取网页的文本内容供分析

### 示例：

```javascript
const pageContent = await webFetch({
  url: "https://docs.anthropic.com/en/docs/claude-code"
});
```

---

## WebSearch

搜索网络并使用结果来通知响应。

### 使用说明：

- 用于搜索网络信息
- 返回搜索结果供分析

### 示例：

```javascript
const searchResults = await webSearch({
  query: "Claude Code documentation"
});
```

---

## TodoRead / TodoWrite

读取和写入待办事项列表。

### 使用说明：

- 用于跟踪任务进度
- 可以创建、更新和读取待办事项

### 示例：

```javascript
// 写入待办事项
await todoWrite({
  todos: [
    { id: "1", content: "分析代码库", status: "in_progress", priority: "high" },
    { id: "2", content: "实现功能", status: "pending", priority: "medium" }
  ]
});

// 读取待办事项
const todos = await todoRead({});
```

---

## NotebookRead / NotebookEdit

读取和编辑笔记本文件。

### 使用说明：

- 用于处理笔记本格式的文件
- 可以读取和修改笔记本内容

---

## exit_plan_mode

退出计划模式。

### 使用说明：

- 用于退出当前的计划模式
- 通常在完成任务规划后使用

---

## 工具使用原则

1. **并行执行**：尽可能并行使用多个工具以最大化性能
2. **工具优先**：仅使用工具完成任务，不使用 bash 或代码注释作为通信手段
3. **验证优先**：在创建新文件或目录前，先验证父目录存在
4. **路径绝对**：始终使用绝对路径，避免相对路径
5. **安全搜索**：避免使用 `find` 和 `grep` 命令，改用 Grep 和 Glob 工具
6. **简洁描述**：为 bash 命令提供5-10个词的清晰描述

---

**版本**: Claude Code 泄露版本  
**提取日期**: 2026-05-08
