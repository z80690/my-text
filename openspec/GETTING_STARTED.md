# OpenAPI 规范入门指南

## 什么是 OpenAPI 规范？

OpenAPI 规范（OpenAPI Specification，原称 Swagger Specification）是一种用于描述 RESTful API 的标准格式。它使用 YAML 或 JSON 格式，让人类和机器都能理解 API 的功能、如何调用它、需要什么参数、以及会返回什么结果。

简单来说，OpenAPI 规范就是一份**API 说明书**，它告诉别人：
- 你的 API 有哪些接口（Endpoints）
- 每个接口接受什么参数
- 每个接口返回什么数据
- 接口的安全要求是什么

## 为什么要使用 OpenAPI？

使用 OpenAPI 规范有很多好处：

1. **文档自动化**：不再需要手动编写和维护 API 文档
2. **代码生成**：可以从规范自动生成客户端 SDK 或服务器端代码
3. **前后端协作**：前端开发人员可以在后端代码完成前就开始工作
4. **API 测试**：可以自动生成测试用例
5. **标准化**：团队遵循统一的 API 设计规范

## 核心概念

### 1. OpenAPI 版本

OpenAPI 规范有不同的版本，目前广泛使用的是 3.0 和 3.1 版本。

```yaml
openapi: 3.1.0  # 当前最新稳定版本
```

### 2. Info 对象

`info` 对象包含 API 的元数据信息，如标题、版本、描述等。

```yaml
openapi: 3.1.0
info:
  title: 知识图谱 API
  version: 1.0.0
  description: |
    这是知识图谱项目的 API 文档。
    提供了知识图谱查询和管理功能。
```

### 3. Paths（路径）

`paths` 是 OpenAPI 规范的核心部分，定义了 API 的所有端点。每个路径以 `/` 开头，代表一个资源。

```yaml
paths:
  /health:           # 健康检查端点
    get:             # HTTP 方法：GET
      summary: 健康检查
      responses:
        '200':
          description: 服务正常运行

  /knowledge-graph:  # 知识图谱主路径
    get:             # 查询图谱
      summary: 查询知识图谱
    post:            # 创建新内容
      summary: 创建节点或关系
```

#### 路径参数

如果路径中包含变量，使用 `{variableName}` 表示：

```yaml
paths:
  /knowledge-graph/{graph_id}:  # graph_id 是路径参数
    get:
      summary: 获取指定图谱
      parameters:
        - name: graph_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 成功获取图谱
```

#### HTTP 方法

常见的 HTTP 方法：
- **GET**：获取资源
- **POST**：创建资源
- **PUT**：更新资源（整体替换）
- **PATCH**：更新资源（部分更新）
- **DELETE**：删除资源

### 4. Components（组件）

`components` 是用于定义可重用对象的区域，主要包括：
- **schemas**：数据模型定义
- **responses**：响应定义
- **parameters**：参数定义
- **securitySchemes**：安全方案

#### Schemas（模式）

Schemas 定义了 API 中使用的数据结构，类似于面向对象中的类。

```yaml
components:
  schemas:
    # 定义一个节点
    Node:
      type: object
      properties:
        id:
          type: string
          description: 节点唯一标识
        name:
          type: string
          description: 节点名称
        type:
          type: string
          description: 节点类型
        properties:
          type: object
          description: 节点属性

    # 定义一个关系
    Relationship:
      type: object
      properties:
        source:
          type: string
          description: 源节点ID
        target:
          type: string
          description: 目标节点ID
        type:
          type: string
          description: 关系类型

    # 定义知识图谱响应
    KnowledgeGraph:
      type: object
      properties:
        graph_id:
          type: string
        nodes:
          type: array
          items:
            $ref: '#/components/schemas/Node'
        relationships:
          type: array
          items:
            $ref: '#/components/schemas/Relationship'
```

#### 使用 $ref 引用

通过 `$ref` 可以引用已定义的组件，实现代码复用：

```yaml
responses:
  KnowledgeGraphResponse:
    description: 知识图谱响应
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/KnowledgeGraph'
```

#### 安全方案

定义 API 的安全认证方式：

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

### 5. Responses（响应）

定义 API 可能的响应：

```yaml
paths:
  /health:
    get:
      responses:
        '200':
          description: 服务健康
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "ok"
        '503':
          description: 服务不可用
```

### 6. Parameters（参数）

定义请求参数，支持四种位置：
- **in: path**：路径参数（必需）
- **in: query**：查询参数（可选）
- **in: header**：请求头参数
- **in: cookie**：Cookie 参数

```yaml
parameters:
  - name: limit
    in: query
    description: 返回结果数量限制
    schema:
      type: integer
      default: 10
      minimum: 1
      maximum: 100
  - name: offset
    in: query
    description: 结果偏移量（用于分页）
    schema:
      type: integer
      default: 0
```

## 快速示例：最小化知识图谱 API

以下是一个包含健康检查和图谱查询的最小化示例：

```yaml
openapi: 3.1.0

info:
  title: 知识图谱 API
  version: 1.0.0
  description: 知识图谱管理服务的 RESTful API

paths:
  /health:
    get:
      summary: 健康检查
      description: 检查服务是否正常运行
      responses:
        '200':
          description: 服务健康
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  timestamp:
                    type: string
                    format: date-time

  /knowledge-graph:
    get:
      summary: 查询知识图谱
      description: 获取当前知识图谱的基本信息
      responses:
        '200':
          description: 成功获取图谱信息
          content:
            application/json:
              schema:
                type: object
                properties:
                  graph_id:
                    type: string
                  node_count:
                    type: integer
                  relationship_count:
                    type: integer
```

## 如何从 OpenAPI 规范生成 FastAPI 代码

### 步骤 1：安装必要工具

使用 `openapi-python-client` 工具从 OpenAPI 规范生成 FastAPI 代码：

```bash
pip install openapi-python-client
```

### 步骤 2：生成代码

运行以下命令生成 FastAPI 服务器代码：

```bash
openapi-python-client generate --path openapi/knowledge_graph.v1.yaml
```

这将生成一个完整的 FastAPI 项目，包括：
- 数据模型（基于 Schemas 定义）
- API 路由（基于 Paths 定义）
- 请求参数验证
- 响应模型

### 步骤 3：使用生成的代码

生成的项目结构类似：

```
openapi_client/
├── api/
│   ├── health_api.py
│   └── knowledge_graph_api.py
├── models/
│   ├── node.py
│   ├── relationship.py
│   └── knowledge_graph.py
├── main.py
└── pyproject.toml
```

启动服务器：

```bash
cd openapi_client
uvicorn main:app --reload
```

### 其他代码生成工具

#### 1. FastAPI 官方推荐方式

如果你只需要模型定义，可以使用 `datamodel-codegen`：

```bash
pip install datamodel-codegen

datamodel-codegen --input openapi/knowledge_graph.v1.yaml --output models.py
```

#### 2. Swagger Codegen

```bash
# 安装 Java 运行时后
swagger-codegen generate \
  -i openapi/knowledge_graph.v1.yaml \
  -l python-flask \
  -o ./generated
```

#### 3. openapi-spec-validator

验证 OpenAPI 规范的正确性：

```bash
pip install openapi-spec-validator

python -c "from openapi_spec_validator import validate; validate(open('openapi/knowledge_graph.v1.yaml'))"
```

## 最佳实践

### 1. 使用语义化版本

在 `info.version` 中使用语义化版本：

```yaml
info:
  version: 1.0.0
```

- **1.0.0**：首次发布
- **1.1.0**：新增功能（向后兼容）
- **1.1.1**：修复 Bug
- **2.0.0**：重大变更（不向后兼容）

### 2. 提供清晰的描述

为每个端点和参数添加 `description`：

```yaml
paths:
  /knowledge-graph/{graph_id}:
    get:
      summary: 获取知识图谱详情
      description: |
        根据图谱 ID 获取完整的知识图谱信息。
        返回所有节点和关系数据。
      parameters:
        - name: graph_id
          description: 知识图谱的唯一标识符
```

### 3. 使用枚举定义常量

对于有限取值的参数，使用 `enum`：

```yaml
parameters:
  - name: node_type
    in: query
    schema:
      type: string
      enum:
        - concept
        - entity
        - event
```

### 4. 定义错误响应

为常见错误定义统一的响应格式：

```yaml
components:
  schemas:
    Error:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string
        details:
          type: object

paths:
  /knowledge-graph/{graph_id}:
    get:
      responses:
        '404':
          description: 资源不存在
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
```

### 5. 分组管理大型规范

对于大型 API，将规范拆分为多个文件：

```
openapi/
├── knowledge_graph.v1.yaml
├── components/
│   ├── schemas.yaml
│   └── responses.yaml
└── paths/
    ├── health.yaml
    └── knowledge-graph.yaml
```

然后使用 `$ref` 引用：

```yaml
paths:
  /health:
    $ref: paths/health.yaml
```

## 常见问题

### Q1: OpenAPI 2.0 和 3.0 有什么区别？

OpenAPI 3.0 是一个重大升级，主要改进：
- 支持 `components` 替代 `definitions`
- 支持 `oneOf`、`anyOf` 等复杂模式
- 更好的参数定义
- 支持 JSON Schema Draft 5

### Q2: 如何验证 OpenAPI 规范？

可以使用在线工具或命令行工具：

- **在线验证**: https://swagger.io/tools/swagger-editor/
- **命令行**: `pip install openapi-spec-validator`

### Q3: 如何处理认证？

在 `security` 字段中引用定义的安全方案：

```yaml
security:
  - BearerAuth: []

paths:
  /admin:
    get:
      security:
        - ApiKeyAuth: []
```

### Q4: 如何描述分页？

使用标准分页参数：

```yaml
parameters:
  - name: page
    in: query
    schema:
      type: integer
      default: 1
  - name: page_size
    in: query
    schema:
      type: integer
      default: 20
```

## 资源链接

- [OpenAPI 官方文档](https://spec.openapis.org/oas/v3.1.0)
- [Swagger Editor（在线编辑器）](https://editor.swagger.io)
- [FastAPI 官方文档](https://fastapi.tiangolo.com)
- [OpenAPI Python Client](https://github.com/openapi-generators/openapi-python-client)

## 下一步

1. 查看生成的示例文件：`openapi/knowledge_graph.v1.yaml`
2. 尝试生成 FastAPI 代码
3. 根据项目需求扩展 OpenAPI 规范
4. 使用 OpenAPI 规范生成客户端 SDK（如果需要前端集成）
