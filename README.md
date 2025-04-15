# 🔒 Criminal Record Management System

A Python-based Criminal Record Management System with a user-friendly GUI built using Tkinter and a MySQL backend. The system supports role-based access for Police and Victims, facilitating case tracking, complaint filing, data visualization, and audit logging through triggers.

## ✨ Key Features

### 🔐 User Authentication
- Secure login with username and password verification
- Role-specific dashboards: Police and Victim

### 🕵️ Police Dashboard
- Add, update, and monitor case details
- File and handle complaints efficiently
- View pending and unresolved cases
- Generate visual data insights using bar graphs (via matplotlib)

### 🙍 Victim Dashboard
- Access personal case and complaint records in a dedicated view

### 🧮 Robust Database Operations
- Nested joins and aggregation queries for detailed case-complaint mapping
- MySQL triggers for maintaining an audit trail on case status changes
- Stored procedures to streamline complaint submissions

## ⚙️ Installation Guide

### 📋 Prerequisites
- Python 3.x
- MySQL Server
- Required Python packages:
  - `tkinter`
  - `mysql-connector-python`
  - `matplotlib`

### 🧰 Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone https://github.com/harshitha-04/Criminal_Record_Information_System.git
   cd Criminal_Record_Information_System
   ```

2. **Install Dependencies**
   ```bash
   pip install mysql-connector-python matplotlib
   ```

3. **Database Configuration**
   - Create a MySQL database named `criminal_record_db`
   - Update the `db_config` dictionary in the code with your MySQL credentials:
     ```python
     db_config = {
       'host': 'localhost',
       'user': 'your_mysql_username',
       'password': 'your_mysql_password',
       'database': 'criminal_record_db'
     }
     ```

4. **Import Schema**
   - Run the following command to import database tables:
     ```bash
     mysql -u root -p criminal_record_db < schema.sql
     ```

5. **Launch the Application**
   ```bash
   python codes.py
   ```

## 🗂️ Database Schema

### Tables Overview:
- **Users**: Holds user credentials and role information
- **Cases**: Contains records of various cases with descriptions and statuses
- **Complaints**: Tracks complaints filed and links them to corresponding cases
- **CaseHistory**: Maintains a record of status updates via triggers

## 🧱 Code Structure
- **HomePage**: Application's welcome screen
- **LoginWindow**: User login interface
- **PoliceDashboard**: Feature-rich dashboard for police users
- **VictimDashboard**: Personalized view for victims
- **ComplaintManagement**: Handles all complaint-related operations
- **Trigger**: MySQL trigger for monitoring case status changes
- **Stored Procedure**: Automates complaint entries

## 📊 Visual Insights
- The system uses `matplotlib` to present:
  - Bar charts displaying the distribution and status of cases for a quick overview

---
Built for a streamlined and secure management of criminal records with enhanced visibility and accountability.

