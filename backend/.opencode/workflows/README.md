# 配置文件路径说明
# 
# 此目录用于存放 oh-my-opencode 工作流配置文件
# 根据你的 oh-my-opencode 版本和配置，配置文件可能需要放在：
# 
# 1. 项目根目录: .opencode/workflows/code-quality.yml
# 2. 或 openspec/workflows/ 目录
# 3. 或在 oh-my-opencode 设置中指定的自定义路径
# 
# 以下是工作流配置文件的 YAML 内容，请根据实际路径放置：
#
# --- BEGIN WORKFLOW CONFIG ---
#
# name: 代码质量守护工作流
# description: 集成 OpenSpec、ESLint、Prettier 的代码规范检查流程
# 
# triggers:
#   - pattern: "全量检查"
#     description: 执行完整的代码规范检查（OpenSpec + ESLint + Prettier）
#   - pattern: "检查接口规范"
#     description: 仅执行 OpenSpec 接口规范检查
#   - pattern: "修复代码风格"
#     description: 仅执行 Prettier 代码格式化
#   - pattern: "语法检查"
#     description: 仅执行 ESLint 语法检查
#   - pattern: "代码检查"
#     description: 执行 ESLint + Prettier 检查
#
# workflow:
#   name: code-quality-guardian
#   parallel: true  # 开启并行执行
#   
#   steps:
#     # 步骤 1: OpenSpec 规范检查
#     - name: openspec-check
#       if: "{{trigger}} contains '规范' or {{trigger}} == '全量检查'"
#       command: |
#         cd backend
#         npx openspec validate ./openspec --strict --output json
#       timeout: 60s
#       continueOnError: true
#       parseOutput: json
#     
#     # 步骤 2: ESLint 语法检查
#     - name: eslint-check
#       if: "{{trigger}} contains '语法' or {{trigger}} contains '检查' or {{trigger}} == '全量检查'"
#       command: |
#         cd backend
#         npx eslint . --format json
#       timeout: 30s
#       continueOnError: true
#       parseOutput: json
#     
#     # 步骤 3: Prettier 格式化检查
#     - name: prettier-check
#       if: "{{trigger}} contains '风格' or {{trigger}} contains '检查' or {{trigger}} == '全量检查'"
#       command: |
#         cd backend
#         npx prettier --check . --ignore-path .prettierignore --output json
#       timeout: 30s
#       continueOnError: true
#
#   # 结果汇总
#   output:
#     format: unified
#     include: [errors, warnings]
#
# --- END WORKFLOW CONFIG ---
