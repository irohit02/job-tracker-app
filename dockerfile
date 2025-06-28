FROM python:3.11-slim

# Install dependencies
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Start the app using gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
