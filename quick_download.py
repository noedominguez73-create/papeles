#!/usr/bin/env python3
"""
USCIS Forms Quick Downloader
Uses predictable URL patterns to download common forms directly
"""

import os
import sqlite3
import requests
import time
from datetime import datetime

# Lista exhaustiva de formularios USCIS conocidos
COMMON_FORMS = [
    # Serie I (Immigration)
    "I-9", "I-90", "I-92", "I-94", "I-102", "I-129", "I-129CW", "I-129CWR", "I-129F", "I-129S", "I-130", "I-131", "I-131A",
    "I-134", "I-140", "I-140G", "I-191", "I-192", "I-193", "I-212", "I-290B", "I-356", "I-360", "I-361", "I-363", "I-363A", "I-407", "I-485",
    "I-508", "I-516", "I-526", "I-526E", "I-539", "I-566", "I-589", "I-590", "I-600", "I-600A",
    "I-601", "I-601A", "I-602", "I-612", "I-687", "I-690", "I-693", "I-694", "I-695", "I-698",
    "I-730", "I-751", "I-765", "I-765V", "I-800", "I-800A", "I-817", "I-821", "I-821D", "I-824",
    "I-829", "I-854", "I-864", "I-864A", "I-864EZ", "I-864P", "I-864W", "I-865", "I-881", "I-894", "I-905", "I-907", "I-910",
    "I-912", "I-914", "I-914A", "I-918", "I-924", "I-924A", "I-929", "I-941", "I-945", 
    "I-956", "I-956F", "I-956G", "I-956H", "I-956K",
    # Serie N (Naturalization)
    "N-14", "N-300", "N-336", "N-400", "N-426", "N-470", "N-565", "N-600", "N-600K", "N-644", "N-648",
    # Serie G (General)
    "G-1", "G-2", "G-3", "G-4", "G-4A", "G-5", "G-5A", "G-7", "G-28", "G-28I", "G-56", "G-56A",
    "G-146", "G-325", "G-325A", "G-325C", "G-325D", "G-325R", "G-639", "G-639-1", "G-731", "G-735", "G-845",
    "G-845S", "G-884", "G-1041", "G-1041A", "G-1055", "G-1145", "G-1256", "G-1450", "G-1566", "G-1650", "G-1651",
    # Serie AR (Alien Registration)
    "AR-11", "AR-103",
    # Otros
    "M-378", "M-476", "M-565", "M-566",
    "DS-260", # State Dept pero procesado por USCIS
    "EOIR-29", # EOIR form
]

class QuickDownloader:
    def __init__(self):
        self.output_dir = 'uscis_forms'
        self.pdfs_dir = os.path.join(self.output_dir, 'pdfs')
        self.db_path = os.path.join(self.output_dir, 'uscis_forms.db')
        
        os.makedirs(self.pdfs_dir, exist_ok=True)
        
        # Patrones de URL para intentar
        self.url_patterns = [
            "https://www.uscis.gov/sites/default/files/document/forms/{form}.pdf",
            "https://www.uscis.gov/sites/default/files/form/{form}.pdf",
            "https://www.uscis.gov/sites/default/files/files/form/{form}.pdf",
        ]
        
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY,
            form_number TEXT UNIQUE,
            form_title TEXT,
            pdf_url TEXT,
            pdf_filename TEXT,
            file_size INTEGER,
            download_date TEXT,
            status TEXT
        )''')
        conn.commit()
        conn.close()
        
    def try_download(self, form_number):
        """Try different URL patterns to download form"""
        form_lower = form_number.lower().replace(' ', '-')
        
        for pattern in self.url_patterns:
            url = pattern.format(form=form_lower)
            
            try:
                response = requests.get(url, timeout=15, stream=True)
                if response.status_code == 200:
                    # Success!
                    filename = f"{form_number}.pdf"
                    filepath = os.path.join(self.pdfs_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(8192):
                            f.write(chunk)
                    
                    size = os.path.getsize(filepath)
                    print(f"✓ {form_number:15} - {size:10,} bytes - {url}")
                    return url, size, 'downloaded'
                    
            except Exception as e:
                continue
        
        print(f"✗ {form_number:15} - Not found")
        return None, 0, 'not_found'
    
    def save_to_db(self, form_number, url, size, status):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO forms 
            (form_number, pdf_url, pdf_filename, file_size, download_date, status)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (form_number, url, f"{form_number}.pdf", size, datetime.now().isoformat(), status))
        conn.commit()
        conn.close()
    
    def run(self):
        print("=" * 70)
        print("USCIS Forms Quick Downloader")
        print("=" * 70)
        
        self.init_db()
        
        downloaded = 0
        failed = 0
        
        for i, form in enumerate(COMMON_FORMS, 1):
            print(f"[{i}/{len(COMMON_FORMS)}] ", end="")
            url, size, status = self.try_download(form)
            self.save_to_db(form, url, size, status)
            
            if status == 'downloaded':
                downloaded += 1
            else:
                failed += 1
            
            time.sleep(0.3)  # Be nice to server
        
        print("\n" + "=" * 70)
        print(f"Descargados: {downloaded}")
        print(f"No encontrados: {failed}")
        print(f"Total: {len(COMMON_FORMS)}")
        print(f"\nBase de datos: {self.db_path}")
        print(f"PDFs: {self.pdfs_dir}")
        print("=" * 70)

if __name__ == '__main__':
    downloader = QuickDownloader()
    downloader.run()
