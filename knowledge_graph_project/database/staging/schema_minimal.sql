-- -*- coding: utf-8 -*-
/**
 * 知识图谱数据库 - 最小化Schema (修复版)
 * Knowledge Graph Database - Minimal Schema (Fixed)
 * 
 * 核心表结构：用户、内容、评论、关系、话题、分类
 * 无外键约束，可独立执行
 * 
 * 版本: 1.0.1 (修复版)
 * 日期: 2026-01-20
 * 修复内容: 移除所有外键约束，简化触发器逻辑
 */

-- ============================================
-- 1. 扩展
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 2. 枚举类型
-- ============================================

-- 平台类型
DO $$ BEGIN
    CREATE TYPE platform_type AS ENUM ('bilibili', 'toutiao', 'other');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- 用户状态
DO $$ BEGIN
    CREATE TYPE user_status AS ENUM ('active', 'inactive', 'banned', 'verified');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- 内容类型
DO $$ BEGIN
    CREATE TYPE content_type AS ENUM ('video', 'article', 'dynamic', 'comment', 'live', 'short_video', '问答', '专栏', '图集');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- 关系类型
DO $$ BEGIN
    CREATE TYPE relation_type AS ENUM ('follows', 'fans', 'likes', 'collects', 'shares', 'comments', 'replies', 'mentions', 'collaborates', 'participates', 'creates', 'tags', 'categorizes', 'features', 'similar_to', 'derived_from', 'topic_of', 'location_of', 'language_of', 'awards', 'promotes', 'disputes', 'related');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- 3. 平台配置表
-- ============================================

CREATE TABLE IF NOT EXISTS platforms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_key VARCHAR(50) UNIQUE NOT NULL,
    platform_name VARCHAR(100) NOT NULL,
    platform_url VARCHAR(255),
    api_base_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
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
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    external_user_id VARCHAR(100) NOT NULL,
    username VARCHAR(255),
    display_name VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    gender VARCHAR(20),
    birthday DATE,
    location VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_type VARCHAR(50),
    follower_count BIGINT DEFAULT 0,
    following_count BIGINT DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    article_count INTEGER DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    play_count BIGINT DEFAULT 0,
    read_count BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    last_active_at TIMESTAMPTZ,
    profile_url VARCHAR(500),
    level INTEGER DEFAULT 0,
    experience BIGINT DEFAULT 0,
    coins BIGINT DEFAULT 0,
    tags TEXT[],
    interests TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 用户索引
CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform_id);
CREATE INDEX IF NOT EXISTS idx_users_external_id ON users(external_user_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- ============================================
-- 5. 内容实体表
-- ============================================

CREATE TABLE IF NOT EXISTS contents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    external_content_id VARCHAR(100) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    author_id UUID,
    title VARCHAR(500),
    description TEXT,
    content_text TEXT,
    content_html TEXT,
    cover_url VARCHAR(500),
    thumbnail_urls TEXT[],
    video_url VARCHAR(500),
    duration INTEGER,
    view_count BIGINT DEFAULT 0,
    like_count BIGINT DEFAULT 0,
    dislike_count BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    share_count BIGINT DEFAULT 0,
    collect_count BIGINT DEFAULT 0,
    coin_count BIGINT DEFAULT 0,
    danmaku_count BIGINT DEFAULT 0,
    score DECIMAL(3,2) DEFAULT 0.0,
    category_id VARCHAR(100),
    category_name VARCHAR(100),
    tags TEXT[],
    topics TEXT[],
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    location_name VARCHAR(255),
    published_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_top BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    raw_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 内容索引
CREATE INDEX IF NOT EXISTS idx_contents_platform ON contents(platform_id);
CREATE INDEX IF NOT EXISTS idx_contents_type ON contents(content_type);
CREATE INDEX IF NOT EXISTS idx_contents_author ON contents(author_id);
CREATE INDEX IF NOT EXISTS idx_contents_published ON contents(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_contents_view_count ON contents(view_count DESC);
CREATE INDEX IF NOT EXISTS idx_contents_tags ON contents USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_contents_topics ON contents USING gin(topics);

-- ============================================
-- 6. 评论实体表
-- ============================================

CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    external_comment_id VARCHAR(100) NOT NULL,
    content_id UUID,
    parent_id UUID,
    root_id UUID,
    author_id UUID,
    content TEXT NOT NULL,
    like_count BIGINT DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    is_top BOOLEAN DEFAULT FALSE,
    is_selected BOOLEAN DEFAULT FALSE,
    raw_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 评论索引
CREATE INDEX IF NOT EXISTS idx_comments_content ON comments(content_id);
CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author_id);
CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_at DESC);

-- ============================================
-- 7. 关系表（知识图谱核心）
-- ============================================

CREATE TABLE IF NOT EXISTS relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    relation_type VARCHAR(50) NOT NULL,
    source_entity_type VARCHAR(50) NOT NULL,
    source_entity_id UUID NOT NULL,
    target_entity_type VARCHAR(50) NOT NULL,
    target_entity_id UUID NOT NULL,
    weight DECIMAL(5,4) DEFAULT 1.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- 关系索引
CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_entity_type, source_entity_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_entity_type, target_entity_id);

-- ============================================
-- 8. 话题/标签表
-- ============================================

CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    external_topic_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cover_url VARCHAR(500),
    profile_url VARCHAR(500),
    content_count BIGINT DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    follower_count BIGINT DEFAULT 0,
    hot_score DECIMAL(15,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 话题索引
CREATE INDEX IF NOT EXISTS idx_topics_name ON topics(name);
CREATE INDEX IF NOT EXISTS idx_topics_hot_score ON topics(hot_score DESC);

-- ============================================
-- 9. 分类表
-- ============================================

CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    external_category_id VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_id UUID,
    icon_url VARCHAR(500),
    description TEXT,
    level INTEGER DEFAULT 1,
    path TEXT[],
    content_count BIGINT DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 分类索引
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_level ON categories(level);

-- ============================================
-- 10. 会话管理表
-- ============================================

CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_id UUID,
    session_name VARCHAR(100) NOT NULL,
    cookies JSONB NOT NULL,
    user_agent VARCHAR(500),
    is_valid BOOLEAN DEFAULT TRUE,
    last_validated_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    bound_user_id UUID,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 会话索引
CREATE INDEX IF NOT EXISTS idx_sessions_platform ON sessions(platform_id);
CREATE INDEX IF NOT EXISTS idx_sessions_valid ON sessions(is_valid);

-- ============================================
-- 11. 更新时间触发器函数
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 12. 为每个表单独创建触发器
-- ============================================

-- platforms表的触发器
DROP TRIGGER IF EXISTS update_platforms_updated_at ON platforms;
CREATE TRIGGER update_platforms_updated_at
    BEFORE UPDATE ON platforms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- users表的触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- contents表的触发器
DROP TRIGGER IF EXISTS update_contents_updated_at ON contents;
CREATE TRIGGER update_contents_updated_at
    BEFORE UPDATE ON contents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- comments表的触发器
DROP TRIGGER IF EXISTS update_comments_updated_at ON comments;
CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- topics表的触发器
DROP TRIGGER IF EXISTS update_topics_updated_at ON topics;
CREATE TRIGGER update_topics_updated_at
    BEFORE UPDATE ON topics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- categories表的触发器
DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- sessions表的触发器
DROP TRIGGER IF EXISTS update_sessions_updated_at ON sessions;
CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- ============================================
-- 13. 验证查询
-- ============================================

-- 查看所有表
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' ORDER BY table_name;

-- 查看平台数据
-- SELECT * FROM platforms;

-- 插入测试数据
-- INSERT INTO users (username, display_name) VALUES ('test', '测试用户');
-- INSERT INTO contents (title, content_type) VALUES ('测试内容', 'video');
