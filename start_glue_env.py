# start_glue_env.py
import os
import subprocess
from pathlib import Path
import time

def start_glue_environment():
    # Create workspace directory
    workspace_dir = Path.cwd() / "glue_workspace"
    workspace_dir.mkdir(exist_ok=True)
    
    # Clean up any existing containers and images
    try:
        subprocess.run(["docker", "rm", "-f", "glue_dev"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "rmi", "-f", "glue-jupyter:local"], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    except Exception:
        pass

    try:
        print("\n🚀 Starting Glue development environment...")
        
        # Create a Dockerfile
        dockerfile_content = '''
FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

USER root

# Set environment variables
ENV PYTHONPATH=/home/glue_user/aws-glue-libs/PyGlue.zip:/home/glue_user/spark/python/lib/py4j-0.10.9-src.zip:/home/glue_user/spark/python/
ENV PATH="/usr/local/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and pip
RUN yum update -y && \\
    yum install -y python3 python3-pip && \\
    pip3 install --upgrade pip && \\
    pip3 install --no-cache-dir jupyter jupyterlab

# Set working directory
WORKDIR /home/glue_user/workspace

# Create jupyter config
RUN mkdir -p /root/.jupyter && \\
    echo "c.NotebookApp.allow_root = True" > /root/.jupyter/jupyter_notebook_config.py && \\
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \\
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \\
    echo "c.NotebookApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py && \\
    echo "c.NotebookApp.allow_origin = '*'" >> /root/.jupyter/jupyter_notebook_config.py

# Expose ports
EXPOSE 8888 4040

# Verify Python and Jupyter installation
RUN python3 -m jupyter --version

# Start Jupyter Lab
ENTRYPOINT ["python3", "-m", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
'''
        
        dockerfile_path = workspace_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        # Build the image
        print("\nBuilding Glue image (this might take a few minutes)...")
        subprocess.run([
            "docker", "build",
            "-t", "glue-jupyter:local",
            "-f", str(dockerfile_path),
            str(workspace_dir)
        ], check=True)

        # Start container
        print("\nStarting container...")
        cmd = [
            "docker", "run", "-d",
            "--name", "glue_dev",
            "-p", "8888:8888",
            "-p", "4040:4040",
            "-v", f"{workspace_dir.absolute()}:/home/glue_user/workspace",
            "glue-jupyter:local"
        ]
        
        container_id = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()

        print(f"Container ID: {container_id}")

        # Wait for container to initialize
        print("\nWaiting for container to initialize...")
        time.sleep(10)

        # Check container status
        container_status = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Status}}", "glue_dev"],
            capture_output=True,
            text=True
        ).stdout.strip()

        print(f"Container status: {container_status}")

        if container_status != "running":
            print("\n❌ Container failed to start properly")
            print("\nContainer logs:")
            subprocess.run(["docker", "logs", "glue_dev"])
            raise Exception("Container not running")

        # Wait for Jupyter to start
        print("\nWaiting for Jupyter Lab to start...", end="")
        max_retries = 30
        jupyter_ready = False
        
        for _ in range(max_retries):
            try:
                result = subprocess.run(
                    ["curl", "-s", "http://localhost:8888"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    jupyter_ready = True
                    print("\n✅ Jupyter Lab is ready!")
                    break
            except subprocess.CalledProcessError:
                pass
            print(".", end="", flush=True)
            time.sleep(2)

        if not jupyter_ready:
            print("\n❌ Jupyter Lab failed to start")
            print("\nContainer logs:")
            subprocess.run(["docker", "logs", "glue_dev"])
            raise Exception("Jupyter Lab not responding")

        # Create a sample notebook
        sample_notebook = workspace_dir / "welcome.ipynb"
        notebook_content = '''{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import sys\\n",
    "print(f\\"Python version: {sys.version}\\")\\n\\n",
    "try:\\n",
    "    from pyspark.context import SparkContext\\n",
    "    from awsglue.context import GlueContext\\n",
    "    from awsglue.job import Job\\n",
    "    \\n",
    "    # Initialize Glue context\\n",
    "    sc = SparkContext()\\n",
    "    glueContext = GlueContext(sc)\\n",
    "    spark = glueContext.spark_session\\n",
    "    job = Job(glueContext)\\n",
    "    \\n",
    "    print(\\"✨ Glue environment initialized successfully!\\")\\n",
    "except Exception as e:\\n",
    "    print(f\\"Error initializing Glue environment: {e}\\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}'''
        sample_notebook.write_text(notebook_content)

        print("\n✨ Glue development environment started successfully!")
        print("\n📓 Access Jupyter Lab at: http://localhost:8888")
        print("📊 Access Spark UI at: http://localhost:4040")
        print(f"📂 Workspace directory: {workspace_dir.absolute()}")
        print("\nℹ️  A sample notebook 'welcome.ipynb' has been created in your workspace")
        
        # Show container status and logs
        print("\n📋 Container status:")
        subprocess.run(["docker", "ps", "--filter", "name=glue_dev"])
        
        print("\n📋 Container logs:")
        subprocess.run(["docker", "logs", "glue_dev"])
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting Glue environment: {e}")
        print("\nContainer logs:")
        subprocess.run(["docker", "logs", "glue_dev"])
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\nContainer logs:")
        subprocess.run(["docker", "logs", "glue_dev"])

if __name__ == "__main__":
    start_glue_environment()
