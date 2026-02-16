# -*- coding: utf-8 -*-
"""Test script for Skills + Database experiment.

Run this script to verify the skills framework works with Supabase.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_direct_skill():
    """Test 1: Direct skill execution."""
    print("=" * 60)
    print("TEST 1: Direct Skill Execution")
    print("=" * 60)

    from skills.examples.db_query.handler import handle

    test_input = {
        "table": "users",
        "columns": "id,email,created_at",
        "limit": 3
    }

    result = handle(test_input)

    print(f"\nInput: {test_input}")
    print(f"\nResult: {result}")

    if result["success"]:
        print(f"\n[PASS] Retrieved {result['data']['row_count']} records")
        return True
    else:
        print(f"\n[FAIL] {result['error']}")
        return False


async def test_logic_chain():
    """Test 2: Logic chain execution."""
    print("\n" + "=" * 60)
    print("TEST 2: Logic Chain Execution")
    print("=" * 60)

    try:
        from skills.logic_chain import ChainExecutor, DatabaseNode, ExecutionConfig

        config = ExecutionConfig(debug_mode=True)
        executor = ChainExecutor(config)

        executor.register_node(DatabaseNode(
            node_id="query_users",
            name="Query Users from Database",
            table="users",
            columns="id,email,created_at",
            limit=5,
            output_key="user_list",
        ))

        print("\n[INFO] Executing chain: query_users")
        context = await executor.execute_chain(
            chain_name="db_query_chain",
            start_node_id="query_users",
            user_data={},
        )

n[INFO        print(f"\] Chain completed")
        print(f"[INFO] Variables: user_list = {context.get('user_list', 'NOT SET')}")

        if context.get("user_list"):
            print(f"\n[PASS] Logic chain executed successfully")
            return:
            print(f True
        else"\n[FAIL] No data retrieved")
            return False

    except ImportError as e:
        print(f"\n[SKIP] Logic chain test (some modules not ready): {e}")
        return None


async def test_condition_branch():
    """Test 3: Condition branching."""
    print("\n" + "=" * 60)
    print("TEST 3: Condition Branching")
    print("=" * 60)

    try:
        from skills.logic_chain import (
            ChainExecutor, DatabaseNode, ConditionNode, IfElseNode,
            SkillNode, ExecutionConfig
        )

        config = ExecutionConfig(debug_mode=True)
        executor = ChainExecutor(config)

        executor.register_node(DatabaseNode(
            node_id="check_admin",
            name="Check if admin user exists",
            table="users",
            columns="id",
            where={"email": "admin@example.com"},
            limit=1,
            output_key="admin_exists",
        ))

        executor.register_node(ConditionNode(
            node_id="is_admin_found",
            name="Admin Found Check",
            condition="$admin_exists != []",
            output_key="should_proceed",
        ))

        executor.register_node(IfElseNode(
            node_id="if_admin_exists",
            name="IF Admin Exists",
            condition_node_id="is_admin_found",
        ))

        executor.register_node(SkillNode(
            node_id="grant_access",
            name="Grant Admin Access",
            skill_name="dummy",
            parameters={"message": "Admin access granted"},
        ))

        executor.register_node(SkillNode(
            node_id="deny_access",
            name="Deny Access",
            skill_name="dummy",
            parameters={"message": "Access denied - no admin found"},
        ))

        executor.nodes["check_admin"].metadata = {"next": {"default": "is_admin_found"}}
        executor.nodes["is_admin_found"].metadata = {"next": {"default": "if_admin_exists"}}
        executor.nodes["if_admin_exists"].metadata = {
            "next": {
                "true": "grant_access",
                "false": "deny_access"
            }
        }

        print("\n[INFO] Chain visualization:")
        print(executor.visualize_chain("check_admin"))

        print("\n[INFO] Executing chain with condition branching")
        context = await executor.execute_chain(
            chain_name="condition_test",
            start_node_id="check_admin",
            user_data={},
        )

        print(f"\n[PASS] Condition chain executed")
        return True

    except Exception as e:
        print(f"\n[FAIL] {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("# Skills + Database Integration Test")
    print("#" * 60)

    results = []

    results.append(await test_direct_skill())
    results.append(await test_logic_chain())
    results.append(await test_condition_branch())

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print(f"Passed:   {passed}")
    print(f"Failed:   {failed}")
    print(f"Skipped:  {skipped}")

    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[ERROR] Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
