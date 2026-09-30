CREATE DATABASE IF NOT EXISTS hostel_allocation;
USE hostel_allocation;

CREATE TABLE IF NOT EXISTS student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    gender VARCHAR(10),
    course VARCHAR(50),
    year INT,
    address VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS hostel (
    hostel_id INT PRIMARY KEY AUTO_INCREMENT,
    hostel_name VARCHAR(100) NOT NULL,
    hostel_type VARCHAR(20) NOT NULL,
    total_rooms INT NOT NULL,
    location VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS room (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    hostel_id INT NOT NULL,
    room_number VARCHAR(20) NOT NULL,
    capacity INT NOT NULL,
    occupied INT DEFAULT 0,
    room_status VARCHAR(20) DEFAULT 'Available',
    FOREIGN KEY (hostel_id) REFERENCES hostel(hostel_id)
);

CREATE TABLE IF NOT EXISTS application (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    hostel_id INT NOT NULL,
    application_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (hostel_id) REFERENCES hostel(hostel_id)
);

CREATE TABLE IF NOT EXISTS allocation (
    allocation_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    room_id INT NOT NULL,
    allocation_date DATE NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (room_id) REFERENCES room(room_id)
);

CREATE TABLE IF NOT EXISTS student_account (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);

CREATE TABLE IF NOT EXISTS admin_account (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO hostel (hostel_name, hostel_type, total_rooms, location)
SELECT 'Vardhaman Girls Hostel','Girls',50,'Campus'
WHERE NOT EXISTS (SELECT 1 FROM hostel WHERE hostel_name='Vardhaman Girls Hostel');

INSERT INTO hostel (hostel_name, hostel_type, total_rooms, location)
SELECT 'Vardhaman Boys Hostel','Boys',60,'Campus'
WHERE NOT EXISTS (SELECT 1 FROM hostel WHERE hostel_name='Vardhaman Boys Hostel');

INSERT INTO room (hostel_id, room_number, capacity, occupied, room_status)
SELECT hostel_id,'G101',3,0,'Available' FROM hostel
WHERE hostel_name='Vardhaman Girls Hostel'
AND NOT EXISTS (SELECT 1 FROM room WHERE room_number='G101');

INSERT INTO room (hostel_id, room_number, capacity, occupied, room_status)
SELECT hostel_id,'G102',3,0,'Available' FROM hostel
WHERE hostel_name='Vardhaman Girls Hostel'
AND NOT EXISTS (SELECT 1 FROM room WHERE room_number='G102');

INSERT INTO room (hostel_id, room_number, capacity, occupied, room_status)
SELECT hostel_id,'B101',3,0,'Available' FROM hostel
WHERE hostel_name='Vardhaman Boys Hostel'
AND NOT EXISTS (SELECT 1 FROM room WHERE room_number='B101');

INSERT INTO admin_account (name,email,password)
SELECT 'Hostel Admin','admin@hostel.com','Admin@123'
WHERE NOT EXISTS (SELECT 1 FROM admin_account WHERE email='admin@hostel.com');
