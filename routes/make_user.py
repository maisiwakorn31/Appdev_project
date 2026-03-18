import sqlite3

# เชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect("users.db")
cur = conn.cursor()

# กำหนดชื่อคนที่ต้องการเปลี่ยนสิทธิ์กลับเป็น User
my_name = "nutthapol bovaree" 

# สั่งอัปเดตตาราง users ให้ role เป็น 'user' เฉพาะคนที่มี fullname ตรงกับ my_name
cur.execute("UPDATE users SET role = 'user' WHERE fullname = ?", (my_name,))

# บันทึกและปิดการเชื่อมต่อ
conn.commit()
conn.close()

print(f"เปลี่ยนสิทธิ์ให้คุณ {my_name} กลับเป็น User สำเร็จแล้ว!")