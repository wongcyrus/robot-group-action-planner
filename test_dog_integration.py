#!/usr/bin/env python3
"""
Test script to verify dog robot integration.
This script performs basic validation without requiring actual robot hardware.
"""

import logging
import sys
from unittest.mock import Mock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_dog_action_import():
    """Test that DogAction can be imported successfully."""
    try:
        # Test import only
        import dog_action  # noqa: F401

        logger.info("✓ DogAction import successful")
        return True
    except ImportError as e:
        logger.error(f"✗ DogAction import failed: {e}")
        return False


def test_dog_action_creation():
    """Test that DogAction can be created with mock dependencies."""
    try:
        from dog_action import DogAction

        # Create action mappings
        action_mappings = {
            "stand_up": 2.0,
            "forward": 2.0,
            "hop": 1.5,
        }

        # Create DogAction instance with None executor (test mode)
        dog_action = DogAction(
            None, action_mappings, {}, "test_dog"  # Use None for test mode
        )

        # Verify it was created successfully
        assert dog_action.dog_id == "test_dog"

        logger.info("✓ DogAction creation successful")
        return True
    except (ImportError, AssertionError, AttributeError) as e:
        logger.error(f"✗ DogAction creation failed: {e}")
        return False


def test_main_integration():
    """Test that main.py can import dog-related modules."""
    try:
        # Mock the dog modules to avoid hardware dependencies
        sys.modules["dog.action_executor"] = Mock()
        sys.modules["dog_action"] = Mock()

        from constant import DOG_IPS, DOG_PORTS, SKIP_DOGS

        logger.info(
            f"✓ Dog constants loaded: IPs={DOG_IPS}, Ports={DOG_PORTS}, Skip={SKIP_DOGS}"
        )

        # Test import of main components
        # Import main to verify it doesn't fail
        main_module = __import__("main")
        del main_module  # Clean up
        logger.info("✓ Main module imports successful")
        return True
    except (ImportError, AttributeError) as e:
        logger.error(f"✗ Main integration test failed: {e}")
        return False


def test_action_parameter_extraction():
    """Test parameter extraction from action names."""
    try:
        from dog_action import DogAction

        action_mappings = {"test": 1.0}

        dog_action = DogAction(None, action_mappings, {}, "test_dog")

        # Test distance extraction
        # pylint: disable=protected-access
        distance_result = dog_action._extract_distance("forward_100", 50)
        logger.info(f"Distance extraction result: {distance_result}")
        assert distance_result == 100
        assert dog_action._extract_distance("forward", 50) == 50

        # Test angle extraction
        assert dog_action._extract_angle("cw_90", 45) == 90
        assert dog_action._extract_angle("cw", 45) == 45

        # Test speed extraction
        assert dog_action._extract_speed("forward_50_0.7", 0.5) == 0.7
        assert dog_action._extract_speed("forward_50", 0.5) == 0.5

        # Test duration extraction
        assert dog_action._extract_duration("hop_2.5", 1.0) == 2.5
        assert dog_action._extract_duration("hop", 1.0) == 1.0
        # pylint: enable=protected-access

        logger.info("✓ Parameter extraction tests passed")
        return True
    except (ImportError, AssertionError, AttributeError) as e:
        logger.error(f"✗ Parameter extraction tests failed: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


def test_action_timing():
    """Test default action timing calculations."""
    try:
        from dog_action import DogAction

        action_mappings = {"test": 1.0}

        dog_action = DogAction(None, action_mappings, {}, "test_dog")

        # Test various action timings
        # pylint: disable=protected-access
        activate_time = dog_action._get_default_action_time("activate")
        logger.info(f"Activate time result: {activate_time}")
        assert activate_time == 1.0
        assert dog_action._get_default_action_time("stand_up") == 2.0
        assert dog_action._get_default_action_time("forward_50") == 2.0
        assert dog_action._get_default_action_time("cw_90") == 2.0
        assert dog_action._get_default_action_time("hop") == 1.5
        assert dog_action._get_default_action_time("stop") == 0.5
        assert dog_action._get_default_action_time("dance") == 3.0
        assert dog_action._get_default_action_time("unknown_action") == 2.0
        # pylint: enable=protected-access

        logger.info("✓ Action timing tests passed")
        return True
    except (ImportError, AssertionError, AttributeError) as e:
        logger.error(f"✗ Action timing tests failed: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False


def run_all_tests():
    """Run all validation tests."""
    logger.info("=== Dog Robot Integration Validation ===")

    tests = [
        ("Import Test", test_dog_action_import),
        ("Creation Test", test_dog_action_creation),
        ("Main Integration Test", test_main_integration),
        ("Parameter Extraction Test", test_action_parameter_extraction),
        ("Action Timing Test", test_action_timing),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            logger.error(f"{test_name} failed")

    logger.info("\n=== Test Results ===")
    logger.info(f"Passed: {passed}/{total}")

    if passed == total:
        logger.info("🎉 All tests passed! Dog robot integration is ready.")
        return True
    else:
        logger.error(
            f"❌ {total - passed} test(s) failed. Please check the issues above."
        )
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
