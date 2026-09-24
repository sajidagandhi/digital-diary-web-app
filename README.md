📔 Digital Diary Web Application

A responsive and user-friendly "Digital Diary Web Application" built using "Python Flask and MySQL".
The application allows users to securely create diary entries, track their moods, manage daily tasks, and view their weekly mood analysis.

✨ Features

🔐 "User Authentication"

   User registration and login
   Password hashing for secure password storage
   Session-based authentication

📅 "Calendar-Based Diary"

   Select a date from the calendar
   Create and edit diary entries for specific dates
   Add a title, diary content, and mood

😊 "Mood Tracker"

   Record your mood with diary entries
   Weekly mood analysis
   Visual mood chart using Chart.js

✅ "To-Do List"

   Add daily tasks
   Mark tasks as completed
   Delete tasks

📊 "Dashboard"

   View recent diary entries
   View task summary
   Access diary, calendar, mood tracker, and to-do features

📱 "Responsive Design"

   Works on desktop and mobile screens
   Responsive sidebar navigation
   Mobile-friendly dashboard

🎨 "Modern UI"

   Blue-themed interface
   Clean dashboard layout
   Diary-inspired typography
   Smooth and simple writing experience

 🛠️ Technologies Used

 Frontend

 HTML5
 CSS3
 JavaScript
 Chart.js

 Backend

 Python
 Flask

 Database

 MySQL
 MySQL Connector/Python

 Security

 Werkzeug password hashing
 Session-based authentication
 Parameterized SQL queries

 📂 Project Structure

```text
digital-diary-web-app/
│
├── digital_diary_app.py
├── digital_diary_schema.sql
├── .gitignore
└── README.md
```

 ⚙️ Requirements

Make sure the following are installed:

 Python 3
 MySQL Server
 Git

Install the required Python packages:

```bash
python -m pip install flask mysql-connector-python werkzeug
```

 🗄️ Database Configuration

The application uses a MySQL database named:

```text
diary
```

The application creates the required database tables automatically when it starts.


 Windows Command Prompt

```cmd
set DIARY_DB_PASSWORD=your_mysql_password
```

Then start the application.

 ▶️ Running the Application

Open Command Prompt inside the project directory:

```cmd
cd digital-diary-web-app
```

Set your MySQL password:

```cmd
set DIARY_DB_PASSWORD=your_mysql_password
```

Run the application:

```cmd
python digital_diary_app.py
```

The application will start at:

```text
http://127.0.0.1:5000
```

Open the address in your web browser.

 📊 Main Modules

 1. Login & Signup

Users can create an account and securely log into the application.

 2. Dashboard

The dashboard provides quick access to diary entries, tasks, calendar features, and mood analysis.

 3. Diary

Users can select a date and write a diary entry containing:

 Title
 Diary content
 Mood

 4. Mood Analysis

The application records moods associated with diary entries and provides a weekly visual analysis.

 5. To-Do List

Users can create tasks, mark them as completed, and delete them when they are no longer needed.

 🔒 Security Notes

 Database credentials should never be committed to GitHub.
 The application uses password hashing instead of storing plain-text passwords.
 SQL queries use parameters to reduce the risk of SQL injection.
 Environment variables are used for sensitive database credentials.

🚀 Future Improvements

Possible future improvements include:

☁️ Cloud deployment
📧 Email-based password recovery
🔔 Task reminders and notifications
🌙 Dark mode
📈 More detailed mood statistics
🖼️ Image attachments for diary entries
📱 Progressive Web App support

Author
Sajida Gandhi
BCA Student

GitHub
[github.com/sajidagandhi](https://github.com/sajidagandhi)

