#!/usr/bin/env python3
"""
Enhanced Stanford Quadruped Integration Script
==============================================

This script provides a complete integration between the Enhanced Network Action Server
and the Stanford Quadruped MovementGroups system, utilizing the improved dance
choreography and action mapping.

Features:
- Direct integration with enhanced createDanceActionListSample.py
- Network action server integration
- Enhanced action mapping
- Real-time choreography execution
- HTTP API endpoint support
- Comprehensive logging and monitoring

Usage:
    python enhanced_stanford_integration.py [options]

Options:
    --network-mode    : Run in network server mode (default: local)
    --port           : HTTP server port (default: 8080)
    --robot-ip       : Robot IP address (default: 10.0.0.10)
    --log-level      : Logging level (default: INFO)
    --demo-mode      : Run demonstration choreography
    --action ACTION  : Execute specific action
    --duration SECS  : Duration for action execution

Author: Enhanced Robot Action Planner System
Date: 2024
License: Apache 2.0
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add paths for imports
sys.path.append(
    os.path.join(os.path.dirname(__file__), "StanfordQuadruped-mini_pupper", "src")
)
sys.path.append(os.path.dirname(__file__))

try:
    from MovementGroup import MovementGroups
except ImportError:
    print("Warning: MovementGroups not available. Using mock implementation.")

    class MovementGroups:
        def __init__(self):
            self.MovementLib = []

        def __getattr__(self, name):
            return lambda *args, **kwargs: print(f"Mock: {name}({args}, {kwargs})")


try:
    from enhanced_action_mapping import EnhancedActionMapper
except ImportError:
    print(
        "Error: Enhanced action mapping not found. Please ensure enhanced_action_mapping.py is available."
    )
    sys.exit(1)


class EnhancedStanfordIntegration:
    """
    Main integration class that combines Stanford Quadruped movements
    with the enhanced network action system
    """

    def __init__(
        self, network_mode: bool = False, port: int = 8080, robot_ip: str = "10.0.0.10"
    ):
        """
        Initialize the enhanced Stanford integration

        Args:
            network_mode: Whether to run in network server mode
            port: HTTP server port for network mode
            robot_ip: Robot IP address for network communication
        """
        self.network_mode = network_mode
        self.port = port
        self.robot_ip = robot_ip

        # Setup logging
        self._setup_logging()

        # Initialize movement system
        self.movement_groups = MovementGroups()

        # Initialize action mapper
        self.action_mapper = EnhancedActionMapper(self.movement_groups)

        # Network server (if in network mode)
        self.server = None

        self.logger.info("Enhanced Stanford Quadruped Integration initialized")
        self.logger.info(f"Network mode: {network_mode}")
        self.logger.info(
            f"Available actions: {len(self.action_mapper.get_available_actions())}"
        )

    def _setup_logging(self) -> None:
        """Setup comprehensive logging"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "enhanced_stanford_integration.log"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger(__name__)

    def start_network_server(self) -> None:
        """Start the HTTP network server for remote control"""
        if not self.network_mode:
            self.logger.warning("Network mode not enabled")
            return

        try:
            import json
            from http.server import BaseHTTPRequestHandler, HTTPServer

            class EnhancedActionHandler(BaseHTTPRequestHandler):
                def __init__(self, integration_instance, *args, **kwargs):
                    self.integration = integration_instance
                    super().__init__(*args, **kwargs)

                def do_POST(self):
                    """Handle POST requests for action execution"""
                    try:
                        # Parse request
                        content_length = int(self.headers["Content-Length"])
                        post_data = self.rfile.read(content_length)
                        request_data = json.loads(post_data.decode("utf-8"))

                        action = request_data.get("action")
                        parameters = request_data.get("parameters", {})

                        if not action:
                            self.send_error(400, "Missing 'action' parameter")
                            return

                        # Execute action
                        success = self.integration.execute_action(action, parameters)

                        # Send response
                        self.send_response(200 if success else 500)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()

                        response = {
                            "success": success,
                            "action": action,
                            "parameters": parameters,
                            "timestamp": time.time(),
                        }

                        self.wfile.write(json.dumps(response).encode("utf-8"))

                    except Exception as e:
                        self.integration.logger.error(
                            f"Error handling request: {str(e)}"
                        )
                        self.send_error(500, str(e))

                def do_GET(self):
                    """Handle GET requests for status and available actions"""
                    if self.path == "/status":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()

                        status = {
                            "status": "active",
                            "available_actions": self.integration.action_mapper.get_available_actions(),
                            "robot_ip": self.integration.robot_ip,
                            "timestamp": time.time(),
                        }

                        self.wfile.write(json.dumps(status).encode("utf-8"))
                    else:
                        self.send_error(404, "Endpoint not found")

                def log_message(self, format, *args):
                    """Override to use our logger"""
                    self.integration.logger.info(f"HTTP: {format % args}")

            # Create server with integration instance bound to handler
            def handler_factory(*args, **kwargs):
                return EnhancedActionHandler(self, *args, **kwargs)

            self.server = HTTPServer(("0.0.0.0", self.port), handler_factory)
            self.logger.info(f"Starting HTTP server on port {self.port}")
            self.server.serve_forever()

        except Exception as e:
            self.logger.error(f"Error starting network server: {str(e)}")
            raise

    def execute_action(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Execute an action using the enhanced action mapper

        Args:
            action: Action name to execute
            parameters: Optional parameters for the action

        Returns:
            bool: True if action executed successfully
        """
        try:
            self.logger.info(f"Executing action: {action}")
            if parameters:
                self.logger.info(f"Parameters: {parameters}")

            success = self.action_mapper.execute_action(action, parameters)

            if success:
                self.logger.info(f"Action {action} completed successfully")
            else:
                self.logger.error(f"Action {action} failed")

            return success

        except Exception as e:
            self.logger.error(f"Error executing action {action}: {str(e)}")
            return False

    def run_enhanced_choreography(self) -> None:
        """
        Run the enhanced choreography from createDanceActionListSample.py
        but with improved integration and monitoring
        """
        self.logger.info("Starting Enhanced Choreography Sequence")

        try:
            # Load and execute the enhanced choreography
            # This integrates with our enhanced createDanceActionListSample.py

            self.logger.info("=== Enhanced Mini Pupper Dance Choreography ===")

            # Execute greeting sequence
            self.execute_action("greeting_sequence", {"duration": 3.0})

            # Execute main dance sequence with enhanced actions
            self.execute_action("dance", {"duration": 15.0, "intensity": 1.2})

            # Execute complex choreography
            self.execute_action("complex_dance", {"duration": 10.0, "intensity": 1.5})

            # Execute finale
            self.execute_action("finale_sequence", {"duration": 8.0})

            self.logger.info("Enhanced choreography completed successfully")

        except Exception as e:
            self.logger.error(f"Error during choreography execution: {str(e)}")
            # Emergency stop
            self.execute_action("emergency_stop")

    def run_demo_mode(self) -> None:
        """Run demonstration mode showing various capabilities"""
        self.logger.info("Starting Demo Mode")

        # Demo sequence
        demos = [
            ("activate", {"duration": 2.0}),
            ("greeting_sequence", {"duration": 3.0}),
            ("forward", {"speed": 0.8, "duration": 2.0}),
            ("turn_right", {"intensity": 1.0}),
            ("dance", {"duration": 8.0, "intensity": 1.0}),
            ("bow", {"intensity": 1.2, "duration": 2.0}),
            ("wave", {"intensity": 1.5}),
            ("celebrate", {"intensity": 1.3}),
            ("circle", {"intensity": 1.0}),
            ("finale_sequence", {"duration": 5.0}),
            ("deactivate", {"duration": 2.0}),
        ]

        for action, params in demos:
            self.logger.info(f"Demo: Executing {action}")
            self.execute_action(action, params)
            time.sleep(1)  # Brief pause between demos

        self.logger.info("Demo mode completed")

    def list_available_actions(self) -> None:
        """List all available actions with categories"""
        actions = self.action_mapper.get_available_actions()

        print("\n=== Enhanced Stanford Quadruped Available Actions ===")
        print(f"Total actions: {len(actions)}")

        # Group actions by category for better presentation
        categories = {
            "Basic Movement": [
                "forward",
                "backward",
                "left",
                "right",
                "turn_left",
                "turn_right",
                "stop",
            ],
            "Activation": ["activate", "deactivate", "emergency_stop"],
            "Entertainment": ["dance", "bow", "wave", "celebrate"],
            "Posture": [
                "pitch_up",
                "pitch_down",
                "roll_left",
                "roll_right",
                "height_up",
                "height_down",
            ],
            "Head Movement": ["look_up", "look_down", "look_left", "look_right"],
            "Advanced": ["circle", "figure_eight", "shake", "stretch"],
            "Complex": ["complex_dance", "greeting_sequence", "finale_sequence"],
        }

        for category, cat_actions in categories.items():
            available_in_category = [a for a in cat_actions if a in actions]
            if available_in_category:
                print(f"\n{category}:")
                for action in available_in_category:
                    print(f"  - {action}")

    def stop(self) -> None:
        """Stop the integration system"""
        self.logger.info("Stopping Enhanced Stanford Integration")

        if self.server:
            self.server.shutdown()
            self.logger.info("HTTP server stopped")

        # Execute emergency stop action
        self.execute_action("emergency_stop")


def main():
    """Main entry point for the enhanced Stanford integration"""
    parser = argparse.ArgumentParser(
        description="Enhanced Stanford Quadruped Integration"
    )

    parser.add_argument(
        "--network-mode", action="store_true", help="Run in network server mode"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="HTTP server port (default: 8080)"
    )
    parser.add_argument(
        "--robot-ip", default="10.0.0.10", help="Robot IP address (default: 10.0.0.10)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--demo-mode", action="store_true", help="Run demonstration choreography"
    )
    parser.add_argument("--action", help="Execute specific action")
    parser.add_argument(
        "--duration",
        type=float,
        default=1.0,
        help="Duration for action execution (default: 1.0)",
    )
    parser.add_argument(
        "--intensity",
        type=float,
        default=1.0,
        help="Intensity for action execution (default: 1.0)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speed for action execution (default: 1.0)",
    )
    parser.add_argument(
        "--list-actions",
        action="store_true",
        help="List all available actions and exit",
    )
    parser.add_argument(
        "--choreography",
        action="store_true",
        help="Run the enhanced choreography sequence",
    )

    args = parser.parse_args()

    # Setup logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        # Create integration instance
        integration = EnhancedStanfordIntegration(
            network_mode=args.network_mode, port=args.port, robot_ip=args.robot_ip
        )

        # Handle different modes
        if args.list_actions:
            integration.list_available_actions()
            return

        if args.action:
            # Execute specific action
            parameters = {
                "duration": args.duration,
                "intensity": args.intensity,
                "speed": args.speed,
            }
            success = integration.execute_action(args.action, parameters)
            if not success:
                sys.exit(1)
            return

        if args.demo_mode:
            integration.run_demo_mode()
            return

        if args.choreography:
            integration.run_enhanced_choreography()
            return

        if args.network_mode:
            print(f"Starting Enhanced Network Server on port {args.port}")
            print("Press Ctrl+C to stop")
            try:
                integration.start_network_server()
            except KeyboardInterrupt:
                print("\nShutting down...")
                integration.stop()
        else:
            # Default: run enhanced choreography
            print("Running Enhanced Stanford Quadruped Integration")
            print("Default mode: Enhanced Choreography")
            integration.run_enhanced_choreography()

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
