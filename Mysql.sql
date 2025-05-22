use nisha;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL
);
CREATE TABLE career_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    interest TEXT,
    skills TEXT,
    goal TEXT,
    role VARCHAR(100)
);
CREATE TABLE career_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    career_goal TEXT
);
select*from users;
select*from career_data;
select*from career_info;
DROP TABLE career_info;
ALTER TABLE users ADD COLUMN profile_pic VARCHAR(255);
CREATE TABLE career_suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    interest TEXT,
    skills TEXT,
    goal TEXT,
    suggestion TEXT
);
ALTER TABLE users ADD role VARCHAR(10) DEFAULT 'user';
UPDATE users SET role='admin' WHERE username='Nisha_yadav';
select username, role from users;
SET SQL_SAFE_UPDATES = 0;
UPDATE users SET role='admin' WHERE username='Nisha_yadav';
SET SQL_SAFE_UPDATES = 1;
ALTER TABLE users ADD COLUMN gender VARCHAR(10);
select* from user;
DESCRIBE users;
SHOW DATABASES;
ALTER TABLE users 
ADD COLUMN gender VARCHAR(10),
ADD COLUMN profile_pic VARCHAR(50);
ALTER TABLE career_data ADD COLUMN career_field VARCHAR(100);
SELECT career_field, COUNT(*) FROM career_data GROUP BY career_field;
CREATE TABLE profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100),
    email VARCHAR(100),
    address VARCHAR(255),
    skills TEXT
);
ALTER TABLE profiles ADD COLUMN address VARCHAR(255);
ALTER TABLE profiles ADD COLUMN skills TEXT;
select *from profiles;
drop table profiles;

