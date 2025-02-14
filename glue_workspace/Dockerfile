
FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01

USER root

# Set environment variables
ENV PYTHONPATH=/home/glue_user/aws-glue-libs/PyGlue.zip:/home/glue_user/spark/python/lib/py4j-0.10.9-src.zip:/home/glue_user/spark/python/
ENV PATH="/usr/local/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and pip
RUN yum update -y && \
    yum install -y python3 python3-pip && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir jupyter jupyterlab

# Set working directory
WORKDIR /home/glue_user/workspace

# Create jupyter config
RUN mkdir -p /root/.jupyter && \
    echo "c.NotebookApp.allow_root = True" > /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_origin = '*'" >> /root/.jupyter/jupyter_notebook_config.py

# Expose ports
EXPOSE 8888 4040

# Verify Python and Jupyter installation
RUN python3 -m jupyter --version

# Start Jupyter Lab
ENTRYPOINT ["python3", "-m", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
