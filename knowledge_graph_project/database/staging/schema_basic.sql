-- -*- coding: utf-8 -*-
/**
 * 知识图谱数据库 - 基础Schema
 * Knowledge Graph Database - Basic Schema
 * 
 * 包含核心表：platforms, users, contents, comments
 * 无外键约束，可独立执行
 * 
 * 版本: 1.0.0
 * 日期: 2026-01-20
 */

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. 平台表 (platforms)
-- ============================================

CREATE TABLE IF NOT EXISTS platforms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入默认平台数据
INSERT INTO platforms (name) VALUES
    ('bilibili'),
    ('toutiao')
ON CONFLICT (name) DO NOTHING;

-- 索引
CREATE INDEX IF NOT EXISTS idx_platforms_name ON platforms(name);

-- ============================================
-- 2. 用户表 (users)
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID,
    external_user_id VARCHAR(100),
    username VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    gender VARCHAR(20),
    location VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    follower_count BIGINT DEFAULT 0,
    following_count BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform_id);
CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_created ON users(created_at DESC);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();

-- ============================================
-- 3. 内容表 (contents)
-- ============================================

CREATE TABLE IF NOT EXISTS contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID,
    external_content_id VARCHAR(100),
    content_type VARCHAR(50),
    author_id UUID,
    title VARCHAR(500),
    description TEXT,
    content_text TEXT,
    cover_url VARCHAR(500),
    thumbnail_urls TEXT[],
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    share_count BIGINT DEFAULT 0,
    collect_count BIGINT DEFAULT 0,
    category_id VARCHAR(100),
    category_name VARCHAR(100),
    tags TEXT[],
    topics TEXT[],
    published_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_top BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    raw_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_contents_platform ON contents(platform_id);
CREATE INDEX IF NOT EXISTS idx_contents_type ON contents(content_type);
CREATE INDEX IF NOT EXISTS idx_contents_author ON contents(author_id);
CREATE INDEX IF NOT EXISTS idx_contents_published ON contents(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_view_count ON contents(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_contents_tags ON contents USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_contents_created ON contents(created_at DESC);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_contents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_contents_updated_at
    BEFORE UPDATE ON contents
    FOR EACH ROW
    EXECUTE FUNCTION update_contents_updated_at();

-- ============================================
-- 4. 评论表 (comments)
-- ============================================

CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID,
    external_comment_id VARCHAR(100),
    content_id UUID,
    parent_id UUID,
    root_id UUID,
    author_id UUID,
    content TEXT,
    like_count BIGINT DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    is_top BOOLEAN DEFAULT FALSE,
    is_selected BOOLEAN DEFAULT FALSE,
    raw_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_comments_content ON comments(content_id);
CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_id);
CREATE INDEX IF NOT EXISTS idx_comments_parent ON comments(parent_id);
CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_at DESC);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_comments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_comments_updated_at();

-- ============================================
-- 5. 关系表 (relations) - 知识图谱核心
-- ============================================

CREATE TABLE IF NOT EXISTS relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID,
    relation_type VARCHAR(50),
    source_entity_type VARCHAR(50),
    source_entity_id UUID,
    target_entity_type VARCHAR(50),
    target_entity_id UUID,
    weight DECIMAL(5,4) DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity_type, source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity_type, target_entity_id);

-- ============================================
-- 6. 话题表 (topics)
-- ============================================

CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID,
    external_topic_id VARCHAR(100),
    name VARCHAR(255),
    description TEXT,
    cover_url VARCHAR(500),
    content_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    follower_count BIGINT DEFAULT 0,
    hot_score DECIMAL(15,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_topics_name ON topics(name);
CREATE INDEX IF NOT EXISTS idx_topics_hot ON topics(hot_score DESC);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_topics_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_topics_updated_at
    BEFORE UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_topics_updated_at();

-- ============================================
-- 验证查询
-- ============================================

-- 查看所有表
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' ORDER BY table_name;

-- 查看平台数据
-- SELECT * FROM platforms;
