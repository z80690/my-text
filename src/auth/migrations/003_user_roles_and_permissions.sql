-- 用户角色和权限管理架构
-- 为系统添加基于角色的访问控制 (RBAC)
-- 在 Supabase SQL Editor 中执行此脚本

-- ========================================
-- 1. 创建角色表
-- ========================================

CREATE TABLE IF NOT EXISTS public.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]::jsonb',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ========================================
-- 2. 创建用户角色关联表
-- ========================================

CREATE TABLE IF NOT EXISTS public.user_role_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES public.user_roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ,  -- 可选的过期时间
    UNIQUE(user_id, role_id)
);

-- ========================================
-- 3. 创建索引
-- ========================================

-- 为角色名称创建索引
CREATE INDEX IF NOT EXISTS idx_user_roles_name ON public.user_roles(name);
CREATE INDEX IF NOT EXISTS idx_user_roles_is_active ON public.user_roles(is_active);

-- 为用户角色关联创建索引
CREATE INDEX IF NOT EXISTS idx_user_role_assignments_user_id ON public.user_role_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_user_role_assignments_role_id ON public.user_role_assignments(role_id);
CREATE INDEX IF NOT EXISTS idx_user_role_assignments_expires_at ON public.user_role_assignments(expires_at);

-- ========================================
-- 4. 创建触发器函数（自动更新 updated_at）
-- ========================================

CREATE OR REPLACE FUNCTION public.handle_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 5. 创建触发器
-- ========================================

CREATE TRIGGER update_user_roles_updated_at
    BEFORE UPDATE ON public.user_roles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_roles_updated_at();

-- ========================================
-- 6. 启用行级安全（RLS）
-- ========================================

ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_role_assignments ENABLE ROW LEVEL SECURITY;

-- ========================================
-- 7. 创建 RLS 策略
-- ========================================

-- 角色表策略
CREATE POLICY "Authenticated users can view active roles" ON public.user_roles
    FOR SELECT
    USING (auth.role() = 'authenticated' AND is_active = true);

CREATE POLICY "Admins can manage roles" ON public.user_roles
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_role_assignments ura
            JOIN public.user_roles ur ON ura.role_id = ur.id
            WHERE ura.user_id = auth.uid()
            AND ur.name = 'admin'
            AND (ura.expires_at IS NULL OR ura.expires_at > NOW())
        )
    );

-- 用户角色关联表策略
CREATE POLICY "Users can view own role assignments" ON public.user_role_assignments
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own roles" ON public.user_role_assignments
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage role assignments" ON public.user_role_assignments
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.user_role_assignments ura
            JOIN public.user_roles ur ON ura.role_id = ur.id
            WHERE ura.user_id = auth.uid()
            AND ur.name = 'admin'
            AND (ura.expires_at IS NULL OR ura.expires_at > NOW())
        )
    );

-- ========================================
-- 8. 创建默认角色
-- ========================================

-- 插入默认角色（如果不存在）
INSERT INTO public.user_roles (name, description, permissions)
VALUES
    ('user', '普通用户角色', '[
        "profile:read",
        "profile:update"
    ]'::jsonb),
    ('admin', '管理员角色，拥有所有权限', '[
        "profile:read",
        "profile:update",
        "profile:delete",
        "users:read",
        "users:update",
        "users:delete",
        "roles:read",
        "roles:manage",
        "admin:all"
    ]'::jsonb),
    ('moderator', 'moderator role with limited admin permissions', '[
        "profile:read",
        "profile:update",
        "users:read",
        "users:update"
    ]'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- ========================================
-- 9. 创建辅助函数
-- ========================================

-- 函数：检查用户是否有特定权限
CREATE OR REPLACE FUNCTION public.user_has_permission(
    p_user_id UUID,
    p_permission TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_has_permission BOOLEAN := false;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM public.user_role_assignments ura
        JOIN public.user_roles ur ON ura.role_id = ur.id
        JOIN public.user_roles r ON ur.id = r.id
        WHERE ura.user_id = p_user_id
        AND ur.is_active = true
        AND (ura.expires_at IS NULL OR ura.expires_at > NOW())
        AND p_permission = ANY(r.permissions)
    ) INTO v_has_permission;

    RETURN v_has_permission;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 函数：获取用户的所有角色
CREATE OR REPLACE FUNCTION public.get_user_roles(p_user_id UUID)
RETURNS TABLE (
    role_id UUID,
    role_name TEXT,
    permissions JSONB,
    assigned_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ur.id,
        ur.name,
        ur.permissions,
        ura.assigned_at,
        ura.expires_at
    FROM public.user_role_assignments ura
    JOIN public.user_roles ur ON ura.role_id = ur.id
    WHERE ura.user_id = p_user_id
    AND ur.is_active = true
    AND (ura.expires_at IS NULL OR ura.expires_at > NOW());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 函数：为用户分配角色
CREATE OR REPLACE FUNCTION public.assign_role(
    p_user_id UUID,
    p_role_name TEXT,
    p_assigned_by UUID,
    p_expires_at TIMESTAMPTZ DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    v_role_id UUID;
BEGIN
    -- 获取角色 ID
    SELECT id INTO v_role_id
    FROM public.user_roles
    WHERE name = p_role_name AND is_active = true;

    IF v_role_id IS NULL THEN
        RETURN false;
    END IF;

    -- 更新或插入角色分配
    INSERT INTO public.user_role_assignments (user_id, role_id, assigned_by, expires_at)
    VALUES (p_user_id, v_role_id, p_assigned_by, p_expires_at)
    ON CONFLICT (user_id, role_id)
    DO UPDATE SET expires_at = p_expires_at;

    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 函数：移除用户角色
CREATE OR REPLACE FUNCTION public.remove_role(
    p_user_id UUID,
    p_role_name TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_role_id UUID;
BEGIN
    -- 获取角色 ID
    SELECT id INTO v_role_id
    FROM public.user_roles
    WHERE name = p_role_name AND is_active = true;

    IF v_role_id IS NULL THEN
        RETURN false;
    END IF;

    -- 删除角色分配
    DELETE FROM public.user_role_assignments
    WHERE user_id = p_user_id AND role_id = v_role_id;

    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ========================================
-- 10. 创建视图
-- ========================================

-- 视图：用户角色概览
CREATE OR REPLACE VIEW public.user_roles_overview AS
SELECT
    u.id AS user_id,
    u.email,
    up.display_name,
    COALESCE(
        json_agg(
            json_build_object(
                'role', ur.name,
                'permissions', ur.permissions,
                'assigned_at', ura.assigned_at,
                'expires_at', ura.expires_at
            }) FILTER (WHERE ur.name IS NOT NULL)
        , '[]'::json
    ) AS roles,
    COUNT(ur.id) AS role_count
FROM auth.users u
LEFT JOIN public.user_profiles up ON u.id = up.id
LEFT JOIN public.user_role_assignments ura ON u.id = ura.user_id
LEFT JOIN public.user_roles ur ON ura.role_id = ur.id
    AND (ura.expires_at IS NULL OR ura.expires_at > NOW())
    AND ur.is_active = true
GROUP BY u.id, u.email, up.display_name;

-- ========================================
-- 11. 添加注释
-- ========================================

COMMENT ON TABLE public.user_roles IS '用户角色定义表';
COMMENT ON TABLE public.user_role_assignments IS '用户角色关联表';

COMMENT ON COLUMN public.user_roles.name IS '角色名称 (user, admin, moderator)';
COMMENT ON COLUMN public.user_roles.permissions IS '角色权限列表';
COMMENT ON COLUMN public.user_role_assignments.expires_at IS '角色分配过期时间';

COMMENT ON FUNCTION public.user_has_permission(UUID, TEXT) IS '检查用户是否有特定权限';
COMMENT ON FUNCTION public.get_user_roles(UUID) IS '获取用户的所有角色';
COMMENT ON FUNCTION public.assign_role(UUID, TEXT, UUID, TIMESTAMPTZ) IS '为用户分配角色';
COMMENT ON FUNCTION public.remove_role(UUID, TEXT) IS '移除用户角色';

-- ========================================
-- 12. 输出创建结果
-- ========================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '用户角色和权限系统创建成功';
    RAISE NOTICE '========================================';
    RAISE NOTICE '表: public.user_roles';
    RAISE NOTICE '表: public.user_role_assignments';
    RAISE NOTICE '默认角色: user, admin, moderator';
    RAISE NOTICE 'RLS: 已启用';
    RAISE NOTICE '========================================';
    RAISE NOTICE '辅助函数:';
    RAISE NOTICE '  - user_has_permission(user_id, permission)';
    RAISE NOTICE '  - get_user_roles(user_id)';
    RAISE NOTICE '  - assign_role(user_id, role_name, assigned_by, expires_at)';
    RAISE NOTICE '  - remove_role(user_id, role_name)';
    RAISE NOTICE '========================================';
END $$;
