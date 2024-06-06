## Dashboard Backend

### Prerequisites

1. Python version - 3.12
2. venv
3. MySql
4. Django - 5.0.1

### Setup Steps

1. Clone the repository:

    ```bash
    git clone {repo_url}
    ```
2. Create Virtual Environment:
    ```bash
    python -m venv {environment_name}
    ```
3. Activate Virtual Environment:
    - For Windows users:
      ```bash
      {environment_name}\Scripts\activate
      ```
    - For Linux and Mac users:
      ```bash
      source {environment_name}/bin/activate
      ```
4. Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Crete database and dedicated user for the project:
      ```bash
   #Log in to MySQL as root (replace 'root' with your MySQL username if different)
   mysql -u root -p
   
   # Enter your MySQL root password when prompted
   
   # Create a new database
   CREATE DATABASE {db_name};
   
   # Create a new user
   CREATE USER {user_name}@{host_name} IDENTIFIED BY {user_passward};
   
   # Grant privileges to the user for the database
   GRANT ALL PRIVILEGES ON {db_name}.* TO {user_name}@{host_name};
   
   # Flush privileges to apply changes
   FLUSH PRIVILEGES;
   
   # Exit MySQL
   EXIT;
   ```

6. Configure Environment Variables:
    - Replace the credentials in the `.env` file with your database credentials.

7. Database Migrations:
    ```bash
    # Create database migrations
    python manage.py makemigrations

    # Apply migrations to the database
    python manage.py migrate
    ```

8. Run Development Server:
    ```bash
    python manage.py runserver
    ```

### Additional Notes

- Make sure to replace `{environment_name}` with your desired name for the virtual environment.
- Ensure MySQL server is running before executing migration commands.