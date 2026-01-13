-- 用户资料表架构设计
-- 扩展 Supabase Auth users 表，存储应用程序特定的用户信息
-- 在 Supabase SQL Editor 中执行此脚本

-- ========================================
-- 1. 创建用户资料表
-- ========================================

CREATE TABLE IF NOT EXISTS public.user_profiles (
    -- 主键：引用 auth.users 表的 ID
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,

    -- 基本信息
    display_name TEXT NOT NULL DEFAULT '',           -- 显示名称
    avatar_url TEXT,                                -- 头像 URL
    bio TEXT,                                       -- 个人简介

    -- 联系信息
    phone TEXT,                                     -- 电话号码（可选）
    website TEXT,                                   -- 个人网站 URL（可选）

    -- 用户偏好设置（JSON 格式，灵活扩展）
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- 统计信息
    stats JSONB NOT NULL DEFAULT '{}'::jsonb,        -- 用户统计数据（如登录次数等）

    -- 状态信息
    is_active BOOLEAN NOT NULL DEFAULT true,         -- 账户是否激活
    last_login_at TIMESTAMPTZ,                      -- 最后登录时间

    -- 元数据
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,     -- 其他元数据

    -- 时间戳
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ========================================
-- 2. 创建索引
-- ========================================

-- 为显示名称创建索引（用于搜索）
CREATE INDEX IF NOT EXISTS idx_user_profiles_display_name
    ON public.user_profiles(display_name);

-- 为活跃用户创建索引
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_active
    ON public.user_profiles(is_active)
    WHERE is_active = true;

-- 为创建时间创建索引（用于排序）
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at
    ON public.user_profiles(created_at DESC);

-- 为更新时间创建索引
CREATE INDEX IF NOT EXISTS idx_user_profiles_updated_at
    ON public.user_profiles(updated_at DESC);

-- ========================================
-- 3. 创建触发器函数（自动更新 updated_at）
-- ========================================

CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 4. 创建触发器
-- ========================================

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- ========================================
-- 5. 创建自动创建用户资料的函数
-- ========================================

-- 当新用户注册时，自动创建对应的用户资料
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, display_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'display_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- 6. 创建触发器（新用户自动创建资料）
-- ========================================

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- ========================================
-- 7. 启用行级安全（RLS）
-- ========================================

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- ========================================
-- 8. 创建 RLS 策略
-- ========================================

-- 策略 1: 用户可以查看自己的资料
CREATE POLICY "Users can view own profile"
    ON public.user_profiles
    FOR SELECT
    USING (auth.uid() = id);

-- 策略 2: 用户可以更新自己的资料
CREATE POLICY "Users can update own profile"
    ON public.user_profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- 策略 3: 用户可以删除自己的资料（级联删除用户时）
CREATE POLICY "Users can delete own profile"
    ON public.user_profiles
    FOR DELETE
    USING (auth.uid() = id);

-- 策略 4: 用户可以插入自己的资料（通过触发器自动创建）
CREATE POLICY "Users can insert own profile"
    ON public.user_profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ========================================
-- 9. 创建辅助函数
-- ========================================

-- 函数：获取用户完整资料（包括 auth.users 信息）
CREATE OR REPLACE FUNCTION public.get_user_profile(user_id UUID)
RETURNS TABLE (
    id UUID,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    bio TEXT,
    preferences JSONB,
    stats JSONB,
    is_active BOOLEAN,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        up.id,
        u.email,
        up.display_name,
        up.avatar_url,
        up.bio,
        up.preferences,
        up.stats,
        up.is_active,
        up.last_login_at,
        up.created_at,
        up.updated_at
    FROM public.user_profiles up
    JOIN auth.users u ON up.id = u.id
    WHERE up.id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 函数：更新用户最后登录时间
CREATE OR REPLACE FUNCTION public.update_last_login(user_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.user_profiles
    SET last_login_at = NOW(),
        stats = jsonb_set(
            stats,
            '{login_count}',
            COALESCE((stats->>'login_count')::int, 0) + 1
        )
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- 10. 创建视图（可选）
-- ========================================

-- 视图：用户概览（用于管理后台）
CREATE OR REPLACE VIEW public.user_overview AS
SELECT
    u.id,
    u.email,
    up.display_name,
    up.is_active,
    u.email_confirmed_at,
    up.last_login_at,
    up.created_at,
    up.updated_at,
    CASE
        WHEN up.last_login_at IS NULL THEN '从未登录'
        WHEN NOW() - up.last_login_at < INTERVAL '7 days' THEN '活跃'
        WHEN NOW() - up.last_login_at < INTERVAL '30 days' THEN '近期活跃'
        ELSE '不活跃'
    END as activity_status
FROM auth.users u
LEFT JOIN public.user_profiles up ON u.id = up.id;

-- ========================================
-- 11. 添加注释
-- ========================================

COMMENT ON TABLE public.user_profiles IS '用户资料表，扩展 Supabase Auth 用户信息';

COMMENT ON COLUMN public.user_profiles.id IS '用户 ID，引用 auth.users.id';

COMMENT ON COLUMN public.user_profiles.display_name IS '用户显示名称';

COMMENT ON COLUMN public.user_profiles.avatar_url IS '头像图片 URL';

COMMENT ON COLUMN public.user_profiles.bio IS '用户个人简介';

COMMENT ON COLUMN public.user_profiles.preferences IS '用户偏好设置（JSON 格式）：{theme: "dark", language: "zh-CN", notifications: true}';

COMMENT ON COLUMN public.user_profiles.stats IS '用户统计数据（JSON 格式）：{login_count: 10, posts_count: 5}';

COMMENT ON COLUMN public.user_profiles.is_active IS '账户是否激活';

COMMENT ON COLUMN public.user_profiles.last_login_at IS '最后登录时间';

COMMENT ON COLUMN public.user_profiles.metadata IS '其他元数据';

COMMENT ON FUNCTION public.get_user_profile(UUID) IS '获取用户完整资料（包括 email）';

COMMENT ON FUNCTION public.update_last_login(UUID) IS '更新用户最后登录时间和登录次数';

-- ========================================
-- 12. 输出创建结果
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '用户资料表创建成功';
    RAISE NOTICE '========================================';
    RAISE NOTICE '表名: public.user_profiles';
    RAISE NOTICE '字段数: 12';
    RAISE NOTICE 'RLS: 已启用';
    RAISE NOTICE '策略数: 4';
    RAISE NOTICE '索引数: 4';
    RAISE NOTICE '========================================';
    RAISE NOTICE '触发器: 已配置自动创建用户资料';
    RAISE NOTICE '辅助函数: get_user_profile(), update_last_login()';
    RAISE NOTICE '视图: user_overview (用户概览)';
    RAISE NOTICE '========================================';
END $$;
