FROM python:3.11-slim

# Install system dependencies
RUN apt-get update -q \
  && apt-get install --no-install-recommends -qy \
  inetutils-ping \
  gcc \
  libc-dev \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /dashmachine

# Copy requirements first to leverage caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PRODUCTION=true
ENV PYTHONUNBUFFERED=1

EXPOSE 5000
VOLUME /dashmachine/dashmachine/user_data

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app" ]
