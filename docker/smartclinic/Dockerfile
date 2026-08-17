FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN pip install uv
ENV PATH="/root/.cargo/bin:$PATH"

# COPY . .
COPY ../../ ./

RUN uv sync
RUN uv pip install tensorflow

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.smartclinic.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
