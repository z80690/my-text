-- -*- coding: utf-8 -*-
/**
 * 知识图谱数据库 - 极简Schema v1
 * Knowledge Graph Database - Minimal Schema v1
 * 
 * 初始版本：仅包含platforms和contents表，无外键约束
 * 后续将通过ALTER TABLE添加关系和外键
 * 
 * 版本: 1.0.0
 * 日期: 2026-01-20
 */

-- ============================================
-- 1. 平台配置表 (platforms)
-- ============================================

CREATE TABLE IF NOT EXISTS platforms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入默认平台
INSERT INTO platforms (name) VALUES
('bilibili'),
('toutiao')
ON CONFLICT DO NOTHING;

-- 平台索引
CREATE INDEX IF NOT EXISTS idx_platforms_name ON platforms(name);

-- ============================================
-- 2. 内容表 (contents)
-- ============================================

CREATE TABLE IF NOT EXISTS contents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500),
    content_type VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 内容索引
CREATE INDEX IF NOT EXISTS idx_contents_type ON contents(content_type);
CREATE INDEX IF NOT EXISTS idx_contents_created ON contents(created_at DESC);

-- ============================================
-- 3. 基础数据验证查询
-- ============================================

-- 查看平台
SELECT * FROM platforms;

-- 查看内容
SELECT * FROM contents;
