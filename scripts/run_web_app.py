#!/usr/bin/env python3
"""
Script to run EpochAI web applications
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web.apps.main_app import create_main_app
from web.apps.realtime_app import create_realtime_app
from web.apps.simple_app import create_simple_app
from config.settings import settings
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(settings.log_level)
logger = get_logger('scripts')


def main():
    """Main function to run web applications"""
    parser = argparse.ArgumentParser(description='Run EpochAI Web Application')
    parser.add_argument('--app', choices=['main', 'realtime', 'simple'], 
                       default='main', help='Web application to run')
    parser.add_argument('--host', default=settings.web.host, 
                       help='Host to bind to')
    parser.add_argument('--port', type=int, default=settings.web.port, 
                       help='Port to bind to')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("🌐 EpochAI Web Application Server")
    print("=" * 40)
    
    # Create the appropriate app
    if args.app == 'main':
        app = create_main_app()
        print("📊 Starting Main Dashboard Application")
    elif args.app == 'realtime':
        app = create_realtime_app()
        print("⚡ Starting Real-time Dashboard Application")
    elif args.app == 'simple':
        app = create_simple_app()
        print("🎯 Starting Simple Dashboard Application")
    
    # Override settings if provided
    if args.debug:
        app.config['DEBUG'] = True
    
    print(f"🚀 Server starting on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or settings.web.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"❌ Server error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())