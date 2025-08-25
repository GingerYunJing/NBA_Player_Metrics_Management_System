# NBA Player Metrics Management System

### A full-stack web application for managing and querying NBA player data with a distributed database architecture

This project provides a modern web interface for user/admin to interact with NBA player statistics, draft information, and team data, complete with user authentication, player management tools, and real-time data querying capabilities.

## Features

- **Player Management**: View, add, edit, and delete NBA players
- **Real-time Statistics**: Current season player stats (2023-24)
- **Draft Information**: Comprehensive draft data from 2003-2025
- **Team Filtering**: Filter players by team
- **User Authentication**: Secure login/signup system
- **Player Following**: Follow/unfollow players
- **SQL Queries**: Execute custom SQL for data analysis
- **Role-based Access**: Public browsing, authenticated management






## Architecture

### System Architecture
This is a **full-stack web application** with three main layers:

1. **Frontend Layer**: HTML/CSS/JavaScript web interface
2. **Backend Layer**: Flask web server with business logic
3. **Database Layer**: Sharded MySQL databases

### Database Design
The system uses a **sharded MySQL database architecture** with two databases:
- **nba_0**: Stores data for teams with even team IDs
- **nba_1**: Stores data for teams with odd team IDs

### Database Schema
```sql
- all_draft_picks: Draft history and player selection data
- current_players: Active player roster and team information
- all_players_season_stats_2023_2024: Current season performance metrics
- player_info: Player biographical and physical information
- user_info: User authentication and account management
```

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: MySQL with SQLAlchemy Core (database connections) + Raw SQL queries
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login with password hashing
- **Data Collection**: NBA API integration
- **Data Processing**: Pandas for CSV manipulation and data sharding






## Project Structure

```
NBA_Player_Metrics_Management_System/
├── app.py                          # Main Flask application
├── schema.sql                      # Database schema definitions
├── insert_initial_data.py          # Database setup and data import
├── run-nbaplayer.sh                # Automated setup and run script
├── requirements.txt
├── README.md
│
├── Data_Collecting.ipynb          # NBA API data collection
├── Data_Sharding.ipynb            # Data distribution logic
│
├── Data/
│   ├── 0/
│   └── 1/
├── for_import_data/               # Processed data for import
│
├── templates/                     # HTML templates
│   ├── index.html                 # Main player listing page
│   ├── login.html                 # User authentication
│   ├── signup.html                # User registration
│   ├── player_stats.html          # Individual player statistics
│   └── query.html                 # SQL query interface
│
└── static/                        # CSS and static assets
    └── css/
        └── index_styles.css       # Main stylesheet
```







## Data Collection & Processing

### Data Sources
- **NBA API**: Official NBA statistics and player information
- **Draft History**: Comprehensive draft data from 2003-2025
- **Current Season Stats**: Real-time 2023-24 season performance data

### Data Processing Pipeline
1. **Data Collection** (`Data_Collecting.ipynb`):
   - Fetches data from NBA API endpoints
   - Processes and cleans raw data
   - Exports to CSV format

2. **Data Sharding** (`Data_Sharding.ipynb`):
   - Splits data based on team ID (even/odd)
   - Creates separate CSV files for each database shard
   - Ensures balanced data distribution

3. **Database Import** (`insert_initial_data.py`):
   - Creates database schemas
   - Imports sharded data into respective databases
   - Establishes foreign key relationships








## Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### Verify Prerequisites
```bash
which python
which pip
which mysql
```

### MySQL PATH Configuration
After installing MySQL, you may need to add the MySQL binary directory to your system PATH. Choose one of the following methods:

**Option 1: Permanent Configuration (Recommended)**
```bash
# Find your MySQL installation path (usually in /usr/local/)
ls /usr/local/mysql*

# Edit your shell configuration file
nano ~/.zshrc

# Add this line to the file (replace with your actual path):
export PATH="/usr/local/mysql-[version]-[os]-[arch]/bin:$PATH"

# Example for macOS:
export PATH="/usr/local/mysql-9.4.0-macos15-arm64/bin:$PATH"

# Save the file and restart your terminal
```

**Option 2: Temporary Configuration (Current Session Only)**
```bash
# Find your MySQL installation path
ls /usr/local/mysql*

# Add to PATH for current terminal session
export PATH="/usr/local/mysql-[version]-[os]-[arch]/bin:$PATH"

# Example for macOS:
export PATH="/usr/local/mysql-9.4.0-macos15-arm64/bin:$PATH"
```

### Installation Steps
```bash
git clone <repository-url>
cd NBA_Player_Metrics_Management_System
./run-nbaplayer.sh
```

The application will be available at `http://localhost:5000`














