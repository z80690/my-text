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
```

---

## LS

列出文件在给定路径。

### 使用说明：

- 路径必须是绝对路径，不能是相对路径
- 如果未提供路径，默认为当前工作目录

### 示例：

```javascript
// 列出当前目录
await ls(".");

// 列出特定目录
await ls("/Users/name/projects");
```

---

## Read

从文件系统读取文件。

### 使用说明：

- 读取文件时，路径必须是绝对路径
- 可以选择指定行数限制和偏移量
- 如果文件内容超过限制，可以分多次读取

### 示例：

```javascript
// 读取整个文件
await read({
  file_path: "/path/to/file.txt"
});

// 读取特定行数
await read({
  file_path: "/path/to/file.txt",
  limit: 100
});

// 从特定偏移量开始读取
await read({
  file_path: "/path/to/file.txt",
  limit: 100,
  offset: 50
});
```

---

## Edit

对文件进行修改。

### 使用说明：

- 需要提供文件路径、搜索字符串和新字符串
- 搜索字符串必须与文件中现有内容完全匹配
- 只替换第一个匹配项

### 示例：

```javascript
await edit({
  file_path: "/path/to/file.txt",
  old_str: "旧字符串",
  new_str: "新字符串"
});
```

---

## MultiEdit

对文件进行多个修改。

### 使用说明：

- 可以在单个调用中对同一文件进行多个编辑
- 所有编辑按顺序应用

### 示例：

```javascript
await multi_edit({
  file_path: "/path/to/file.txt",
  edits: [
    {
      old_str: "旧字符串1",
      new_str: "新字符串1"
    },
    {
      old_str: "旧字符串2",
      new_str: "新字符串2"
    }
  ]
});
```

---

## Write

写入文件到文件系统。

### 使用说明：

- 如果文件不存在，将创建新文件
- 如果文件已存在，将覆盖其内容
- 必须先读取文件（如果已存在），然后才能写入

### 示例：

```javascript
await write({
  file_path: "/path/to/new-file.txt",
  content: "文件内容"
});
```

---

## WebFetch

获取 URL 的内容。

### 使用说明：

- 获取 URL 内容并转换为 markdown 格式
- 如果内容非常大，可能会被截断
- 这是只读操作，不会修改任何文件

### 示例：

```javascript
await web_fetch({
  url: "https://example.com"
});
```

---

## WebSearch

搜索互联网。

### 使用说明：

- 执行网络搜索
- 返回搜索结果列表
- 谨慎使用，频繁搜索会影响用户体验

### 示例：

```javascript
await web_search({
  query: "search query"
});
```

---

## TodoRead

读取待办事项列表。

### 示例：

```javascript
await todo_read({});
```

---

## TodoWrite

写入待办事项列表。

### 参数：

- todos: 待办事项列表

### 示例：

```javascript
await todo_write({
  todos: [
    {
      content: "任务内容",
      status: "in_progress",
      priority: "high"
    }
  ]
});
```
