import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file if exists
# This will not override existing environment variables
load_dotenv()

class NewsDatabase:
    def __init__(self):
        # Get database connection details from environment variables
        # Default values are already set in Dockerfile for containerized deployments
        self.host = os.environ.get('MYSQL_HOST', 'localhost')
        self.user = os.environ.get('MYSQL_USER', 'root')
        self.password = os.environ.get('MYSQL_PASSWORD', '')
        self.database = os.environ.get('MYSQL_DATABASE', 'news_agent')
        self.connection = None
        self.cursor = None
        
        print(f"Database configuration: host={self.host}, database={self.database}, user={self.user}")
        
    def connect(self):
        """Establish connection to the MySQL database"""
        try:
            # First try to connect with the database specified
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                self.cursor = self.connection.cursor(dictionary=True)
                print(f"Connected to existing database '{self.database}'")
            except mysql.connector.Error as err:
                # If database doesn't exist, connect without specifying database
                if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                    print(f"Database '{self.database}' does not exist, creating it...")
                    self.connection = mysql.connector.connect(
                        host=self.host,
                        user=self.user,
                        password=self.password
                    )
                    self.cursor = self.connection.cursor(dictionary=True)
                    
                    # Create the database
                    self.cursor.execute(f"CREATE DATABASE `{self.database}`")
                    print(f"Database '{self.database}' created successfully")
                    
                    # Use the database
                    self.cursor.execute(f"USE `{self.database}`")
                else:
                    # If it's another error, raise it
                    raise
            
            # Create tables if they don't exist
            self._create_tables()
            
            return True
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database: {err}")
            return False
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        # Articles table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            link VARCHAR(255) NOT NULL UNIQUE,
            date VARCHAR(100),
            region VARCHAR(100),
            tag VARCHAR(100),
            abstract TEXT,
            content LONGTEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # Events table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            link VARCHAR(255) NOT NULL UNIQUE,
            date VARCHAR(100),
            address TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        self.connection.commit()
    
    def article_exists(self, link):
        """Check if an article with the given link already exists in the database"""
        query = "SELECT id FROM articles WHERE link = %s"
        # Convert to string to handle _elementunicoderesult objects
        link_str = str(link) if link is not None else ""
        self.cursor.execute(query, (link_str,))
        return self.cursor.fetchone() is not None
    
    def event_exists(self, link):
        """Check if an event with the given link already exists in the database"""
        query = "SELECT id FROM events WHERE link = %s"
        # Convert to string to handle _elementunicoderesult objects
        link_str = str(link) if link is not None else ""
        self.cursor.execute(query, (link_str,))
        return self.cursor.fetchone() is not None
    
    def save_article(self, article):
        """Save an article to the database if it doesn't already exist"""
        link_str = str(article.get('link', '')) if article.get('link') is not None else ""
        if self.article_exists(link_str):
            # Article already exists, update it if needed
            return False
        
        query = """
        INSERT INTO articles (title, link, date, region, tag, abstract, content)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # Convert all values to strings to handle special objects
        values = (
            str(article.get('title', '')) if article.get('title') is not None else "",
            link_str,
            str(article.get('date', '')) if article.get('date') is not None else "",
            str(article.get('region', '')) if article.get('region') is not None else "",
            str(article.get('tag', '')) if article.get('tag') is not None else "",
            str(article.get('abstract', '')) if article.get('abstract') is not None else "",
            str(article.get('content', '')) if article.get('content') is not None else ""
        )
        
        self.cursor.execute(query, values)
        self.connection.commit()
        return True
    
    def save_event(self, event):
        """Save an event to the database if it doesn't already exist"""
        link_str = str(event.get('link', '')) if event.get('link') is not None else ""
        if self.event_exists(link_str):
            # Event already exists, update it if needed
            return False
        
        query = """
        INSERT INTO events (title, link, date, address, summary)
        VALUES (%s, %s, %s, %s, %s)
        """
        # Convert all values to strings to handle special objects
        values = (
            str(event.get('title', '')) if event.get('title') is not None else "",
            link_str,
            str(event.get('date', '')) if event.get('date') is not None else "",
            str(event.get('address', '')) if event.get('address') is not None else "",
            str(event.get('summary', '')) if event.get('summary') is not None else ""
        )
        
        self.cursor.execute(query, values)
        self.connection.commit()
        return True
    
    def get_articles(self, limit=100, region=None, tag=None):
        """Retrieve articles from the database with optional filtering"""
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if region:
            query += " AND region = %s"
            params.append(region)
        
        if tag:
            query += " AND tag = %s"
            params.append(tag)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_events(self, limit=100):
        """Retrieve events from the database"""
        query = "SELECT * FROM events ORDER BY created_at DESC LIMIT %s"
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
