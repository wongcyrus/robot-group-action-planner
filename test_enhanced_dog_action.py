#!/usr/bin/env python3
"""
Test script for the enhanced NetworkDogAction with MovementGroups integration.

This script demonstrates how to use the new NetworkDogAction class that directly
calls MovementGroups functions without any backwards compatibility mapping.
"""

import time

from actions.dog_action import DogAction


def test_movement_groups_actions():
    """Test various MovementGroups actions."""

    # Initialize the NetworkDogAction with direct MovementGroups action names
    action_timings = {
        # Basic movement actions
        "move_forward": 3.0,
        "move_backward": 3.0,
        "move_left": 2.0,
        "move_right": 2.0,
        # Looking actions
        "look_up": 2.0,
        "look_down": 2.0,
        "look_left": 2.0,
        "look_right": 2.0,
        # Complex movements
        "head_move": 3.0,
        "body_row": 2.0,
        "height_move": 3.0,
        "gait_uni": 4.0,
        # Leg movements
        "foreleg_lift": 2.0,
        "backleg_lift": 2.0,
        # Special movements
        "rotate": 3.0,
        "bowback": 2.0,
        "body_cycle": 5.0,
        "head_ellipse": 4.0,
        # Control actions
        "stop": 1.0,
    }

    repeat_counts = {
        "move_forward": 1,
        "look_up": 2,
        "body_cycle": 1,
        "head_ellipse": 1,
    }

    dog_action = DogAction(
        action_name_to_time=action_timings,
        action_name_to_repeat_time=repeat_counts,
        dog_id="test_dog",
        robot_ip="10.0.0.10",  # Update with your robot's IP
        robot_api_port=8080,
    )

    print("Testing Enhanced NetworkDogAction with MovementGroups")
    print("=" * 60)

    # Test connection and get available actions
    print("\n1. Checking robot connection and available actions...")
    status = dog_action.get_robot_status()
    if status.get("connected", False):
        print(
            f"✅ Connected to robot at {dog_action.robot_ip}:{dog_action.robot_api_port}"
        )
        available_actions = status.get("available_actions", [])
        print(f"📋 Available actions: {', '.join(available_actions)}")
    else:
        print(f"❌ Failed to connect to robot: {status.get('error', 'Unknown error')}")
        print("⚠️  Running in simulation mode for demonstration...")

    # Test basic movement actions
    print("\n2. Testing basic movement actions...")
    basic_movements = ["move_forward", "move_backward", "move_left", "move_right"]

    for action in basic_movements:
        print(f"  🐕 Executing: {action}")
        success = dog_action.execute_action_sync(action)
        if success:
            print(f"  ✅ {action} completed successfully")
        else:
            print(f"  ❌ {action} failed")
        time.sleep(0.5)

    # Test looking actions
    print("\n3. Testing head/looking actions...")
    look_actions = ["look_up", "look_down", "look_left", "look_right"]

    for action in look_actions:
        print(f"  👀 Executing: {action}")
        success = dog_action.execute_action_sync(action)
        if success:
            print(f"  ✅ {action} completed successfully")
        else:
            print(f"  ❌ {action} failed")
        time.sleep(0.5)

    # Test complex movements
    print("\n4. Testing complex movement actions...")
    complex_actions = ["body_cycle", "head_ellipse", "rotate"]

    for action in complex_actions:
        print(f"  🎭 Executing: {action}")
        success = dog_action.execute_action_sync(action)
        if success:
            print(f"  ✅ {action} completed successfully")
        else:
            print(f"  ❌ {action} failed")
        time.sleep(1.0)

    # Test leg movements
    print("\n5. Testing leg movement actions...")
    leg_actions = ["foreleg_lift", "backleg_lift"]

    for action in leg_actions:
        print(f"  🦵 Executing: {action}")
        success = dog_action.execute_action_sync(action)
        if success:
            print(f"  ✅ {action} completed successfully")
        else:
            print(f"  ❌ {action} failed")
        time.sleep(0.5)

    # Test stop action
    print("\n6. Testing stop action...")
    print("  🛑 Executing: stop")
    success = dog_action.execute_action_sync("stop")
    if success:
        print("  ✅ stop completed successfully")
    else:
        print("  ❌ stop failed")

    # Clean up
    print("\n7. Cleaning up...")
    dog_action.cleanup()
    print("  ✅ Cleanup completed")

    print("\n" + "=" * 60)
    print("Enhanced NetworkDogAction test completed!")
    print("All MovementGroups actions are now directly accessible without mapping.")


if __name__ == "__main__":
    test_movement_groups_actions()
