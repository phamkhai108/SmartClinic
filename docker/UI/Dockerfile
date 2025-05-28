FROM python:3.12-slim

WORKDIR /app/ui

# Copy thư mục UI vào /app/ui trong container
COPY UI ./ui

WORKDIR /app/ui

# Expose port 5000
EXPOSE 5000

# Chạy python HTTP server trên cổng 5000
CMD ["python", "-m", "http.server", "5000"]
