# 🕸️ Bubble.io Agency Scraper
Welcome to Bubble.io Agency Scraper—a flexible and customizable tool that extracts detailed information about agencies listed on Bubble.io. This script empowers you to effortlessly scrape data from multiple linked pages and save it to a Google Sheet. 🎉<br><br>
This project was inspired by Upwork posting, where I successfully scraped over **27 pages** of agency data from Bubble.io. Through this process, I gathered all the key information—starting from **Agency Name**, **Country**, and **Featured Works** to **External Profile Links**. This experience allowed me to refine the scraping process, ensuring the script is flexible and adaptable to future changes in the website structure.

By the end, I had built a robust solution that could handle future page expansions while maintaining data accuracy and organization.
<br><br>
<img width="956" alt="Screenshot 2024-09-26 204614" src="https://github.com/user-attachments/assets/fe63ed6e-38e0-4100-a27c-a008e366d44d">

## 🏃 Usage
1. Make sure your python is installed.
```bash
python --version

# Python 3.x.x
```
2. Build your python environment.
```bash
# Replace 'project_env' by your environment name specified
python -m venv project_env

# Install dependencies
pip install -r requirements.txt

# Activate your environment
# (Windows)
source project_env/Scripts/activate

# (Linux)
source project_env/bin/activate
```  
3. Start scraping 🎉
```bash
scrapy crawl bubble
```

## ✨ Tools
This project utilizes the following tools for efficient data extraction and processing:

* Selenium: For automating web browser interaction and handling dynamic content.
* Scrapy: A robust framework for building web scrapers and managing requests.
* Gspread: To connect between Python and Google Sheets for seamless data storage.

## 🙏 Acknowledgement
Thanks for checking out Bubble.io Agency Scraper. Feel free to reach out if you have questions, suggestions, or just want to chat about web scraping! 😊
