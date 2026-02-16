# -*- coding: utf-8 -*-
"""Example chain demonstrating IF/ELSE branching logic."""

import asyncio
from skills.logic_chain import (
    ChainExecutor,
    ChainContext,
    ExecutionConfig,
    SkillNode,
    ConditionNode,
    IfElseNode,
)


def create_user_registration_chain() -> ChainExecutor:
    """Create a user registration verification chain.

    Flow:
    1. Start
    2. Validate email format
    3. IF email valid -> Check if user exists
       ELSE -> Reject registration
    4. IF user doesn't exist -> Create user
       ELSE -> Return "user exists" error
    5. End
    """
    config = ExecutionConfig(debug_mode=True)
    executor = ChainExecutor(config)

    executor.register_node(SkillNode(
        node_id="start",
        name="Start Node",
        skill_name="dummy_start",
        parameters={},
    ))

    executor.register_node(ConditionNode(
        node_id="check_email",
        name="Validate Email Format",
        condition="$email matches .*@.*\\..*",
        output_key="email_valid",
    ))

    executor.register_node(IfElseNode(
        node_id="if_email_valid",
        name="IF Email Valid",
        condition_node_id="check_email    executor.register_node(SkillNode(
",
    ))

        node_id="check_user_exists",
        name="Check User Exists",
        skill_name="check_user",
        parameters={"email": "$email"},
        output_key="user_exists",
    ))

    executor.register_node(ConditionNode(
        node_id="check_user_not_exists",
        name="User Doesn't Exist",
        condition="$user_exists == false",
        output_key="can_register",
    ))

    executor.register_node(IfElseNode(
        node_id="if_user_not_exists",
        name="IF User Not Exists",
        condition_node_id="check_user_not_exists",
    ))

    executor.register_node(SkillNode(
        node_id="create_user",
        name="Create User",
        skill_name="create_user",
        parameters={
            "email": "$email",
            "name": "$name",
        },
    ))

    executor.register_node(SkillNode(
        node_id="reject_registration",
        name="Reject Registration",
        skill_name="reject_registration",
        parameters={"reason": "Invalid email format"},
    ))

    executor.register_node(SkillNode(
        node_id="user_exists_error",
        name="User Already Exists",
        skill_name="user_exists_error",
        parameters={"email": "$email"},
    ))

    executor.register_node(SkillNode(
        node_id="end_success",
        name="Registration Complete",
        skill_name="dummy_success",
        parameters={},
    ))

    executor.register_node(SkillNode(
        node_id="end_error",
        name="Error End",
        skill_name="dummy_error",
        parameters={},
    ))

    executor.nodes["start"].metadata = {"next": {"default": "check_email"}}
    executor.nodes["check_email"].metadata = {"next": {"default": "if_email_valid"}}
    executor.nodes["if_email_valid"].metadata = {
        "next": {
            "true": "check_user_exists",
            "false": "reject_registration",
        }
    }
    executor.nodes["check_user_exists"].metadata = {"next": {"default": "check_user_not_exists"}}
    executor.nodes["check_user_not_exists"].metadata = {"next": {"default": "if_user_not_exists"}}
    executor.nodes["if_user_not_exists"].metadata = {
        "next": {
            "true": "create_user",
            "false": "user_exists_error",
        }
    }
    executor.nodes["create_user"].metadata = {"next": {"default": "end_success"}}
    executor.nodes["reject_registration"].metadata = {"next": {"default": "end_error"}}
    executor.nodes["user_exists_error"].metadata = {"next": {"default": "end_error"}}

    return executor


async def run_example():
    """Run the example chain."""
    executor = create_user_registration_chain()

    print("\n" + "=" * 60)
    print("Chain Visualization:")
    print("=" * 60)
    print(executor.visualize_chain("start"))

    print("\n" + "=" * 60)
    print("Executing Chain - Scenario 1: Valid New User")
    print("=" * 60)

    context = await executor.execute_chain(
        chain_name="user_registration",
        start_node_id="start",
        user_data={
            "email": "newuser@example.com",
            "name": "New User",
        },
    )

    print(f"\nFinal Variables: {context.variables}")
    print(f"\nNode Results: {list(context.node_results.keys())}")

    print("\n" + "=" * 60)
    print("Executing Chain - Scenario 2: Invalid Email")
    print("=" * 60)

    executor2 = create_user_registration_chain()
    context2 = await executor2.execute_chain(
        chain_name="user_registration_invalid",
        start_node_id="start",
        user_data={
            "email": "invalid-email",
            "name": "Bad User",
        },
    )

    print(f"\nFinal Variables: {context2.variables}")


if __name__ == "__main__":
    asyncio.run(run_example())
