-- -*- coding: utf-8 -*-
/**
 * 知识图谱数据库 Schema
 * Knowledge Graph Database Schema
 * 
 * 支持哔哩哔哩和今日头条数据存储
 * Designed for Bilibili and Toutiao data storage
 * 
 * 版本: 1.0.0
 * 日期: 2026-01-19
 */

-- ============================================
-- 1. 基础配置
-- ============================================

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- 2. 平台配置表
-- ============================================

-- 平台类型枚举
DO $$ BEGIN
    CREATE TYPE platform_type AS ENUM ('bilibili', 'toutiao', 'other');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 用户状态枚举
DO $$ BEGIN
    CREATE TYPE user_status AS ENUM ('active', 'inactive', 'banned', 'verified');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 内容类型枚举
DO $$ BEGIN
    CREATE TYPE content_type AS ENUM ('video', 'article', 'dynamic', 'comment', 'live', 'short_video', '问答', '专栏', '图集');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 关系类型枚举
DO $$ BEGIN
    CREATE TYPE relation_type AS ENUM (
        'follows',           -- 关注
        'fans',              -- 粉丝
        'likes',             -- 点赞
        'collects',          -- 收藏
        'shares',            -- 分享
        'comments',          -- 评论
        'replies',           -- 回复
        'mentions',          -- 提及
        'collaborates',      -- 合作
        'participates',      -- 参与
        'creates',           -- 创建
        'tags',              -- 标签
        'categorizes',       -- 分类
        'features',          -- 特性
        'similar_to',        -- 相似
        'derived_from',      -- 衍生
        'topic_of',          -- 话题
        'location_of',       -- 位置
        'language_of',       -- 语言
        'awards',            -- 获奖
        'promotes',          -- 推荐
        'disputes',          -- 争议
        'related'            -- 相关
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- 3. 平台账号表
-- ============================================

-- 平台信息表
CREATE TABLE IF NOT EXISTS platforms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_key VARCHAR(50) UNIQUE NOT NULL,  -- bilibili, toutiao
    platform_name VARCHAR(100) NOT NULL,
    platform_url VARCHAR(255),
    api_base_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入默认平台
INSERT INTO platforms (platform_key, platform_name, platform_url, api_base_url) VALUES
('bilibili', '哔哩哔哩', 'https://www.bilibili.com', 'https://api.bilibili.com'),
('toutiao', '今日头条', 'https://www.toutiao.com', 'https://www.toutiao.com/api')
ON CONFLICT (platform_key) DO NOTHING;

-- ============================================
-- 4. 用户实体表
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    external_user_id VARCHAR(100) NOT NULL,
    
    -- 用户资料
    username VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    gender VARCHAR(20),  -- male, female, unknown
    birthday DATE,
    location VARCHAR(255),
    
    -- 认证信息
    is_verified BOOLEAN DEFAULT FALSE,
    verification_type VARCHAR(50),
    
    -- 统计数据
    follower_count BIGINT DEFAULT 0,
    following_count BIGINT DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    article_count INTEGER DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    play_count BIGINT DEFAULT 0,
    read_count BIGINT DEFAULT 0,
    
    -- 状态
    status user_status DEFAULT 'active',
    last_active_at TIMESTAMP WITH TIME ZONE,
    
    -- 其他信息
    profile_url VARCHAR(500),
    level INTEGER DEFAULT 0,
    experience BIGINT DEFAULT 0,
    coins BIGINT DEFAULT 0,
    tags TEXT[],  -- 用户标签
    interests TEXT[],  -- 兴趣标签
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 唯一约束
    UNIQUE(platform_id, external_user_id)
);

-- 用户索引
CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform_id);
CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_follower_count ON users(follower_count DESC);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- 用户全文搜索
CREATE INDEX IF NOT EXISTS idx_users_search ON users USING gin(
    (COALESCE(username, '') || ' ' || COALESCE(display_name, '') || ' ' || COALESCE(bio, '')) gin_trgm_ops
);

-- ============================================
-- 5. 内容实体表
-- ============================================

CREATE TABLE IF NOT EXISTS contents (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    external_content_id VARCHAR(100) NOT NULL,
    
    -- 内容类型
    content_type content_type NOT NULL,
    
    -- 作者
    author_id UUID REFERENCES users(id),
    
    -- 内容详情
    title VARCHAR(500),
    description TEXT,
    content_text TEXT,  -- 原始内容文本
    content_html TEXT,  -- HTML格式内容
    
    -- 媒体信息
    cover_url VARCHAR(500),
    thumbnail_urls TEXT[],  -- 缩略图列表
    video_url VARCHAR(500),
    duration INTEGER,  -- 视频时长(秒)
    
    -- 统计数据
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    dislike_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    share_count BIGINT DEFAULT 0,
    collect_count BIGINT DEFAULT 0,
    coin_count BIGINT DEFAULT 0,
    danmaku_count BIGINT DEFAULT 0,  -- 弹幕数
    score DECIMAL(3,2) DEFAULT 0.0,  -- 评分
    
    -- 分类和标签
    category_id VARCHAR(100),
    category_name VARCHAR(100),
    tags TEXT[],
    topics TEXT[],  -- 话题标签
    
    -- 位置信息
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    location_name VARCHAR(255),
    
    -- 时间信息
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 状态
    is_deleted BOOLEAN DEFAULT FALSE,
    is_top BOOLEAN DEFAULT FALSE,  -- 是否置顶
    is_featured BOOLEAN DEFAULT FALSE,  -- 是否推荐
    
    -- 原始数据
    raw_data JSONB DEFAULT '{}',
    
    -- 唯一约束
    UNIQUE(platform_id, external_content_id)
);

-- 内容索引
CREATE INDEX IF NOT EXISTS idx_contents_platform ON contents(platform_id);
CREATE INDEX IF NOT EXISTS idx_contents_type ON contents(content_type);
CREATE INDEX IF NOT EXISTS idx_contents_author ON contents(author_id);
CREATE INDEX IF NOT EXISTS idx_contents_published ON contents(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_view_count ON contents(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_contents_like_count ON contents(like_count DESC);
CREATE INDEX IF NOT EXISTS idx_contents_tags ON contents USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_contents_topics ON contents USING gin(topics);

-- ============================================
-- 6. 评论实体表
-- ============================================

CREATE TABLE IF NOT EXISTS comments (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    external_comment_id VARCHAR(100) NOT NULL,
    
    -- 关联内容
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    
    -- 父评论（回复）
    parent_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    root_id UUID REFERENCES comments(id) ON DELETE CASCADE,
    
    -- 评论者
    author_id UUID REFERENCES users(id),
    
    -- 评论内容
    content TEXT NOT NULL,
    
    -- 统计数据
    like_count BIGINT DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    
    -- 置顶/精选
    is_top BOOLEAN DEFAULT FALSE,
    is_selected BOOLEAN DEFAULT FALSE,  -- 是否精选
    
    -- 时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 原始数据
    raw_data JSONB DEFAULT '{}',
    
    -- 唯一约束
    UNIQUE(platform_id, external_comment_id)
);

-- 评论索引
CREATE INDEX IF NOT EXISTS idx_comments_content ON comments(content_id);
CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_id);
CREATE INDEX IF NOT EXISTS idx_comments_parent ON comments(parent_id);
CREATE INDEX IF NOT EXISTS idx_comments_root ON comments(root_id);
CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_at DESC);

-- ============================================
-- 7. 关系表（知识图谱核心）
-- ============================================

CREATE TABLE IF NOT EXISTS relations (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    
    -- 关系类型
    relation_type relation_type NOT NULL,
    
    -- 源实体
    source_entity_type VARCHAR(50) NOT NULL,  -- user, content, comment, etc.
    source_entity_id UUID NOT NULL,
    
    -- 目标实体
    target_entity_type VARCHAR(50) NOT NULL,
    target_entity_id UUID NOT NULL,
    
    -- 关系属性
    weight DECIMAL(5,4) DEFAULT 1.0,  -- 关系权重
    metadata JSONB DEFAULT '{}',
    
    -- 时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,  -- 关系过期时间
    
    -- 唯一约束
    UNIQUE(platform_id, relation_type, source_entity_id, target_entity_id)
);

-- 关系索引
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity_type, source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity_type, target_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_platform ON relations(platform_id);

-- ============================================
-- 8. 话题/标签表
-- ============================================

CREATE TABLE IF NOT EXISTS topics (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    external_topic_id VARCHAR(100) NOT NULL,
    
    -- 话题详情
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_url VARCHAR(500),
    profile_url VARCHAR(500),
    
    -- 统计
    content_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    follower_count BIGINT DEFAULT 0,
    
    -- 热度
    hot_score DECIMAL(15,2) DEFAULT 0.0,
    
    -- 时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 唯一约束
    UNIQUE(platform_id, external_topic_id)
);

-- 话题索引
CREATE INDEX IF NOT EXISTS idx_topics_platform ON topics(platform_id);
CREATE INDEX IF NOT EXISTS idx_topics_name ON topics(name);
CREATE INDEX IF NOT EXISTS idx_topics_hot_score ON topics(hot_score DESC);
CREATE INDEX IF NOT EXISTS idx_topics_follower ON topics(follower_count DESC);

-- ============================================
-- 9. 分类表
-- ============================================

CREATE TABLE IF NOT EXISTS categories (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    external_category_id VARCHAR(100) NOT NULL,
    
    -- 分类详情
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    icon_url VARCHAR(500),
    description TEXT,
    
    -- 层级
    level INTEGER DEFAULT 1,
    path TEXT[],  -- 分类路径
    
    -- 统计
    content_count BIGINT DEFAULT 0,
    
    -- 排序
    sort_order INTEGER DEFAULT 0,
    
    -- 时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 唯一约束
    UNIQUE(platform_id, external_category_id)
);

-- ============================================
-- 10. Cookie/会话管理表
-- ============================================

CREATE TABLE IF NOT EXISTS sessions (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    session_name VARCHAR(100) NOT NULL,
    
    -- 会话数据
    cookies JSONB NOT NULL,
    user_agent VARCHAR(500),
    local_storage JSONB DEFAULT '{}',
    session_storage JSONB DEFAULT '{}',
    
    -- 状态
    is_valid BOOLEAN DEFAULT TRUE,
    last_validated_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    -- 绑定用户（可选）
    bound_user_id UUID REFERENCES users(id),
    
    -- 过期时间
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- 时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 唯一约束
    UNIQUE(platform_id, session_name)
);

-- 会话索引
CREATE INDEX IF NOT EXISTS idx_sessions_platform ON sessions(platform_id);
CREATE INDEX IF NOT EXISTS idx_sessions_valid ON sessions(is_valid);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);

-- ============================================
-- 11. 采集任务表
-- ============================================

CREATE TABLE IF NOT EXISTS crawl_tasks (
    -- 基础信息
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID REFERENCES platforms(id),
    task_type VARCHAR(50) NOT NULL,  -- user_contents, user_followers, topic_contents, etc.
    
    -- 任务目标
    target_type VARCHAR(50) NOT NULL,  -- user, content, topic
    target_id VARCHAR(100) NOT NULL,
    target_name VARCHAR(255),
    
    -- 任务配置
    config JSONB DEFAULT '{}',
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed, paused
    progress DECIMAL(5,2) DEFAULT 0.0,  -- 进度百分比
    
    -- 统计
    total_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    
    -- 错误信息
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- 时间
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 12. 知识图谱视图
-- ============================================

-- 用户关系视图
CREATE OR REPLACE VIEW user_relations_view AS
SELECT 
    r.id,
    r.relation_type,
    r.weight,
    r.created_at,
    source_user.id AS source_user_id,
    source_user.username AS source_username,
    source_user.display_name AS source_display_name,
    target_user.id AS target_user_id,
    target_user.username AS target_username,
    target_user.display_name AS target_display_name
FROM relations r
JOIN users source_user ON r.source_entity_id = source_user.id
JOIN users target_user ON r.target_entity_id = target_user.id
WHERE r.source_entity_type = 'user' AND r.target_entity_type = 'user';

-- 内容关系视图
CREATE OR REPLACE VIEW content_relations_view AS
SELECT 
    c.id,
    c.content_type,
    c.title,
    c.view_count,
    c.like_count,
    c.comment_count,
    c.published_at,
    u.id AS author_id,
    u.username AS author_username,
    u.display_name AS author_display_name,
    c.tags,
    c.topics
FROM contents c
LEFT JOIN users u ON c.author_id = u.id;

-- 热门内容视图
CREATE OR REPLACE VIEW popular_contents_view AS
SELECT 
    c.id,
    c.platform_id,
    c.external_content_id,
    c.content_type,
    c.title,
    c.description,
    c.cover_url,
    c.view_count,
    c.like_count,
    c.comment_count,
    c.share_count,
    c.published_at,
    c.tags,
    c.topics,
    p.platform_key,
    p.platform_name
FROM contents c
JOIN platforms p ON c.platform_id = p.id
WHERE c.is_deleted = FALSE
ORDER BY c.view_count DESC
LIMIT 1000;

-- ============================================
-- 13. 触发器函数
-- ============================================

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 应用更新时间触发器
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at()
        ', t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 14. 存储过程
-- ============================================

-- 添加用户
CREATE OR REPLACE PROCEDURE add_user(
    p_platform_key VARCHAR,
    p_external_user_id VARCHAR,
    p_username VARCHAR,
    p_display_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_platform_id UUID;
BEGIN
    SELECT id INTO v_platform_id FROM platforms WHERE platform_key = p_platform_key;
    
    INSERT INTO users (platform_id, external_user_id, username, display_name)
    VALUES (v_platform_id, p_external_user_id, p_username, p_display_name)
    ON CONFLICT (platform_id, external_user_id) DO UPDATE
    SET 
        username = EXCLUDED.username,
        display_name = EXCLUDED.display_name,
        updated_at = NOW();
END;
$$;

-- 添加内容
CREATE OR REPLACE PROCEDURE add_content(
    p_platform_key VARCHAR,
    p_external_content_id VARCHAR,
    p_content_type content_type,
    p_title VARCHAR,
    p_description TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_platform_id UUID;
BEGIN
    SELECT id INTO v_platform_id FROM platforms WHERE platform_key = p_platform_key;
    
    INSERT INTO contents (platform_id, external_content_id, content_type, title, description)
    VALUES (v_platform_id, p_external_content_id, p_content_type, p_title, p_description)
    ON CONFLICT (platform_id, external_content_id) DO UPDATE
    SET 
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        updated_at = NOW();
END;
$$;

-- 添加关注关系
CREATE OR REPLACE PROCEDURE add_follow_relation(
    p_platform_key VARCHAR,
    p_follower_external_id VARCHAR,
    p_following_external_id VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_platform_id UUID;
    v_follower_id UUID;
    v_following_id UUID;
BEGIN
    SELECT id INTO v_platform_id FROM platforms WHERE platform_key = p_platform_key;
    
    SELECT id INTO v_follower_id FROM users 
    WHERE platform_id = v_platform_id AND external_user_id = p_follower_external_id;
    
    SELECT id INTO v_following_id FROM users 
    WHERE platform_id = v_platform_id AND external_user_id = p_following_external_id;
    
    IF v_follower_id IS NOT NULL AND v_following_id IS NOT NULL THEN
        INSERT INTO relations (platform_id, relation_type, source_entity_type, source_entity_id, 
                               target_entity_type, target_entity_id)
        VALUES (v_platform_id, 'follows', 'user', v_follower_id, 'user', v_following_id)
        ON CONFLICT (platform_id, relation_type, source_entity_id, target_entity_id) DO NOTHING;
    END IF;
END;
$$;

-- ============================================
-- 15. 权限设置
-- ============================================

-- 授予基本权限（根据实际需要调整）
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_user;
