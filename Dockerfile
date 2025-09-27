# Pull base image
FROM python:3.12-slim-bullseye

RUN apt-get update \
    && apt-get install -y netcat supervisor build-essential python3-dev \
    && useradd -m -s /bin/bash appuser # Add appuser

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Set work directory
WORKDIR $APP_HOME

# Install dependencies
COPY requirements/requirements.txt requirements/requirements.txt
RUN python -m pip install --upgrade uv pip wheel
RUN python -m uv pip install -r requirements/requirements.txt

# Copy project
COPY . .

# Ensure appuser has ownership of the application directory
RUN chown -R appuser:appuser $APP_HOME

# # Copy supervisord configuration
# COPY deploy/supervisor_scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# COPY deploy/supervisor_scripts/celery_supervisord.conf /etc/supervisor/conf.d/celery_supervisord.conf
# COPY deploy/supervisor_scripts/uvicorn_supervisord.conf /etc/supervisor/conf.d/uvicorn_supervisord.conf
# COPY deploy/supervisor_scripts/dramatiq_supervisord.conf /etc/supervisor/conf.d/dramatiq_supervisord.conf

# # Change permissions for deploy folder scripts
RUN sed -i 's/\r$//g' /app/deploy/*.sh
RUN chmod +x /app/deploy/*.sh


# Ensure that supervisord runs as appuser and log directories are owned by appuser
# RUN mkdir -p /var/log/supervisor \
#     && chown -R appuser:appuser /var/log/supervisor

# RUN mkdir -p /app/tmp/logs \
#     && chown -R appuser:appuser /app/tmp/logs \
#     && touch /app/tmp/logs/service.log \
#     && chown appuser:appuser /app/tmp/logs/service.log

# Switch to appuser to run the container
USER appuser

EXPOSE 8000

# Run the application
CMD ["/app/deploy/uvicorn_start.sh"]
