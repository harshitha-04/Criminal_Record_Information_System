-- Drop the existing database if it exists
DROP DATABASE IF EXISTS criminal_record_db;

-- Create a new database
CREATE DATABASE criminal_record_db;

-- Use the newly created database
USE criminal_record_db;


-- Create Users table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Passwords should be hashed in a real application
    role ENUM('police', 'victim') NOT NULL
);

-- Create Victims table (assuming victims are stored separately from Users)
CREATE TABLE Victims (
    victim_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Create Cases table with a foreign key constraint to Victims table
CREATE TABLE Cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    case_type VARCHAR(50) NOT NULL,
    description TEXT,
    place VARCHAR(100) DEFAULT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    accused VARCHAR(100) DEFAULT NULL,
    victim_id INT,
    lawyer VARCHAR(100) DEFAULT NULL,
    police_id INT,
    case_status VARCHAR(20) DEFAULT 'Open',
    FOREIGN KEY (victim_id) REFERENCES Victims(victim_id) ON DELETE SET NULL,
    FOREIGN KEY (police_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

ALTER TABLE Cases
ADD COLUMN victim_name VARCHAR(100);


-- Create Complaints table with foreign key constraints to Cases and Users
CREATE TABLE Complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    description TEXT NOT NULL,
    complainant_name VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    filed_by INT,
    police_id INT,
    FOREIGN KEY (case_id) REFERENCES Cases(case_id) ON DELETE CASCADE,
    FOREIGN KEY (filed_by) REFERENCES Users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (police_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

-- Insert sample users (police and victims)
INSERT INTO Users (username, password, role) VALUES
('officer_john', 'password123', 'police'),
('officer_jane', 'password456', 'police'),
('victim_alex', 'password789', 'victim'),
('victim_sam', 'password012', 'victim');

-- Insert sample victims into Victims table (referencing Users table)
INSERT INTO Victims (user_id) VALUES
(3),  -- victim_alex
(4);  -- victim_sam

-- Insert sample cases
INSERT INTO Cases (case_type, description, place, accused, victim_id, lawyer, police_id) VALUES
('Theft', 'Description of the theft case', 'New York', 'John Doe', 1, 'Lawyer A', 1),
('Assault', 'Description of the assault case', 'Los Angeles', 'Jane Doe', 2, 'Lawyer B', 2);

-- Insert sample complaints for a case
INSERT INTO Complaints (case_id, description, filed_by, police_id) VALUES
(1, 'Complaint related to theft', 3, 1),
(2, 'Complaint related to assault', 4, 2);

-- Example of a nested query to fetch the username of the victim for the most recent case
SELECT username FROM Users WHERE user_id = (
    SELECT victim_id FROM Cases ORDER BY timestamp DESC LIMIT 1
);

-- Example of a join query to fetch cases and their complaints
SELECT c.case_id, c.case_type, co.description AS complaint_description
FROM Cases c
JOIN Complaints co ON c.case_id = co.case_id;

-- Example of an aggregate query to count cases handled by each police officer
SELECT police_id, COUNT(*) AS case_count
FROM Cases
GROUP BY police_id;

DESCRIBE Complaints;
ALTER TABLE Complaints
ADD COLUMN status VARCHAR(255) NOT NULL DEFAULT 'Pending';
ALTER TABLE Complaints
MODIFY COLUMN complaint_id INT AUTO_INCREMENT;
ALTER TABLE Complaints
MODIFY COLUMN case_id INT DEFAULT 1;

-- Modify the case_status column to remove the default value and make it manually entered
ALTER TABLE Cases
MODIFY COLUMN case_status VARCHAR(20) NOT NULL;

SELECT * from Victims;

DESCRIBE Cases;

SELECT * FROM VICTIMS;

SELECT TRIGGER_NAME
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'criminal_record_db';

desc cases;
ALTER TABLE Complaints
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE Complaints
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;


CREATE TABLE CaseHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES Cases(case_id)
);

select * from CaseHistory;

select * from victims;


INSERT INTO Users (username, password, role) VALUES
('officer_anuj', 'securepass5', 'police'),
('officer_pooja', 'securepass6', 'police'),
('victim_rahul', 'securepass7', 'victim'),
('victim_nisha', 'securepass8', 'victim'),
('officer_karan', 'securepass9', 'police'),
('officer_sneha', 'securepass10', 'police'),
('victim_vikram', 'securepass11', 'victim'),
('victim_rina', 'securepass12', 'victim'),
('officer_manish', 'securepass13', 'police'),
('officer_tanya', 'securepass14', 'police');

ALTER TABLE cases
MODIFY case_status VARCHAR(255) DEFAULT 'pending';


INSERT INTO Victims (user_id) VALUES
(1),  -- officer_anuj
(2),  -- officer_pooja
(3),  -- victim_rahul
(4),  -- victim_nisha
(5),  -- officer_karan
(6),  -- officer_sneha
(7),  -- victim_vikram
(8);  -- victim_rina

INSERT INTO Cases (case_type, description, place, accused, victim_id, lawyer, police_id) VALUES
('Fraud', 'Description of fraud case in Delhi', 'Delhi', 'Rajesh Sharma', 3, 'Lawyer E', 1),
('Cyber Crime', 'Description of cyber crime case in Bangalore', 'Bangalore', 'Suresh Reddy', 4, 'Lawyer F', 2),
('Murder', 'Description of murder case in Chennai', 'Chennai', 'Vikram Singh', 5, 'Lawyer G', 3),
('Kidnapping', 'Description of kidnapping case in Kolkata', 'Kolkata', 'Ravi Verma', 6, 'Lawyer H', 4),
('Extortion', 'Description of extortion case in Hyderabad', 'Hyderabad', 'Amit Kumar', 7, 'Lawyer I', 5),
('Terrorism', 'Description of terrorism case in Mumbai', 'Mumbai', 'Ajay Mehta', 8, 'Lawyer J', 6),
('Assault with Intent to Kill','Description of assault case in Pune','Pune','Deepak Joshi' ,7,'Lawyer K' ,7),
('Robbery with Violence','Description of robbery case in Ahmedabad','Ahmedabad','Nitin Yadav' ,8,'Lawyer L' ,8);

INSERT INTO Complaints (case_id, description, filed_by, police_id) VALUES
(1, 'Complaint related to fraud incident filed by victim_rahul.', 3, 1),
(2, 'Complaint related to cyber crime incident filed by victim_nisha.', 4, 2),
(3, 'Complaint related to murder incident filed by victim_vikram.', 5, 3),
(4, 'Complaint related to kidnapping incident filed by victim_rina.', 6, 4),
(5, 'Complaint related to extortion incident filed by officer_manish.', 7, 5),
(6, 'Complaint related to terrorism incident filed by officer_tanya.', 8, 6);
