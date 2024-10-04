FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

ENV ROOT='/app'

# Install necessary packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    curl \
    nano \
    cmake \
    libboost-python-dev \
    libboost-thread-dev \
    python3-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    lshw \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . ${ROOT}

# Set working directory
WORKDIR ${ROOT}

# Upgrade pip and install requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Change permissions for scripts
RUN chmod +x run_ssl_proxy.sh && chmod +x install_ollama.sh

RUN ./install_ollama.sh

CMD ./run_ssl_proxy.sh & ollama serve & streamlit run app.py