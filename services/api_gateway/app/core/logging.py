import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import get_settings

settings = get_settings()

def setup_logging():
    """Настройка JSON-логирования с correlation ID."""
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    log_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.INFO)
    
    # Подавить лишние логи от библиотек
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)