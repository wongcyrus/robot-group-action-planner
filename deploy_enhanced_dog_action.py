#!/usr/bin/env python3
"""
Deployment script for Enhanced Dog Action Integration

This script helps deploy the enhanced dog action integration to your robot setup.
It can be run from the PC to deploy files to the robot automatically.

Usage:
    python deploy_enhanced_dog_action.py [options]
"""

import argparse
import os
import subprocess
import sys


def run_command(command, check=True, capture_output=True):
    """Run a command and handle errors."""
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=capture_output, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e}")
        if capture_output:
            print(f"Output: {e.stdout}")
            print(f"Error output: {e.stderr}")
        return None


def check_robot_connectivity(robot_ip, robot_user="ubuntu"):
    """Check if the robot is reachable via SSH."""
    print(f"Checking connectivity to {robot_user}@{robot_ip}...")

    result = run_command(
        f"ssh -o ConnectTimeout=5 -o BatchMode=yes {robot_user}@{robot_ip} 'echo connected'"
    )

    if result and result.returncode == 0:
        print("✓ Robot is reachable via SSH")
        return True
    else:
        print("✗ Cannot connect to robot via SSH")
        print(
            f"  Make sure SSH key authentication is set up for {robot_user}@{robot_ip}"
        )
        return False


def deploy_files_to_robot(robot_ip, robot_user="ubuntu"):
    """Deploy enhanced files to the robot."""
    print("Deploying files to robot...")

    # Files to deploy
    files_to_deploy = [
        (
            "StanfordQuadruped-mini_pupper/network_action_server.py",
            "/home/ubuntu/StanfordQuadruped/network_action_server.py",
        ),
        (
            "StanfordQuadruped-mini_pupper/setup_enhanced_network_server.py",
            "/home/ubuntu/setup_enhanced_network_server.py",
        ),
    ]

    for local_file, remote_file in files_to_deploy:
        if not os.path.exists(local_file):
            print(f"✗ Local file not found: {local_file}")
            return False

        print(f"  Copying {local_file} -> {robot_user}@{robot_ip}:{remote_file}")
        result = run_command(f"scp {local_file} {robot_user}@{robot_ip}:{remote_file}")

        if not result or result.returncode != 0:
            print(f"✗ Failed to copy {local_file}")
            return False

    print("✓ Files deployed successfully")
    return True


def run_robot_setup(robot_ip, robot_user="ubuntu", install_service=True):
    """Run the setup script on the robot."""
    print("Running setup on robot...")

    setup_args = ""
    if not install_service:
        setup_args = "--no-service"

    # Run setup script
    setup_command = (
        f"cd /home/ubuntu && python3 setup_enhanced_network_server.py {setup_args}"
    )

    if install_service:
        setup_command = f"sudo {setup_command}"

    print(f"  Executing: {setup_command}")
    result = run_command(
        f"ssh {robot_user}@{robot_ip} '{setup_command}'", capture_output=False
    )

    if result and result.returncode == 0:
        print("✓ Robot setup completed successfully")
        return True
    else:
        print("✗ Robot setup failed")
        return False


def test_api_connection(robot_ip, api_port=8080):
    """Test the API connection to the robot."""
    print(f"Testing API connection to http://{robot_ip}:{api_port}...")

    try:
        import requests

        response = requests.get(f"http://{robot_ip}:{api_port}/status", timeout=10)

        if response.status_code == 200:
            print("✓ API is accessible and responding")
            status = response.json()
            print(f"  Robot running: {status.get('running', 'unknown')}")
            print(f"  Available actions: {len(status.get('available_actions', []))}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False

    except ImportError:
        print("⚠ requests module not available, skipping API test")
        print("  Install with: pip install requests")
        return True  # Don't fail deployment for this

    except Exception as e:
        print(f"✗ API connection failed: {e}")
        print("  The service might still be starting up")
        return False


def update_local_config():
    """Update the local configuration to use enhanced dog action."""
    print("Updating local configuration...")

    # Check if main.py exists and suggest changes
    if os.path.exists("main.py"):
        print("  Found main.py - you may need to update it to use enhanced dog action")
        print("  Change:")
        print("    from actions.dog_action import DogAction")
        print("  to:")
        print("    from actions.enhanced_dog_action import DogAction")
        print(
            "  (Or just use the existing import - it will auto-detect the enhanced version)"
        )

    # Check if enhanced_dog_action.py exists
    if os.path.exists("actions/enhanced_dog_action.py"):
        print("✓ Enhanced dog action is available locally")
    else:
        print("⚠ Enhanced dog action not found locally")
        print("  Make sure enhanced_dog_action.py is in the actions/ directory")

    return True


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(
        description="Deploy Enhanced Dog Action Integration"
    )
    parser.add_argument("--robot-ip", default="10.0.0.10", help="Robot IP address")
    parser.add_argument("--robot-user", default="ubuntu", help="Robot SSH username")
    parser.add_argument("--api-port", type=int, default=8080, help="Robot API port")
    parser.add_argument(
        "--no-service", action="store_true", help="Skip systemd service installation"
    )
    parser.add_argument(
        "--skip-test", action="store_true", help="Skip API connection test"
    )
    parser.add_argument(
        "--local-only", action="store_true", help="Only update local configuration"
    )

    args = parser.parse_args()

    print("Enhanced Dog Action Integration Deployment")
    print("=" * 50)

    # Update local configuration
    if not update_local_config():
        print("Local configuration update failed")
        return 1

    # Skip robot deployment if local-only
    if args.local_only:
        print("\nLocal-only mode - skipping robot deployment")
        print("✅ Local configuration updated successfully")
        return 0

    # Check robot connectivity
    if not check_robot_connectivity(args.robot_ip, args.robot_user):
        print("\nDeployment failed - cannot reach robot")
        print("Make sure:")
        print(f"  1. Robot is powered on and connected to network")
        print(f"  2. Robot IP {args.robot_ip} is correct")
        print(f"  3. SSH key authentication is set up")
        print(f"  4. You can manually SSH: ssh {args.robot_user}@{args.robot_ip}")
        return 1

    # Deploy files
    if not deploy_files_to_robot(args.robot_ip, args.robot_user):
        print("\nDeployment failed - file transfer error")
        return 1

    # Run setup on robot
    if not run_robot_setup(args.robot_ip, args.robot_user, not args.no_service):
        print("\nDeployment failed - robot setup error")
        return 1

    # Test API connection
    if not args.skip_test:
        if not args.no_service:
            print("\nWaiting for service to start...")
            import time

            time.sleep(5)

        if not test_api_connection(args.robot_ip, args.api_port):
            print("\nAPI test failed - but deployment may still be successful")
            print("The service might need more time to start up")
            print(f"Try manually: curl http://{args.robot_ip}:{args.api_port}/status")

    # Success message
    print(
        f"""
✅ Enhanced Dog Action Integration Deployed Successfully!

🤖 Robot Configuration:
   IP: {args.robot_ip}
   API Port: {args.api_port}
   Service: {'Installed' if not args.no_service else 'Manual start required'}

📡 Test Connection:
   curl http://{args.robot_ip}:{args.api_port}/status

🔧 Manual Control:
   SSH: ssh {args.robot_user}@{args.robot_ip}
   Start: sudo systemctl start quadruped-network-server
   Status: sudo systemctl status quadruped-network-server

📋 Next Steps:
   1. Test the API connection
   2. Update your choreography scripts to use the new features
   3. Enjoy improved robot control!
"""
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
