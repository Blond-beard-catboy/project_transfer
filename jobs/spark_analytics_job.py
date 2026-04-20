from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, when, year, month, to_date

def main():
    # JDBC URLs
    ORDER_DB_URL   = "jdbc:postgresql://127.0.0.1:5432/order_db"
    PAYMENT_DB_URL = "jdbc:postgresql://127.0.0.1:5432/payment_db"
    ROUTE_DB_URL   = "jdbc:postgresql://127.0.0.1:5432/route_db"
    USER_DB_URL    = "jdbc:postgresql://127.0.0.1:5432/user_db"

    PROPS = {
        "user": "postgres",
        "password": "postgres",
        "driver": "org.postgresql.Driver"
    }

    spark = SparkSession.builder \
        .appName("FreightAnalytics") \
        .config("spark.master", "local[*]") \
        .config("spark.driver.host", "localhost") \
        .config("spark.driver.port", "0") \
        .config("spark.ui.enabled", "false") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.jars", "postgresql-42.6.0.jar") \
        .getOrCreate()

    # Чтение таблиц
    orders   = spark.read.jdbc(url=ORDER_DB_URL,   table="orders",   properties=PROPS)
    payments = spark.read.jdbc(url=PAYMENT_DB_URL, table="payments", properties=PROPS)
    routes   = spark.read.jdbc(url=ROUTE_DB_URL,   table="routes",   properties=PROPS)
    users    = spark.read.jdbc(url=USER_DB_URL,    table="users",    properties=PROPS)

    # Переименовываем id в orders, чтобы избежать конфликта с payments.id
    orders = orders.withColumnRenamed("id", "order_id")

    # Добавляем год и месяц из даты создания
    orders_with_date = orders.withColumn("order_date", to_date(col("created_at"))) \
        .withColumn("year", year("order_date")) \
        .withColumn("month", month("order_date"))

    # Объединяем заказы с платежами (используем переименованный столбец order_id)
    monthly = orders_with_date.join(payments, orders_with_date.order_id == payments.order_id, "left") \
    .groupBy("year", "month") \
    .agg(sum("amount").alias("revenue"), count("*").alias("orders_count"))

    # Прогноз на следующий месяц (простая экстраполяция)
    monthly.createOrReplaceTempView("monthly")
        # Упрощённый прогноз: среднее значение за последние 3 месяца
    forecast = spark.sql("""
        SELECT 
            MAX(year) + 1 AS forecast_year,
            MAX(month) + 1 AS forecast_month,
            AVG(revenue) AS forecast_revenue
        FROM monthly
        WHERE (year, month) IN (
            SELECT year, month FROM monthly
            ORDER BY year DESC, month DESC
            LIMIT 3
        )
    """)
    forecast.write.mode("overwrite").jdbc(url=ORDER_DB_URL, table="dm_profit_forecast", properties=PROPS)

    # Порожние маршруты (без заказа)
    empty_runs = routes.filter(col("order_id").isNull()) \
        .withColumn("day", to_date(col("created_at"))) \
        .groupBy("day") \
        .count() \
        .withColumnRenamed("count", "empty_runs")
    empty_runs.write.mode("append").jdbc(url=ORDER_DB_URL, table="dm_empty_runs", properties=PROPS)

    # Рейтинг водителей (если есть данные)
    if "driver_id" in orders.columns and "amount" in payments.columns:
        driver_stats = orders.join(payments, orders.order_id == payments.order_id, "left") \
            .groupBy("driver_id") \
            .agg(
                count("*").alias("total_orders"),
                sum("amount").alias("total_profit")
            ) \
            .withColumn("rating", col("total_orders") * 10 + col("total_profit") / 1000)
        driver_stats.write.mode("overwrite").jdbc(url=ORDER_DB_URL, table="dm_driver_rating", properties=PROPS)
    else:
        print("Таблица orders не содержит driver_id или payments не содержит amount, пропускаем dm_driver_rating.")

    spark.stop()
    print("Spark job completed successfully.")

if __name__ == "__main__":
    main()