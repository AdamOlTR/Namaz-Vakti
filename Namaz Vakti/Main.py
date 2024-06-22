import subprocess
import sys

# Liste der erforderlichen Pakete
required_packages = [
    'requests',
    'beautifulsoup4',
    'pandas',
    'colored'
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

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import webbrowser
import os
from threading import Thread
from colored import fg, attr  # Importing colored module for colored output

# Program to scrape Namaz times from the Diyanet website and display them in a browser
try:
    # URL for Dortmund on the Diyanet website
    full_url = "https://namazvakitleri.diyanet.gov.tr/tr-TR/10922/oberaden-icin-namaz-vakti"

    # Function to scrape Namaz times from the given URL
    def scrape_namaz_times(url):
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
            return df
        else:
            print(f"{fg('red')}Failed to retrieve the data. Status code: {response.status_code}{attr('reset')}")
            return None

    # Function to filter Namaz times for today's date
    def get_todays_namaz_times(df):
        today = datetime.today().strftime('%d %B %Y')  # Get today's date in the format 'DD Month YYYY'
        today = today.replace("January", "Ocak").replace("February", "Şubat").replace("March", "Mart").replace("April", "Nisan") \
                    .replace("May", "Mayıs").replace("June", "Haziran").replace("July", "Temmuz").replace("August", "Ağustos") \
                    .replace("September", "Eylül").replace("October", "Ekim").replace("November", "Kasım").replace("December", "Aralık")
        todays_times = df[df['Miladi Tarih'].str.contains(today)]
        if not todays_times.empty:
            print(f"{fg('green')}Today's times successfully filtered.{attr('reset')}")
        return todays_times

    # Function to get the next prayer time
    def get_next_prayer_time(todays_times):
        now = datetime.now()
        prayer_times = []

        for time_str in todays_times.iloc[0, 1:]:  # Skip the first column with the date
            prayer_time = datetime.strptime(time_str, '%H:%M').replace(year=now.year, month=now.month, day=now.day)
            if prayer_time < now:
                prayer_time += timedelta(days=1)  # Move to the next day if the time has already passed
            prayer_times.append(prayer_time)

        next_prayer_time = min(prayer_times)
        print(f"Current time: {now}")
        print(f"Next prayer time: {next_prayer_time}")
        return next_prayer_time

    # Scrape Namaz times and update HTML file content
    def update_namaz_times():
        df = scrape_namaz_times(full_url)
        if df is not None:
            todays_times = get_todays_namaz_times(df)
            if not todays_times.empty:
                next_prayer_time = get_next_prayer_time(todays_times).strftime('%Y-%m-%dT%H:%M:%S')
                with open("namaz_times.html", "r+", encoding="utf-8") as file:
                    html_content = file.read()
                    start_marker = "<!-- start of namaz times -->"
                    end_marker = "<!-- end of namaz times -->"
                    start = html_content.find(start_marker) + len(start_marker)
                    end = html_content.find(end_marker)
                    if start < len(start_marker) or end == -1:
                        print(f"{fg('red')}Markers not found in the HTML file.{attr('reset')}")
                        return False
                    new_html = html_content[:start] + todays_times.to_html(index=False, border=0, classes='dataframe') + html_content[end:]
                    new_html = new_html.replace('<span id="next-prayer-time" data-time=""></span>', f'<span id="next-prayer-time" data-time="{next_prayer_time}"></span>')
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

    # Function to periodically update Namaz times
    def periodic_update():
        while True:
            update_namaz_times()
            time.sleep(60)  # Wait for 1 minute before updating again

    # Open Chrome and display the Namaz times
    def open_chrome():
        file_path = os.path.abspath("namaz_times.html")
        webbrowser.open(f"file://{file_path}")

    # Main function to start threads for updating and opening browser
    def main():
        update_thread = Thread(target=periodic_update)
        update_thread.start()
        
        # Open the browser once
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
