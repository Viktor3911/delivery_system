import enum


class TransportType(str, enum.Enum):
    FOOT = "foot"       # Пеший
    BICYCLE = "bicycle" # Вело
    CAR = "car"         # Авто


class OrderStatus(str, enum.Enum):
    DELIVERED = "delivered"   # Успешная доставка
    CANCELLED = "cancelled"   # Клиент передумал или курьер не нашел адрес
