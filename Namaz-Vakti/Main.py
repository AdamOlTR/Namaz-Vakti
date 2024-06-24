import subprocess
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os
import webbrowser
from colored import fg, attr

# Liste der erforderlichen Pakete
required_packages = [
    'requests',
    'beautifulsoup4',
    'pandas',
    'colored',
    'pytz'
]

# Funktion zur Installation von Paketen
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Installation der Pakete, falls sie nicht vorhanden sind
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install_package(package)

# Program to scrape Namaz times from the Diyanet website and display them in a browser
try:
    # URL for Dortmund on the Diyanet website
    full_url = "https://namazvakitleri.diyanet.gov.tr/tr-TR/10922/oberaden-icin-namaz-vakti"

    # Function to scrape Namaz times from the given URL
    def scrape_namaz_times(url):
        print(f"{fg('yellow')}Fetching Namaz times from URL: {url}{attr('reset')}")
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'class': 'table vakit-table'})
            
            if table is None:
                print(f"{fg('red')}Table not found on the page. Printing HTML for debugging.{attr('reset')}")
                print(soup.prettify())
                return None
            
            headers = [header.text.strip() for header in table.find_all('th')]
            rows = [[cell.text.strip() for cell in row.find_all('td')] for row in table.find_all('tr')[1:]]
            df = pd.DataFrame(rows, columns=headers)
            df.drop(columns=['Hicri Tarih'], inplace=True)
            print(f"{fg('green')}Table successfully scraped.{attr('reset')}")
            print(df.head())
            return df
        else:
            print(f"{fg('red')}Failed to retrieve the data. Status code: {response.status_code}{attr('reset')}")
            return None

    # Function to filter Namaz times for today's date
    def get_todays_namaz_times(df):
        today = datetime.today().strftime('%d %B %Y')
        today = today.replace("January", "Ocak").replace("February", "Şubat").replace("March", "Mart").replace("April", "Nisan") \
                    .replace("May", "Mayıs").replace("June", "Haziran").replace("July", "Temmuz").replace("August", "Ağustos") \
                    .replace("September", "Eylül").replace("October", "Ekim").replace("November", "Kasım").replace("December", "Aralık")
        print(f"{fg('yellow')}Filtering times for today: {today}{attr('reset')}")
        todays_times = df[df['Miladi Tarih'].str.contains(today)]
        if not todays_times.empty:
            print(f"{fg('green')}Today's times successfully filtered.{attr('reset')}")
            print(todays_times)
        else:
            print(f"{fg('red')}No times found for today: {today}{attr('reset')}")
        return todays_times

    # Scrape Namaz times and update HTML file content
    def update_namaz_times():
        df = scrape_namaz_times(full_url)
        if df is not None:
            todays_times = get_todays_namaz_times(df)
            if not todays_times.empty:
                html_file_path = "/home/oberadencamii/Namaz-Vakti/Namaz-Vakti/namaz_times.html"
                if not os.path.exists(html_file_path):
                    print(f"{fg('red')}HTML file not found: {html_file_path}{attr('reset')}")
                    return False
                with open(html_file_path, "r+", encoding="utf-8") as file:
                    html_content = file.read()
                    start_marker = "<!-- start of namaz times -->"
                    end_marker = "<!-- end of namaz times -->"
                    start = html_content.find(start_marker) + len(start_marker)
                    end = html_content.find(end_marker)
                    if start < len(start_marker) or end == -1:
                        print(f"{fg('red')}Markers not found in the HTML file.{attr('reset')}")
                        return False
                    print(f"{fg('yellow')}Updating HTML file with today's times.{attr('reset')}")
                    new_html = html_content[:start] + todays_times.to_html(index=False, border=0, classes='dataframe') + html_content[end:]
                    file.seek(0)
                    file.write(new_html)
                    file.truncate()
                print(f"{fg('green')}HTML file successfully updated.{attr('reset')}")
                return True
            else:
                print(f"{fg('red')}No data available for today{attr('reset')}")
                return False
        else:
            print(f"{fg('red')}No data available{attr('reset')}")
            return False

    # Function to open the browser and display the Namaz times
    def open_chrome():
        file_path = "/home/oberadencamii/Namaz-Vakti/Namaz-Vakti/namaz_times.html"
        webbrowser.open(f"file://{file_path}")

    # Main function
    def main():
        if update_namaz_times():
            open_chrome()

# Error handling
except Exception as e:
    print(f"{fg('red')}An error occurred: {e}{attr('reset')}")

except KeyboardInterrupt:
    print(f"{fg('red')}Program terminated{attr('reset')}")

except SystemExit:
    print(f"{fg('red')}Program terminated{attr('reset')}")

# Run the script
if __name__ == "__main__":
    main()
