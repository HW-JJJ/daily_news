from flask import Flask, render_template, request
import sqlite3
import time
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from gensim.summarization import summarize

# URL for news section
url = "https://news.naver.com/section/100"

# Setup Chrome options for headless mode
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = wb.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)

# Common function to create table if it doesn't exist
def create_table(db_name):
    conn = sqlite3.connect(db_name)
    curs = conn.cursor()
    
    # Table creation query
    sql = """
    CREATE TABLE IF NOT EXISTS contact(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        article TEXT,
        body TEXT
    )
    """
    curs.execute(sql)
    conn.commit()
    curs.close()
    conn.close()

# Function to insert data into the table
def insert_data(db_name, title, article, body):
    conn = sqlite3.connect(db_name)
    curs = conn.cursor()
    
    # Insert data query
    insert_sql = "INSERT INTO contact (title, article, body) VALUES (?, ?, ?)"
    curs.execute(insert_sql, (title, article, body))
    conn.commit()
    
    curs.close()
    conn.close()

# Function to summarize the article based on its length
def summarize_article(article_text):
    text_length = len(article_text)
    if text_length >= 1500:
        summary = summarize(article_text, 0.1)
    elif text_length >= 1400:
        summary = summarize(article_text, 0.11)
    elif text_length >= 1300:
        summary = summarize(article_text, 0.12)
    elif text_length >= 1200:
        summary = summarize(article_text, 0.13)
    elif text_length >= 1100:
        summary = summarize(article_text, 0.14)
    elif text_length >= 1000:
        summary = summarize(article_text, 0.15)
    elif text_length >= 900:
        summary = summarize(article_text, 0.16)
    elif text_length >= 750:
        summary = summarize(article_text, 0.2)
    elif text_length >= 500:
        summary = summarize(article_text, 0.3)
    elif text_length >= 200:
        summary = summarize(article_text, 0.5)
    else:
        summary = article_text
    return summary

# General function to collect articles from each section
def collect_articles(section_name, db_name, section_index, menu_index):
    # Data collection logic for different news sections
    try:
        section_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".Nlnb_menu_inner li:nth-child({menu_index}) span"))
        )
        section_button.click()

        # Clicking the headline banner
        headline_banner = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#newsct>div>div>a"))
        )
        headline_banner.click()

        # Collect the first 10 articles
        for i in range(10):
            try:
                news_title_button = driver.find_element(By.CSS_SELECTOR, f"#newsct div>ul>li:nth-child({i+1})>div>div a")
                news_title_button.click()
                time.sleep(2)
                
                # Collect the article content
                news_titles = driver.find_element(By.CSS_SELECTOR, "#title_area>span")
                news_title_text = news_titles.text
                
                article_body = driver.find_element(By.CSS_SELECTOR, "#dic_area")
                article_text = article_body.text
                summary = summarize_article(article_text)
                
                # Insert the data into the database
                insert_data(db_name, news_title_text, summary, article_text)
                
                # Go back to the news list
                driver.back()
                time.sleep(2)
            except Exception as e:
                print(f"Error in article {i+1}: {e}")
    except Exception as e:
        print(f"Error in {section_name} section: {e}")
    finally:
        print(f"Finished collecting articles for {section_name}")

# Main execution
def main():
    # List of sections to collect news from
    sections = [
        ("Politic", "politics.db", 2, 2),
        ("Economy", "economy.db", 3, 3),
        ("Society", "society.db", 4, 4),
        ("Culture", "culture.db", 5, 5),
        ("IT/Science", "it_science.db", 6, 6),
        ("World", "world.db", 7, 7)
    ]

    for section_name, db_name, section_index, menu_index in sections:
        # Create the table for each section
        create_table(db_name)
        # Collect articles for each section
        collect_articles(section_name, db_name, section_index, menu_index)
        time.sleep(5)

    # Close the driver after collecting all articles
    driver.quit()

# Run the main function
if __name__ == "__main__":
    main()

