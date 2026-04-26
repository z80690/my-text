# Agent Framework

## 概述
这是一个用于 TRAE IDE 的 MCP 服务器框架，提供了基本的 JSON-RPC 服务。

## 目录结构
```
.trae/frameworks/
└── agent_framework_mcp_server.py  # 服务器主文件
```

## 功能特性
- 支持 JSON-RPC 2.0 协议
- 提供 initialize 和 tools/list 方法
- 支持标准输入输出模式

## 运行方式
服务器可以通过以下命令启动：
```bash
python -m agent_framework_mcp_server
```

## 配置说明
该框架会自动处理请求和响应，无需额外配置。
