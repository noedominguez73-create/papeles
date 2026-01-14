#!/usr/bin/env python3
"""
Verificacion completa de la base de datos USCIS
"""
import sqlite3
import os

db_path = 'uscis_forms/uscis_forms.db'
pdfs_dir = 'uscis_forms/pdfs'

print("=" * 80)
print("VERIFICACION COMPLETA DE BASE DE DATOS")
print("=" * 80)

# Conectar a BD
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Estadísticas generales
print("\n1. ESTADISTICAS GENERALES")
print("-" * 80)

c.execute("SELECT COUNT(*) FROM forms")
total_registros = c.fetchone()[0]
print(f"Total registros en BD: {total_registros}")

c.execute("SELECT status, COUNT(*) FROM forms GROUP BY status")
for status, count in c.fetchall():
    print(f"  - {status}: {count}")

# Tamaño total
c.execute("SELECT SUM(file_size) FROM forms WHERE status='downloaded'")
total_size = c.fetchone()[0] or 0
print(f"\nTamaño total descargado: {total_size:,} bytes ({total_size/(1024*1024):.2f} MB)")

# Archivos físicos
pdf_files = [f for f in os.listdir(pdfs_dir) if f.endswith('.pdf')]
print(f"Archivos PDF físicos: {len(pdf_files)}")

# Verificar consistencia
print("\n2. VERIFICACION DE CONSISTENCIA")
print("-" * 80)

c.execute("SELECT COUNT(*) FROM forms WHERE status='downloaded' AND pdf_filename IS NOT NULL")
registros_con_pdf = c.fetchone()[0]

if len(pdf_files) == registros_con_pdf:
    print(f"OK - Archivos PDF ({len(pdf_files)}) coinciden con registros ({registros_con_pdf})")
else:
    print(f"ADVERTENCIA - PDFs: {len(pdf_files)}, Registros: {registros_con_pdf}")

# Mostrar muestra de datos
print("\n3. MUESTRA DE FORMULARIOS EN BASE DE DATOS (primeros 20)")
print("-" * 80)
c.execute("""SELECT form_number, form_title, 
             CAST(file_size AS INTEGER) as size, status 
             FROM forms 
             WHERE status='downloaded'
             ORDER BY form_number 
             LIMIT 20""")

for num, title, size, status in c.fetchall():
    size_kb = size / 1024 if size else 0
    print(f"{num:12} - {size_kb:7.1f} KB - {status}")

# Formularios por serie
print("\n4. FORMULARIOS POR SERIE")
print("-" * 80)

series = {}
c.execute("SELECT form_number FROM forms WHERE status='downloaded'")
for (num,) in c.fetchall():
    prefix = num.split('-')[0] if '-' in num else 'Otros'
    series[prefix] = series.get(prefix, 0) + 1

for prefix in sorted(series.keys()):
    print(f"Serie {prefix:10}: {series[prefix]:3} formularios")

# Top 10 más grandes
print("\n5. TOP 10 ARCHIVOS MAS GRANDES")
print("-" * 80)
c.execute("""SELECT form_number, CAST(file_size AS INTEGER) as size 
             FROM forms 
             WHERE status='downloaded' 
             ORDER BY size DESC 
             LIMIT 10""")

for i, (num, size) in enumerate(c.fetchall(), 1):
    print(f"{i:2}. {num:12} - {size/1024:8.1f} KB ({size/(1024*1024):.2f} MB)")

# Ejemplos de consultas útiles
print("\n6. EJEMPLOS DE CONSULTAS SQL")
print("-" * 80)
print("""
# Buscar formulario específico:
SELECT * FROM forms WHERE form_number = 'I-485';

# Ver todos los formularios de naturalización:
SELECT form_number, pdf_filename FROM forms 
WHERE form_number LIKE 'N-%' AND status='downloaded';

# Formularios descargados hoy:
SELECT form_number, download_date FROM forms 
WHERE DATE(download_date) = DATE('now') AND status='downloaded';

# Total por estado:
SELECT status, COUNT(*), SUM(file_size)/(1024*1024) as total_mb 
FROM forms GROUP BY status;
""")

conn.close()

print("\n" + "=" * 80)
print("Base de datos verificada correctamente")
print(f"Ubicacion: {os.path.abspath(db_path)}")
print("=" * 80)
