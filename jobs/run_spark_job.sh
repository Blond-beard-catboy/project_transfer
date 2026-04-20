#!/bin/bash

# Скрипт для запуска Spark-джобы (локально или в среде с установленным spark-submit)
# Требуется наличие файла postgresql-42.6.0.jar в той же папке (или указать путь)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Путь к JAR-файлу драйвера PostgreSQL (скачать с https://jdbc.postgresql.org/download/)
POSTGRES_JAR="$SCRIPT_DIR/postgresql-42.6.0.jar"

if [ ! -f "$POSTGRES_JAR" ]; then
    echo "Ошибка: Файл $POSTGRES_JAR не найден. Скачайте PostgreSQL JDBC driver и положите в $SCRIPT_DIR"
    exit 1
fi

echo "Запуск Spark-джобы..."
spark-submit \
    --jars "$POSTGRES_JAR" \
    --master local[*] \
    spark_analytics_job.py

echo "Джоба завершена."