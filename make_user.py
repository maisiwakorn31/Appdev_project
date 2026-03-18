import sqlite3

# เชื่อมต่อกับฐานข้อมูล
conn = sqlite3.connect("users.db")
cur = conn.cursor()

# กำหนดชื่อที่คุณต้องการให้เป็น Admin (พิมพ์ให้ตรงกับที่สมัครไว้เป๊ะๆ นะครับ)
my_name = "nutthapol bovaree" 

# สั่งอัปเดตตาราง users ให้ role เป็น 'admin' เฉพาะคนที่มี fullname ตรงกับ my_name
cur.execute("UPDATE users SET role = 'admin' WHERE fullname = ?", (my_name,))

# บันทึกและปิดการเชื่อมต่อ
conn.commit()
conn.close()

print(f"เปลี่ยนสิทธิ์ให้คุณ {my_name} เป็น Admin สำเร็จแล้ว!")