# AB Test: Task Management API

## 项目简介

这是一个用于 AB 测试的简化任务管理 API 项目，使用 Node.js + 原生 HTTP 模块实现。

## 功能特性

### 用户管理 API
- GET /api/users - 获取所有用户
- GET /api/users?id={id} - 获取单个用户
- POST /api/users - 创建用户
- PUT /api/users?id={id} - 更新用户
- DELETE /api/users?id={id} - 删除用户

### 任务管理 API
- GET /api/tasks - 获取所有任务
- GET /api/tasks?id={id} - 获取单个任务
- POST /api/tasks - 创建任务
- PUT /api/tasks?id={id} - 更新任务
- DELETE /api/tasks?id={id} - 删除任务

### 健康检查
- GET /health - 服务健康检查

## 快速开始

### 安装依赖
```bash
npm install
```

### 启动服务器
```bash
npm start
```

### 运行测试
```bash
npm test
```

## 测试结果记录

### 组 A（v5.0 规则体系）
- 执行时间：[待记录]
- Bug 数量：[待记录]
- 规则查阅时间：[待记录]
- 返工次数：[待记录]

### 组 B（v6.0 规则体系）
- 执行时间：[待记录]
- Bug 数量：[待记录]
- 规则查阅时间：[待记录]
- 返工次数：[待记录]

## API 使用示例

### 创建用户
```bash
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com"}'
```

### 创建任务
```bash
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "Test Description", "priority": "high"}'
```

## 测试覆盖

- 用户 CRUD 操作
- 任务 CRUD 操作
- 输入验证
- 错误处理
- 路由 404 处理

## 版本

- API 版本: 1.0.0
- AB Test 版本: v6.0
