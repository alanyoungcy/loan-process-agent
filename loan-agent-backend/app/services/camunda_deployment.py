"""
Camunda/Zeebe Deployment Service
Deploy BPMN and DMN files to Camunda 8 via zbctl and save to filesystem
"""
import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CamundaDeploymentService:
    """Service for deploying workflows and decisions to Camunda 8"""

    def __init__(self):
        self.zeebe_address = "localhost:26500"
        # Paths to save deployed files
        self.deployments_dir = "/Volumes/Orico/code/capco/loan-agent/camunda-deployments"
        self.frontend_workflows_dir = "/Volumes/Orico/code/capco/loan-agent/loan-agent-frontend/public/workflows"

    async def deploy_bpmn(self, name: str, bpmn_xml: str) -> Dict[str, Any]:
        """
        Deploy BPMN workflow to Camunda 8 using zbctl and save to filesystem

        Args:
            name: Name for the workflow file
            bpmn_xml: BPMN XML content

        Returns:
            Dict with deployment result
        """
        try:
            # Clean filename
            filename = f"{name}.bpmn" if not name.endswith('.bpmn') else name

            # Create temp file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.bpmn',
                delete=False,
                prefix=f'{name}_'
            ) as f:
                f.write(bpmn_xml)
                temp_file = f.name

            try:
                # Deploy using zbctl
                result = subprocess.run(
                    ['zbctl', 'deploy', temp_file,
                     '--address', self.zeebe_address,
                     '--insecure'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Deployment successful - save to both locations for sync
                    try:
                        # Save to camunda-deployments/
                        deployments_path = os.path.join(self.deployments_dir, filename)
                        with open(deployments_path, 'w') as f:
                            f.write(bpmn_xml)
                        logger.info(f"Saved BPMN to {deployments_path}")

                        # Save to frontend/public/workflows/ for editor access
                        frontend_path = os.path.join(self.frontend_workflows_dir, filename)
                        with open(frontend_path, 'w') as f:
                            f.write(bpmn_xml)
                        logger.info(f"Saved BPMN to {frontend_path}")

                    except Exception as save_err:
                        logger.warning(f"Deployed to Camunda but failed to save to disk: {save_err}")

                    logger.info(f"Successfully deployed BPMN: {name}")
                    return {
                        "success": True,
                        "message": f"Successfully deployed {name} to Camunda and saved to filesystem",
                        "output": result.stdout
                    }
                else:
                    logger.error(f"Failed to deploy BPMN: {result.stderr}")
                    return {
                        "success": False,
                        "error": result.stderr
                    }

            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        except Exception as e:
            logger.error(f"Error deploying BPMN: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def deploy_dmn(self, name: str, dmn_xml: str) -> Dict[str, Any]:
        """
        Deploy DMN decision to Camunda 8 using zbctl and save to filesystem

        Args:
            name: Name for the decision file
            dmn_xml: DMN XML content

        Returns:
            Dict with deployment result
        """
        try:
            # Clean filename
            filename = f"{name}.dmn" if not name.endswith('.dmn') else name

            # Create temp file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.dmn',
                delete=False,
                prefix=f'{name}_'
            ) as f:
                f.write(dmn_xml)
                temp_file = f.name

            try:
                # Deploy using zbctl
                result = subprocess.run(
                    ['zbctl', 'deploy', temp_file,
                     '--address', self.zeebe_address,
                     '--insecure'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Deployment successful - save to both locations for sync
                    try:
                        # Save to camunda-deployments/
                        deployments_path = os.path.join(self.deployments_dir, filename)
                        with open(deployments_path, 'w') as f:
                            f.write(dmn_xml)
                        logger.info(f"Saved DMN to {deployments_path}")

                        # Save to frontend/public/workflows/ for editor access
                        frontend_path = os.path.join(self.frontend_workflows_dir, filename)
                        with open(frontend_path, 'w') as f:
                            f.write(dmn_xml)
                        logger.info(f"Saved DMN to {frontend_path}")

                    except Exception as save_err:
                        logger.warning(f"Deployed to Camunda but failed to save to disk: {save_err}")

                    logger.info(f"Successfully deployed DMN: {name}")
                    return {
                        "success": True,
                        "message": f"Successfully deployed {name} to Camunda and saved to filesystem",
                        "output": result.stdout
                    }
                else:
                    logger.error(f"Failed to deploy DMN: {result.stderr}")
                    return {
                        "success": False,
                        "error": result.stderr
                    }

            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

        except Exception as e:
            logger.error(f"Error deploying DMN: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
camunda_deployment = CamundaDeploymentService()
