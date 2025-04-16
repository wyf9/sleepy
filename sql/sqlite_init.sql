CREATE TABLE IF NOT EXISTS Events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    show_name TEXT,
    app_name  TEXT NOT NULL,
    [using]   BOOLEAN NOT NULL,
    start_time DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS ColorGroup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    color_hex TEXT NOT NULL DEFAULT '#a0ad9e',
    [set] INTEGER DEFAULT 0
)

-- INSERT INTO Events (device_id,show_name,app_name,[using],start_time) VALUES ('test_device','手机','哔哩哔哩',true,'2025-4-5 11:00:00')