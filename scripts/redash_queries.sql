-- 1. Топ-10 курьеров по заработку (Bar Chart)
-- Анализ эффективности персонала: кто приносит больше всего выручки.
SELECT 
    c.name AS courier_name,
    c.transport_type,
    count(o.id) AS orders_delivered,
    round(sum(o.price)::numeric, 2) AS total_earned
FROM orders o
JOIN couriers c ON o.courier_id = c.id
GROUP BY c.id, c.name, c.transport_type
ORDER BY total_earned DESC
LIMIT 10;

-- 2. Средний чек и общая выручка по типам транспорта (Столбчатая диаграмма)
-- Показывает финансовую эффективность каждого вида доставки.
SELECT 
    c.transport_type,
    round(avg(o.price)::numeric, 2) AS avg_ticket,
    round(sum(o.price)::numeric, 2) AS total_revenue
FROM orders o
JOIN couriers c ON o.courier_id = c.id
GROUP BY c.transport_type
ORDER BY total_revenue DESC;

-- 3. Средняя дистанция и время доставки (Комбинированный график)
-- Проверка логики: насколько быстро разные типы транспорта преодолевают расстояние.
SELECT 
    c.transport_type,
    round(avg(o.distance_km)::numeric, 2) AS avg_distance_km,
    round(avg(extract(epoch from (o.finished_at - o.created_at))/60)::numeric, 2) AS avg_duration_minutes
FROM orders o
JOIN couriers c ON o.courier_id = c.id
GROUP BY c.transport_type;

-- 4. Топ-10 клиентов по количеству заказов и затратам (Таблица)
-- Анализ лояльности пользователей.
SELECT 
    cl.name AS client_name,
    count(o.id) AS total_orders,
    round(sum(o.price)::numeric, 2) AS total_spent
FROM orders o
JOIN clients cl ON o.client_id = cl.id
GROUP BY cl.id, cl.name
ORDER BY total_spent DESC
LIMIT 10;

-- 5. География заказов (Карта / Map)
-- Redash может визуализировать точки на карте Москвы.
SELECT 
    pickup_lat, 
    pickup_lon,
    delivery_lat,
    delivery_lon,
    price
FROM orders
WHERE status = 'delivered';
