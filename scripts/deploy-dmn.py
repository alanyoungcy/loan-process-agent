#!/usr/bin/env python3
"""
Deploy DMN files to Camunda 8 Zeebe
"""
import os
import sys
from pyzeebe import ZeebeClient

# Zeebe connection
ZEEBE_HOST = "localhost"
ZEEBE_PORT = 26500

# DMN files directory
DMN_DIR = "/Volumes/Orico/code/capco/loan-agent/camunda-deployments"

def deploy_dmn_files():
    """Deploy all DMN files to Zeebe"""

    print("🚀 Deploying DMN files to Camunda 8 Zeebe...")
    print(f"📂 DMN Directory: {DMN_DIR}")
    print(f"🔗 Zeebe Gateway: {ZEEBE_HOST}:{ZEEBE_PORT}")
    print()

    try:
        # Create Zeebe client
        client = ZeebeClient(hostname=ZEEBE_HOST, port=ZEEBE_PORT)

        # Find all DMN files
        dmn_files = [f for f in os.listdir(DMN_DIR) if f.endswith('.dmn')]

        if not dmn_files:
            print("❌ No DMN files found!")
            return

        print(f"📋 Found {len(dmn_files)} DMN files:")
        for f in dmn_files:
            print(f"   • {f}")
        print()

        # Deploy each DMN file
        for dmn_file in dmn_files:
            file_path = os.path.join(DMN_DIR, dmn_file)

            try:
                print(f"⏳ Deploying {dmn_file}...", end=" ")

                # Read DMN XML
                with open(file_path, 'r') as f:
                    dmn_xml = f.read()

                # Deploy to Zeebe
                result = client.deploy_resource(file_path)

                print(f"✅ Deployed successfully!")

            except Exception as e:
                print(f"❌ Failed: {e}")

        print()
        print("🎉 Deployment complete!")
        print()
        print("📊 View your decisions in Camunda Operate:")
        print("   → http://localhost:8080")
        print()

    except Exception as e:
        print(f"❌ Error connecting to Zeebe: {e}")
        print()
        print("💡 Make sure Zeebe is running:")
        print("   docker-compose ps zeebe")
        print("   curl http://localhost:9600/ready")
        sys.exit(1)

if __name__ == "__main__":
    deploy_dmn_files()
