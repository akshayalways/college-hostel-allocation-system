COLLEGE HOSTEL ALLOCATION SYSTEM

1. Open app.py and replace YOUR_MYSQL_PASSWORD with your local MySQL root password.
2. If your database/tables already exist, you can use them directly.
3. Run database/schema.sql in MySQL to create any missing tables and sample hostels/rooms/admin.
4. Install packages:
   py -m pip install -r requirements.txt
5. Start:
   py app.py
6. Open:
   http://127.0.0.1:5000/

Student:
- Register: /register
- Login: /login
- Dashboard: /dashboard
- Apply for hostel from the dashboard

Admin:
- Login: /admin/login
- Default admin email: admin@hostel.com
- Default admin password: Admin@123

NOTE:
This is a course project starter. Passwords are kept simple to match the existing beginner DBMS setup. For a production system, use password hashing and environment variables.
