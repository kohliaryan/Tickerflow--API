FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir "uv>=0.4.0"

COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-install-project --no-cache

# --- MISSING LINE BELOW ---
# This adds the virtual environment to the system path
ENV PATH="/app/.venv/bin:$PATH"
# --------------------------

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]