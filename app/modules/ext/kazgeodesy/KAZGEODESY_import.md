# Импортирование данных Казгеодезии

## 1. Импортирование данных из shape файлов через QGIS

1. Открыть QGIS
2. Загрузить shape файлы как слои
3. Подключиться к базе данных
4. Импортировать данные из shape файлов в базу данных через QGIS посредством перетаскивания слоев из окна слоев в окно базы данных
5. Проверить результаты импортирования

## 2. Корректировка данных

```sql
-- OBLASTI
-- create primary key
ALTER TABLE geo."KAZGEODESY_RK_OBLASTI" DROP CONSTRAINT "KAZGEODESY_RK_OBLASTI_pkey";
ALTER TABLE geo."KAZGEODESY_RK_OBLASTI" ADD PRIMARY KEY (id);
ALTER TABLE geo."KAZGEODESY_RK_OBLASTI" DROP COLUMN IF EXISTS id_0 CASCADE;

-- RAIONY
-- remove duplicate ids
DELETE FROM geo."KAZGEODESY_RK_RAIONY" T1 USING geo."KAZGEODESY_RK_RAIONY" T2 WHERE T1.ctid < T2.ctid AND T1.id = T2.id;

-- remove empty ids
DELETE FROM geo."KAZGEODESY_RK_RAIONY" WHERE id IS NULL;

-- create primary key
ALTER TABLE geo."KAZGEODESY_RK_RAIONY" DROP CONSTRAINT "KAZGEODESY_RK_RAIONY_pkey";
ALTER TABLE geo."KAZGEODESY_RK_RAIONY" ADD PRIMARY KEY (id);
ALTER TABLE geo."KAZGEODESY_RK_RAIONY" DROP COLUMN IF EXISTS id_0 CASCADE;

-- create foreign key to OBLASTI
ALTER TABLE geo."KAZGEODESY_RK_RAIONY" ADD CONSTRAINT KAZGEODESY_RK_RAIONY_KAZGEODESY_RK_OBLASTI_id_fk
        FOREIGN KEY (parent_id) REFERENCES geo."KAZGEODESY_RK_OBLASTI" ON UPDATE CASCADE ON DELETE RESTRICT;
```
