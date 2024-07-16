import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk, UnidentifiedImageError
import time
import logging

class NamazVaktiApp:
    def __init__(self, root):
        # Anpassbare Variablen
        self.config = {
            "background_image_path": r"D:\Code\Namaz_Vakti\camii.jpg",
            "fullscreen": True,
            "city_name": "Oberaden",
            "city_id": "10922/oberaden-icin-namaz-vakti",
            "label_font": ('Helvetica', 18, 'bold'),
            "label_background": "#4682B4",
            "label_foreground": "#ffffff",
            "city_label_font": ('Helvetica', 24, 'bold'),
            "date_time_label_font": ('Helvetica', 20, 'bold'),
            "label_width": 10,
            "label_height": 2,
            "frame_background": "#ffffff",
            "frame_borderwidth": 2,
            "frame_relief": "solid",
            "frame_padding": 20,
            "update_interval": 1800000,  # 30 Minuten
            "log_file": "namaz_vakti.log"
        }

        self.root = root
        self.root.title("Gebetszeiten")
        self.root.geometry("1920x1080")
        if self.config["fullscreen"]:
            self.root.attributes('-fullscreen', True)  # Vollbildmodus aktivieren
        self.root.bind("<Escape>", self.exit_fullscreen)  # Vollbildmodus mit Escape beenden

        # Logging konfigurieren
        logging.basicConfig(filename=self.config["log_file"], level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Hintergrundbild hinzufügen
        self.set_background_image()

        self.create_widgets()
        
        # Daten abrufen und aktualisieren
        self.update_prayer_times()
        self.update_clock()
        self.schedule_update()

    def set_background_image(self):
        try:
            self.background_image = Image.open(self.config["background_image_path"])  # Pfad zum Bild anpassen
            self.background_image = self.background_image.resize((1920, 1080), Image.LANCZOS)
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = tk.Label(self.root, image=self.background_photo)
            self.background_label.place(relwidth=1, relheight=1)
            self.log_message("Hintergrundbild erfolgreich geladen.", "info")
        except (FileNotFoundError, UnidentifiedImageError) as e:
            self.log_message(f"Fehler beim Laden des Hintergrundbildes: {e}", "error")
            self.root.destroy()

    def create_widgets(self):
        self.city_label = self.create_label(self.root, self.config["city_name"], self.config["city_label_font"], 0.05)
        self.date_label = self.create_label(self.root, "", self.config["date_time_label_font"], 0.1)
        self.time_label = self.create_label(self.root, "", self.config["date_time_label_font"], 0.15)

        self.time_frame = tk.Frame(self.root, background=self.config["frame_background"], borderwidth=self.config["frame_borderwidth"], relief=self.config["frame_relief"], padx=self.config["frame_padding"], pady=self.config["frame_padding"])
        self.time_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.prayer_labels = {}
        self.prayers = ["Imsak", "Gunes", "Ogle", "Ikindi", "Aksam", "Yatsi"]
        for i, prayer in enumerate(self.prayers):
            label_frame = tk.Frame(self.time_frame, background=self.config["label_background"], padx=10, pady=10)
            label_frame.grid(row=0, column=i, padx=10, pady=10)
            label_frame.grid_propagate(False)
            label = tk.Label(label_frame, text=f"{prayer}\n-", font=self.config["label_font"], background=self.config["label_background"], foreground=self.config["label_foreground"], width=self.config["label_width"], height=self.config["label_height"])
            label.pack(fill="both", expand=True)
            self.prayer_labels[prayer] = label

    def create_label(self, parent, text, font, rely):
        label = tk.Label(parent, text=text, font=font, background="#ffffff", borderwidth=self.config["frame_borderwidth"], relief=self.config["frame_relief"])
        label.place(relx=0.5, rely=rely, anchor='center')
        return label

    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_clock)  # Aktualisierung alle 1000 ms (1 Sekunde)

    def update_prayer_times(self):
        try:
            self.log_message("Aktualisiere Gebetszeiten...", "debug")
            prayer_times = self.get_prayer_times(self.config["city_id"])
            if prayer_times:
                today = self.convert_date_to_turkish(datetime.now())
                self.date_label.config(text=today)
                self.log_message(f"Heutiges Datum: {today}", "info")
                if today in prayer_times:
                    for prayer in self.prayers:
                        time = prayer_times[today].get(prayer, "-")
                        self.log_message(f"Setze {prayer}: {time}", "info")
                        self.prayer_labels[prayer].config(text=f"{prayer}\n{time}")
                else:
                    self.log_message(f"Keine Gebetszeiten für heute ({today}) gefunden.", "warning")
            else:
                self.log_message("Gebetszeiten konnten nicht abgerufen werden.", "error")
        except Exception as e:
            self.log_message(f"Fehler beim Abrufen der Gebetszeiten: {e}", "error")

    def convert_date_to_turkish(self, date):
        months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        days = {
            "Monday": "Pazartesi", "Tuesday": "Salı", "Wednesday": "Çarşamba",
            "Thursday": "Perşembe", "Friday": "Cuma", "Saturday": "Cumartesi",
            "Sunday": "Pazar"
        }
        day = date.day
        month = months[date.month]
        year = date.year
        weekday = days[date.strftime("%A")]
        return f"{day} {month} {year} {weekday}"

    def get_prayer_times(self, city_id):
        try:
            url = f"https://namazvakitleri.diyanet.gov.tr/tr-TR/{city_id}"
            self.log_message(f"Rufe URL ab: {url}", "debug")
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            self.log_message(f"Fehler: {e}", "error")
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table vakit-table"})
        if not table:
            self.log_message("Fehler: Tabelle nicht gefunden.", "error")
            return None
        rows = table.find_all("tr")

        prayer_times = {}
        for row in rows[1:]:  # Skip the header row
            cells = row.find_all("td")
            date = cells[0].get_text(strip=True)
            imsak_time = cells[1].get_text(strip=True)
            # Wenn "Imsak" nicht im richtigen Format ist, extrahiere nur die Uhrzeit
            if not imsak_time.replace(':', '').isdigit():
                imsak_time = cells[1].find_next("td").get_text(strip=True)
            prayer_times[date] = {
                "Imsak": imsak_time,
                "Gunes": cells[2].get_text(strip=True),
                "Ogle": cells[3].get_text(strip=True),
                "Ikindi": cells[4].get_text(strip=True),
                "Aksam": cells[5].get_text(strip=True),
                "Yatsi": cells[6].get_text(strip=True),
            }
        self.log_message(f"Gebetszeiten abgerufen: {prayer_times}", "info")
        return prayer_times

    def schedule_update(self):
        # Aktualisierung alle 30 Minuten
        self.root.after(self.config["update_interval"], self.update_and_schedule)

    def update_and_schedule(self):
        self.update_prayer_times()
        self.schedule_update()

    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)

    def log_message(self, message, level):
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)
        elif level == "warning":
            logging.warning(message)
        else:
            logging.debug(message)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = NamazVaktiApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fehler", f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        logging.critical(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
