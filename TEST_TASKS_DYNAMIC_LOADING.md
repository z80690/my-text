# 技能动态加载测试任务清单

## 测试任务1：验证动态加载初始化

**任务描述**：启动技能管理器，验证所有技能是否被正确动态加载

**验证步骤**：
1. 调用 `SkillManager().initialize()` 
2. 检查加载的技能数量是否与 `skills` 目录下的技能文件夹数量一致
3. 确认没有使用固定列表加载

**预期结果**：
- 所有包含 `SKILL.md` 的子目录都被识别
- 技能列表应包含：api-token-optimizer, auto-debug, auto-doc, auto-hook, auto-memory, auto-refactor, file-cleaner, local-privacy, my-code-review, tool-usage-tracker

---

## 测试任务2：技能搜索匹配测试

**任务描述**：验证技能关键词匹配功能是否正常工作

**测试查询**：
1. "代码审查" → 应匹配 my-code-review
2. "API Token优化" → 应匹配 api-token-optimizer  
3. "清理未使用文件" → 应匹配 file-cleaner
4. "代码重构" → 应匹配 auto-refactor
5. "文档生成" → 应匹配 auto-doc

---

## 测试任务3：技能详细信息提取

**任务描述**：验证技能元数据解析是否正确

**测试技能**：my-code-review

**验证字段**：
- name: 技能名称
- description: 技能描述
- version: 版本号
- trigger_keywords: 触发关键词列表
- definition_file: SKILL.md 文件路径

---

## 测试任务4：技能热重载功能

**任务描述**：验证 `reload()` 方法能正确重新扫描技能目录

**测试步骤**：
1. 初始化技能管理器
2. 记录初始技能数量
3. 调用 `reload()`
4. 验证重载后技能数量保持一致
5. （可选）在测试期间添加一个新技能文件夹，验证是否被自动发现

---

## 测试任务5：错误处理验证

**任务描述**：验证对不存在技能的请求能正确处理

**测试步骤**：
1. 调用 `get('non-existent-skill')`
2. 验证返回值为 None
3. 确认不会抛出异常

---

## 动态加载核心实现说明

### 工作原理
```
┌─────────────────────────────────────────────────────────────┐
│                    SkillManager.initialize()                │
├─────────────────────────────────────────────────────────────┤
│  1. 检查 .trae/skills 目录是否存在                          │
│  2. 遍历目录下所有子目录                                    │
│  3. 对每个子目录查找 SKILL.md 文件                          │
│  4. 解析 SKILL.md 中的 YAML front matter                    │
│  5. 提取 name, description, trigger_keywords 等字段        │
│  6. 将技能数据存入 self.skills 字典                         │
└─────────────────────────────────────────────────────────────┘
```

### 关键代码
```python
async def initialize(self):
    self.skills = {}
    
    for skill_dir in self.skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_id = skill_dir.name
        skill_md_path = skill_dir / 'SKILL.md'
        
        if skill_md_path.exists():
            skill_data = await self._parse_skill_md(skill_md_path, skill_id)
            if skill_data:
                self.skills[skill_id] = skill_data
```

### 特点
- ✅ 完全动态扫描，无固定技能列表
- ✅ 自动发现新增技能
- ✅ 支持热重载
- ✅ 从 SKILL.md 自动提取元数据
- ✅ 错误处理完善
