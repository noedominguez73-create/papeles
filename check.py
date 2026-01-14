import sqlite3
import os

db = sqlite3.connect('uscis_forms/uscis_forms.db')
c = db.cursor()

print("Total forms:", c.execute('SELECT COUNT(*) FROM forms').fetchone()[0])
print("\nBy status:")
for row in c.execute('SELECT status, COUNT(*) FROM forms GROUP BY status'):
    print(f"  {row[0]}: {row[1]}")

# Total size
size = c.execute('SELECT SUM(file_size) FROM forms WHERE status="downloaded"').fetchone()[0] or 0
print(f"\nTotal size: {size/(1024*1024):.2f} MB")

# Count PDFs
pdf_count = len([f for f in os.listdir('uscis_forms/pdfs') if f.endswith('.pdf')])
print(f"PDF files: {pdf_count}")

# Sample
print("\nSample forms:")
for row in c.execute('SELECT form_number, form_title, status FROM forms LIMIT 10'):
    print(f"  {row[0]:10} - {row[1][:40]:40} [{row[2]}]")

db.close()
