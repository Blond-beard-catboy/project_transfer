#!/bin/bash

# Скрипт для автоматической загрузки PostgreSQL JDBC драйвера

JDBC_URL="https://jdbc.postgresql.org/download/postgresql-42.6.0.jar"
OUTPUT_FILE="postgresql-42.6.0.jar"

echo "Скачивание PostgreSQL JDBC драйвера с $JDBC_URL..."
curl -L -o "$OUTPUT_FILE" "$JDBC_URL"

if [ -f "$OUTPUT_FILE" ]; then
    echo "Драйвер успешно загружен: $OUTPUT_FILE"
else
    echo "Ошибка при загрузке драйвера. Попробуйте скачать вручную с $JDBC_URL"
    exit 1
fi