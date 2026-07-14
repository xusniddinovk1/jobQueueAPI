FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 'uv' paket menejerini rasmiy imijdan tezkor nusxalab olamiz
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Ba'zi kutubxonalar uchun kerak bo'lishi mumkin bo'lgan tizim paketlari
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bog'liqliklar fayllarini nusxalaymiz
COPY pyproject.toml uv.lock* ./

# Konteyner ichida .venv yaratib, barcha kutubxonalarni o'rnatamiz
RUN uv sync --frozen --no-cache

# Loyihaning qolgan qismini nusxalaymiz
COPY . /app/

EXPOSE 8000

# Production uchun FastAPI loyihasini uvicorn orqali ishga tushiramiz
# (Aytaylik, asosiy faylingiz 'main.py' va undagi FastAPI obyekti 'app' deb nomlangan)
CMD ["/app/.venv/bin/uvicorn", "appp.main:app", "--host", "0.0.0.0", "--port", "8000"]