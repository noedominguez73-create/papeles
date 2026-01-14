#!/usr/bin/env python3
import sqlite3
import os

db_path = 'uscis_forms/uscis_forms.db'
pdfs_dir = 'uscis_forms/pdfs'

print("=" * 70)
print("REPORTE DE DESCARGA - FORMULARIOS USCIS")
print("=" * 70)

# Database stats
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM forms')
total_forms = cursor.fetchone()[0]

cursor.execute('SELECT status, COUNT(*) FROM forms GROUP BY status')
status_counts = cursor.fetchall()

cursor.execute('SELECT SUM(file_size) FROM forms WHERE status="downloaded"')
total_size = cursor.fetchone()[0] or 0

cursor.execute('SELECT form_number, form_title, file_size FROM forms WHERE status="downloaded" ORDER BY file_size DESC LIMIT 10')
top_forms = cursor.fetchall()

cursor.execute('SELECT * FROM scrape_log ORDER BY id DESC LIMIT 1')
last_scrape = cursor.fetchone()

print(f"\n📊 ESTADÍSTICAS GENERALES")
print("-" * 70)
print(f"Total formularios en base de datos: {total_forms}")
print(f"\nEstados de formularios:")
for status, count in status_counts:
    print(f"  • {status}: {count}")

print(f"\n💾 ALMACENAMIENTO")
print("-" * 70)
print(f"Tamaño total descargado: {total_size:,} bytes ({total_size/(1024*1024):.2f} MB)")

# Count actual PDF files
pdf_count = len([f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')])
print(f"Archivos PDF físicos: {pdf_count}")

print(f"\n📋 TOP 10 ARCHIVOS MÁS GRANDES")
print("-" * 70)
for i, (num, title, size) in enumerate(top_forms, 1):
    print(f"{i:2}. {num:10} - {title[:45]:45} {size:10,} bytes")

print(f"\n🕐 ÚLTIMA EJECUCIÓN")
print("-" * 70)
if last_scrape:
    print(f"Fecha: {last_scrape[1]}")
    print(f"Formularios procesados: {last_scrape[2]}")
    print(f"Descargados: {last_scrape[3]}")
    print(f"Fallidos: {last_scrape[4]}")
    print(f"Estado: {last_scrape[5]}")

# Sample forms
print(f"\n📄 MUESTRA DE FORMULARIOS")
print("-" * 70)
cursor.execute('SELECT form_number, form_title, status FROM forms LIMIT 15')
sample = cursor.fetchall()
for num, title, status in sample:
    icon = "✓" if status == "downloaded" else "✗"
    print(f"{icon} {num:10} - {title[:50]}")

conn.close()

print("\n" + "=" * 70)
print(f"Base de datos: {db_path}")
print(f"PDFs descargados: {pdfs_dir}")
print("=" * 70)
