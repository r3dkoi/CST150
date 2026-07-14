# Setting up VS Code to communicate with MySQL

Steps taken to get VS Code able to run SQL queries against a local MySQL database.

- Downloaded MySQL Installer (web installer, `mysql-installer-web-community-8.0.46.0.msi`) from the official MySQL downloads page
- Ran the installer with Setup Type: **Server only**
- Configured server as:
  - Config Type: Development Computer
  - Connectivity: TCP/IP, Port 3306
  - Authentication Method: Use Strong Password Encryption (default, recommended)
  - Set and saved a root account password (no extra MySQL user accounts added)
  - Windows Service: configured as `MySQL80`, set to start at system startup, running under Standard System Account
  - Server file permissions: left as default (full access to service user + administrators only)
- Clicked Execute to install and start the MySQL Server service
- Verified the install by opening **MySQL 8.0 Command Line Client** from the Start Menu and logging in with the root password


- Installed VS Code extensions:
  - **SQLTools** (by Matheus Teixeira)
  - **SQLTools MySQL/MariaDB** driver (same author) — required for SQLTools to actually connect to MySQL
- Added a new connection in SQLTools:
  - Connection name: `restaurant_db`
  - Server Address: `localhost`
  - Port: `3306`
  - Database: `mysql` (system schema, used temporarily since `restaurant_db` didn't exist yet)
  - Username: `root`
  - Password mode: Ask upon connection
  - Authentication Protocol: default
  - SSL: Disabled
-
