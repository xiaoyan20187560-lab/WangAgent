import sqlite3

conn = sqlite3.connect(r"E:\PYCHAMxuexilaji\BuAgent\build_harness\test.db")
print("SQLite连接成功")
conn.close()