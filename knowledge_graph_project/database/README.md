# 知识图谱数据库 Schema 文档

## 1. 架构概述

本 Schema 用于存储哔哩哔哩和今日头条平台的知识图谱数据，支持用户关系网络、内容关联关系和话题标签的存储与查询。核心包含 6 张数据表，通过外键关联形成完整的知识图谱结构。

## 2. 数据表结构

### 2.1 平台表 (platforms)

存储支持的数据平台配置信息。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 平台唯一标识 |
| platform_key | VARCHAR(50) | UNIQUE, NOT NULL | 平台标识符 (bilibili/toutiao) |
| platform_name | VARCHAR(100) | NOT NULL | 平台显示名称 |
| platform_url | VARCHAR(255) | - | 平台官网地址 |
| api_base_url | VARCHAR(255) | - | API 基础地址 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否启用 |
| config | JSONB | DEFAULT '{}' | 扩展配置 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 更新时间 |

**索引**：
- `idx_platforms_key` - 平台标识符唯一索引

**默认数据**：
```sql
INSERT INTO platforms (platform_key, platform_name, platform_url, api_base_url) VALUES
('bilibili', '哔哩哔哩', 'https://www.bilibili.com', 'https://api.bilibili.com'),
('toutiao', '今日头条', 'https://www.toutiao.com', 'https://www.toutiao.com/api');
```

### 2.2 用户表 (users)

存储用户基本信息及统计数据。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 用户唯一标识 |
| platform_id | UUID | REFERENCES platforms(id) | 所属平台 |
| external_user_id | VARCHAR(100) | NOT NULL | 平台原始用户 ID |
| username | VARCHAR(255) | - | 用户名 |
| display_name | VARCHAR(255) | - | 显示名称 |
| avatar_url | VARCHAR(500) | - | 头像地址 |
| bio | TEXT | - | 个人简介 |
| gender | VARCHAR(20) | - | 性别 (male/female/unknown) |
| birthday | DATE | - | 生日 |
| location | VARCHAR(255) | - | 所在地 |
| is_verified | BOOLEAN | DEFAULT FALSE | 是否认证 |
| verification_type | VARCHAR(50) | - | 认证类型 |
| follower_count | BIGINT | DEFAULT 0 | 粉丝数 |
| following_count | BIGINT | DEFAULT 0 | 关注数 |
| video_count | INTEGER | DEFAULT 0 | 视频数 |
| article_count | INTEGER | DEFAULT 0 | 文章数 |
| like_count | BIGINT | DEFAULT 0 | 获赞数 |
| play_count | BIGINT | DEFAULT 0 | 播放数 |
| read_count | BIGINT | DEFAULT 0 | 阅读数 |
| status | user_status | DEFAULT 'active' | 状态 (active/inactive/banned/verified) |
| last_active_at | TIMESTAMP WITH TIME ZONE | - | 最后活跃时间 |
| profile_url | VARCHAR(500) | - | 个人主页地址 |
| level | INTEGER | DEFAULT 0 | 等级 |
| experience | BIGINT | DEFAULT 0 | 经验值 |
| coins | BIGINT | DEFAULT 0 | 硬币数 |
| tags | TEXT[] | - | 用户标签数组 |
| interests | TEXT[] | - | 兴趣标签数组 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 更新时间 |

**唯一约束**：
- `(platform_id, external_user_id)` - 平台内用户唯一

**索引**：
- `idx_users_platform` - 平台索引
- `idx_users_external_id` - 外部 ID 索引
- `idx_users_username` - 用户名索引
- `idx_users_follower_count` - 粉丝数降序索引
- `idx_users_status` - 状态索引
- `idx_users_search` - 全文搜索索引 (GIN)

**触发器**：
- `update_users_updated_at` - 自动更新 updated_at 字段

### 2.3 内容表 (contents)

存储视频、文章、动态等内容实体。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 内容唯一标识 |
| platform_id | UUID | REFERENCES platforms(id) | 所属平台 |
| external_content_id | VARCHAR(100) | NOT NULL | 平台原始内容 ID |
| content_type | content_type | NOT NULL | 内容类型 (video/article/dynamic/live 等) |
| author_id | UUID | REFERENCES users(id) | 作者 ID |
| title | VARCHAR(500) | - | 内容标题 |
| description | TEXT | - | 描述 |
| content_text | TEXT | - | 原始文本内容 |
| content_html | TEXT | - | HTML 格式内容 |
| cover_url | VARCHAR(500) | - | 封面图地址 |
| thumbnail_urls | TEXT[] | - | 缩略图数组 |
| video_url | VARCHAR(500) | - | 视频地址 |
| duration | INTEGER | - | 视频时长(秒) |
| view_count | BIGINT | DEFAULT 0 | 播放/阅读数 |
| like_count | BIGINT | DEFAULT 0 | 点赞数 |
| dislike_count | BIGINT | DEFAULT 0 | 踩数 |
| comment_count | BIGINT | DEFAULT 0 | 评论数 |
| share_count | BIGINT | DEFAULT 0 | 分享数 |
| collect_count | BIGINT | DEFAULT 0 | 收藏数 |
| coin_count | BIGINT | DEFAULT 0 | 投币数 |
| danmaku_count | BIGINT | DEFAULT 0 | 弹幕数 |
| score | DECIMAL(3,2) | DEFAULT 0.0 | 评分 |
| category_id | VARCHAR(100) | - | 分类 ID |
| category_name | VARCHAR(100) | - | 分类名称 |
| tags | TEXT[] | - | 标签数组 |
| topics | TEXT[] | - | 话题数组 |
| latitude | DECIMAL(10,8) | - | 纬度 |
| longitude | DECIMAL(11,8) | - | 经度 |
| location_name | VARCHAR(255) | - | 位置名称 |
| published_at | TIMESTAMP WITH TIME ZONE | - | 发布时间 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 更新时间 |
| is_deleted | BOOLEAN | DEFAULT FALSE | 是否删除 |
| is_top | BOOLEAN | DEFAULT FALSE | 是否置顶 |
| is_featured | BOOLEAN | DEFAULT FALSE | 是否推荐 |
| raw_data | JSONB | DEFAULT '{}' | 原始数据 |

**唯一约束**：
- `(platform_id, external_content_id)` - 平台内内容唯一

**索引**：
- `idx_contents_platform` - 平台索引
- `idx_contents_type` - 内容类型索引
- `idx_contents_author` - 作者索引
- `idx_contents_published` - 发布时间降序索引
- `idx_contents_view_count` - 播放数降序索引
- `idx_contents_like_count` - 点赞数降序索引
- `idx_contents_tags` - 标签 GIN 索引
- `idx_contents_topics` - 话题 GIN 索引

**触发器**：
- `update_contents_updated_at` - 自动更新 updated_at 字段

### 2.4 评论表 (comments)

存储评论及回复关系。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 评论唯一标识 |
| platform_id | UUID | REFERENCES platforms(id) | 所属平台 |
| external_comment_id | VARCHAR(100) | NOT NULL | 平台原始评论 ID |
| content_id | UUID | REFERENCES contents(id) ON DELETE CASCADE | 所属内容 ID |
| parent_id | UUID | REFERENCES comments(id) ON DELETE CASCADE | 父评论 ID |
| root_id | UUID | REFERENCES comments(id) ON DELETE CASCADE | 根评论 ID |
| author_id | UUID | REFERENCES users(id) | 评论者 ID |
| content | TEXT | NOT NULL | 评论内容 |
| like_count | BIGINT | DEFAULT 0 | 点赞数 |
| reply_count | INTEGER | DEFAULT 0 | 回复数 |
| is_top | BOOLEAN | DEFAULT FALSE | 是否置顶 |
| is_selected | BOOLEAN | DEFAULT FALSE | 是否精选 |
| raw_data | JSONB | DEFAULT '{}' | 原始数据 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 更新时间 |

**唯一约束**：
- `(platform_id, external_comment_id)` - 平台内评论唯一

**索引**：
- `idx_comments_content` - 内容索引
- `idx_comments_author` - 作者索引
- `idx_comments_parent` - 父评论索引
- `idx_comments_root` - 根评论索引
- `idx_comments_created` - 创建时间降序索引

**触发器**：
- `update_comments_updated_at` - 自动更新 updated_at 字段

### 2.5 关系表 (relations)

知识图谱核心表，存储实体间的各种关系。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 关系唯一标识 |
| platform_id | UUID | REFERENCES platforms(id) | 所属平台 |
| relation_type | relation_type | NOT NULL | 关系类型 (follows/fans/likes/collects 等) |
| source_entity_type | VARCHAR(50) | NOT NULL | 源实体类型 (user/content/comment) |
| source_entity_id | UUID | NOT NULL | 源实体 ID |
| target_entity_type | VARCHAR(50) | NOT NULL | 目标实体类型 |
| target_entity_id | UUID | NOT NULL | 目标实体 ID |
| weight | DECIMAL(5,4) | DEFAULT 1.0 | 关系权重 |
| metadata | JSONB | DEFAULT '{}' | 扩展属性 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 创建时间 |
| expires_at | TIMESTAMP WITH TIME ZONE | - | 过期时间 |

**唯一约束**：
- `(platform_id, relation_type, source_entity_id, target_entity_id)` - 关系唯一

**索引**：
- `idx_relations_type` - 关系类型索引
- `idx_relations_source` - 源实体复合索引
- `idx_relations_target` - 目标实体复合索引
- `idx_relations_platform` - 平台索引

**关系类型枚举**：
- `follows` - 关注
- `fans` - 粉丝
- `likes` - 点赞
- `collects` - 收藏
- `shares` - 分享
- `comments` - 评论
- `replies` - 回复
- `mentions` - 提及
- `collaborates` - 合作
- `participates` - 参与
- `creates` - 创建
- `tags` - 标签
- `categorizes` - 分类
- `features` - 特性
- `similar_to` - 相似
- `derived_from` - 衍生
- `topic_of` - 话题
- `location_of` - 位置
- `language_of` - 语言
- `awards` - 获奖
- `promotes` - 推荐
- `disputes` - 争议
- `related` - 相关

### 2.6 话题表 (topics)

存储话题/标签信息及热度数据。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PRIMARY KEY | 话题唯一标识 |
| platform_id | UUID | REFERENCES platforms(id) | 所属平台 |
| external_topic_id | VARCHAR(100) | NOT NULL | 平台原始话题 ID |
| name | VARCHAR(255) | NOT NULL | 话题名称 |
| description | TEXT | - | 话题描述 |
| cover_url | VARCHAR(500) | - | 封面图地址 |
| profile_url | VARCHAR(500) | - | 话题主页地址 |
| content_count | BIGINT | DEFAULT 0 | 内容数 |
| view_count | BIGINT | DEFAULT 0 | 浏览数 |
| follower_count | BIGINT | DEFAULT 0 | 关注者数 |
| hot_score | DECIMAL(15,2) | DEFAULT 0.0 | 热度分数 |
| created_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | DEFAULT NOW() | 更新时间 |

**唯一约束**：
- `(platform_id, external_topic_id)` - 平台内话题唯一

**索引**：
- `idx_topics_platform` - 平台索引
- `idx_topics_name` - 名称索引
- `idx_topics_hot_score` - 热度降序索引
- `idx_topics_follower` - 关注者降序索引

**触发器**：
- `update_topics_updated_at` - 自动更新 updated_at 字段

## 3. 快速开始

### 3.1 执行 Schema

**方式一：Supabase SQL 编辑器**

1. 打开 Supabase 项目控制台
2. 进入 SQL Editor
3. 复制 `schema.sql` 文件内容
4. 点击 Run 执行

**方式二：psql 命令行**

```bash
psql -h your-project.supabase.co -U postgres -d postgres -f schema.sql
```

**方式三：基础版本（无外键）**

如需快速测试或独立部署，可使用 `schema_basic.sql`：

```bash
psql -h your-project.supabase.co -U postgres -d postgres -f schema_basic.sql
```

### 3.2 测试数据插入

```sql
-- 插入平台数据（自动执行）
-- 查看平台
SELECT * FROM platforms;

-- 插入测试用户
INSERT INTO users (platform_id, external_user_id, username, display_name, follower_count) 
SELECT p.id, 'user_001', 'test_user', '测试用户', 1000
FROM platforms p WHERE p.platform_key = 'bilibili'
ON CONFLICT (platform_id, external_user_id) DO NOTHING;

-- 插入测试内容
INSERT INTO contents (platform_id, external_content_id, content_type, title, view_count, like_count)
SELECT p.id, 'video_001', 'video', '测试视频', 50000, 1000
FROM platforms p WHERE p.platform_key = 'bilibili'
ON CONFLICT (platform_id, external_content_id) DO NOTHING;

-- 插入测试话题
INSERT INTO topics (platform_id, external_topic_id, name, hot_score, content_count)
SELECT p.id, 'topic_001', '热门话题', 10000.00, 500
FROM platforms p WHERE p.platform_key = 'bilibili'
ON CONFLICT (platform_id, external_topic_id) DO NOTHING;
```

### 3.3 数据验证查询

```sql
-- 查看所有表
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' ORDER BY table_name;

-- 统计各表记录数
SELECT 'platforms' AS table_name, COUNT(*) AS count FROM platforms
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'contents', COUNT(*) FROM contents
UNION ALL SELECT 'comments', COUNT(*) FROM comments
UNION ALL SELECT 'relations', COUNT(*) FROM relations
UNION ALL SELECT 'topics', COUNT(*) FROM topics;
```

## 4. 示例查询

### 4.1 查询所有平台

```sql
SELECT 
    id,
    platform_key,
    platform_name,
    platform_url,
    is_active,
    created_at
FROM platforms
ORDER BY platform_name;
```

### 4.2 按类型查询内容

```sql
-- 查询所有视频
SELECT id, title, content_type, view_count, like_count, published_at
FROM contents
WHERE content_type = 'video'
ORDER BY published_at DESC
LIMIT 20;

-- 查询热门内容（播放数 > 10000）
SELECT id, title, view_count, like_count, comment_count
FROM contents
WHERE view_count > 10000
ORDER BY view_count DESC
LIMIT 50;
```

### 4.3 查询内容的评论

```sql
-- 查询指定内容的所有顶级评论
SELECT 
    c.id,
    c.content,
    c.like_count,
    c.is_top,
    c.created_at,
    u.display_name AS author_name,
    u.avatar_url
FROM comments c
LEFT JOIN users u ON c.author_id = u.id
WHERE c.content_id = '指定内容UUID'
  AND c.parent_id IS NULL
ORDER BY c.is_top DESC, c.like_count DESC, c.created_at DESC;

-- 查询评论的回复
SELECT 
    c.id,
    c.content,
    c.like_count,
    c.created_at,
    u.display_name AS author_name
FROM comments c
LEFT JOIN users u ON c.author_id = u.id
WHERE c.parent_id = '指定评论UUID'
ORDER BY c.created_at ASC;
```

### 4.4 探索实体关系

```sql
-- 查询用户的粉丝关系
SELECT 
    r.relation_type,
    r.weight,
    source.username AS source_username,
    source.display_name AS source_display_name,
    target.username AS target_username,
    target.display_name AS target_display_name
FROM relations r
JOIN users source ON r.source_entity_id = source.id
JOIN users target ON r.target_entity_id = target.id
WHERE r.source_entity_type = 'user'
  AND r.target_entity_type = 'user'
  AND r.relation_type = 'follows'
LIMIT 100;

-- 查询内容的话题标签
SELECT 
    c.title,
    c.content_type,
    c.view_count,
    c.likes_count,
    c.topics
FROM contents c
WHERE c.topics IS NOT NULL
  AND array_length(c.topics, 1) > 0
ORDER BY c.view_count DESC
LIMIT 20;

-- 查询话题下的内容
SELECT 
    c.title,
    c.content_type,
    c.view_count,
    c.like_count,
    c.published_at
FROM contents c
WHERE '指定话题' = ANY(c.topics)
ORDER BY c.published_at DESC
LIMIT 50;
```

## 5. 视图

### 5.1 用户关系视图 (user_relations_view)

```sql
SELECT * FROM user_relations_view;
```

展示用户之间的关注、粉丝等关系，包含源用户和目标用户的详细信息。

### 5.2 内容关系视图 (content_relations_view)

```sql
SELECT * FROM content_relations_view;
```

展示内容详情及作者信息，方便内容检索和展示。

### 5.3 热门内容视图 (popular_contents_view)

```sql
SELECT * FROM popular_contents_view;
```

展示按播放数排序的前 1000 条热门内容，包含平台信息。

## 6. 存储过程

### 6.1 添加用户

```sql
CALL add_user(
    'bilibili',          -- 平台标识
    'external_user_id',  -- 外部用户 ID
    'username',          -- 用户名
    'display_name'       -- 显示名称
);
```

### 6.2 添加内容

```sql
CALL add_content(
    'bilibili',          -- 平台标识
    'external_content_id', -- 外部内容 ID
    'video',             -- 内容类型
    '视频标题',          -- 标题
    '视频描述'           -- 描述
);
```

### 6.3 添加关注关系

```sql
CALL add_follow_relation(
    'bilibili',          -- 平台标识
    'follower_external_id',   -- 粉丝外部 ID
    'following_external_id'   -- 关注对象外部 ID
);
```

## 7. 枚举类型

| 枚举名称 | 值 |
|----------|------|
| platform_type | 'bilibili', 'toutiao', 'other' |
| user_status | 'active', 'inactive', 'banned', 'verified' |
| content_type | 'video', 'article', 'dynamic', 'comment', 'live', 'short_video', '问答', '专栏', '图集' |
| relation_type | 'follows', 'fans', 'likes', 'collects', 'shares', 'comments', 'replies', 'mentions', 'collaborates', 'participates', 'creates', 'tags', 'categorizes', 'features', 'similar_to', 'derived_from', 'topic_of', 'location_of', 'language_of', 'awards', 'promotes', 'disputes', 'related' |

## 8. 文件说明

| 文件 | 说明 |
|------|------|
| `schema.sql` | 完整 Schema，包含所有表、视图、触发器和存储过程 |
| `schema_basic.sql` | 基础 Schema，无外键约束，可独立执行 |
| `README.md` | 本文档 |
