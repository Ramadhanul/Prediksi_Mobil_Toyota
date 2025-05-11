import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import re

# Setup Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")

# Setup WebDriver
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# Base URL tanpa nomor halaman
base_url = "https://www.mobil123.com/mobil-bekas-dijual/toyota/indonesia?min_year=2005&max_year=2025&page_size=25&page_number="

# Simpan hasil semua halaman
data_mobil = []

# Jumlah total halaman (bisa diubah sesuai kebutuhan)
total_pages = 1064

for page in range(1, total_pages + 1):
    print(f"Memproses halaman {page}...")
    url = base_url + str(page)
    
    try:
        driver.get(url)
        time.sleep(2)  # tunggu agar halaman bisa dimuat

        soup = BeautifulSoup(driver.page_source, "html.parser")
        articles = soup.find_all("article", class_="listing")

        for article in articles:
            title_tag = article.find("h2", class_="listing__title")
            a_tag = title_tag.find("a") if title_tag else None

            # Judul & Link
            title = a_tag.get_text(strip=True) if a_tag else "N/A"
            link = a_tag["href"] if a_tag and a_tag.has_attr("href") else "N/A"

            # Harga
            price_tag = article.find("div", class_="listing__price")
            price = price_tag.get_text(strip=True) if price_tag else "N/A"

            # Tahun dari judul
            match = re.match(r"(\d{4})", title)
            tahun = match.group(1) if match else "N/A"

            data_mobil.append({
                "Judul": title,
                "Harga": price,
                "Tahun": tahun,
                "Link": link
            })

    except Exception as e:
        print(f"Gagal memproses halaman {page}: {e}")
        continue

# Tutup browser
driver.quit()

# Convert dan simpan
df = pd.DataFrame(data_mobil)
df.to_csv("data_mobil_toyota_semua_halaman.csv", index=False)
print("Selesai! Data disimpan ke 'data_mobil_toyota_semua_halaman.csv'")
