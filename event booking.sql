CREATE DATABASE event_system;

USE event_system;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100),
    event_date DATE,
    total_seats INT,
    available_seats INT
);

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    event_id INT,
    tickets INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Sample events
INSERT INTO events (event_name, event_date, total_seats, available_seats)
VALUES 
('Concert Night', '2026-05-10', 100, 100),
('Tech Conference', '2026-06-15', 200, 200),
('Comedy Show', '2026-05-25', 150, 150);

select * from  bookings;