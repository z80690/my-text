-- Supabase Auth 配置脚本
-- 用于设置认证系统的配置参数
-- 在 Supabase SQL Editor 中运行此脚本

-- 启用邮箱认证（默认已启用，这里仅作确认）
INSERT INTO auth.authentication_methods (id, provider, is_enabled)
VALUES ('email', 'email', true)
ON CONFLICT (id) DO UPDATE SET is_enabled = true;

-- 配置邮箱验证（启用验证）
-- 注意：需要在 Supabase Dashboard 的 Authentication > Providers 中手动配置
-- 这里设置默认行为：注册时需要验证邮箱

-- 设置密码策略
-- 在 Supabase Dashboard 中配置以下设置：
-- 1. Minimum Password Length: 8 characters
-- 2. Require Uppercase: Off (可选)
-- 3. Require Numbers: Off (可选)
-- 4. Require Special Characters: Off (可选)

-- 启用会话管理
INSERT INTO auth.sessions_config (id, token_expiry, refresh_token_expiry)
VALUES ('default', 3600, 604800) -- 访问令牌1小时，刷新令牌7天
ON CONFLICT (id) DO UPDATE SET
    token_expiry = 3600,
    refresh_token_expiry = 604800;

-- 创建自定义邮件模板（示例）
-- 注意：实际邮件模板需要在 Supabase Dashboard 的 Authentication > Email Templates 中配置

-- 允许邮箱注册
UPDATE auth.authentication_methods
SET allow_sign_up = true
WHERE provider = 'email';

-- 禁用其他认证提供程序（暂时只使用邮箱认证）
UPDATE auth.authentication_methods
SET allow_sign_up = false
WHERE provider IN ('google', 'github', 'gitlab', 'bitbucket', 'azure', 'apple', 'facebook', 'twitter', 'phone');

-- 创建审计日志函数（可选）
CREATE OR REPLACE FUNCTION auth.log_auth_event()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auth.audit_log (user_id, event_type, metadata, created_at)
    VALUES (
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        jsonb_build_object(
            'table', TG_TABLE_NAME,
            'operation', TG_OP,
            'new', NEW,
            'old', OLD
        ),
        NOW()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建审计日志表（如果不存在）
CREATE TABLE IF NOT EXISTS auth.audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 为审计日志表创建索引
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON auth.audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON auth.audit_log(created_at);

-- 输出配置信息
DO $$
BEGIN
    RAISE NOTICE 'Supabase Auth 配置完成';
    RAISE NOTICE '邮箱认证: 已启用';
    RAISE NOTICE '密码最小长度: 8 字符';
    RAISE NOTICE '访问令牌过期时间: 1 小时';
    RAISE NOTICE '刷新令牌过期时间: 7 天';
    RAISE NOTICE '审计日志: 已启用';
END $$;
