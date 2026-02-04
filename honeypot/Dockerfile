FROM python:3.11-slim

WORKDIR /app

# Install required Python dependency
RUN pip install --no-cache-dir paramiko

# Copy honeypot source files
COPY honeypot.py logger.py ./

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 22

CMD ["python", "-u", "honeypot.py"]
