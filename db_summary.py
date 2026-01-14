import sqlite3
import os

conn = sqlite3.connect('uscis_forms/uscis_forms.db')
c = conn.cursor()

output = []
output.append("=" * 70)
output.append("RESUMEN DE BASE DE DATOS USCIS")
output.append("=" * 70)

# Totales
total = c.execute('SELECT COUNT(*) FROM forms').fetchone()[0]
downloaded = c.execute("SELECT COUNT(*) FROM forms WHERE status='downloaded'").fetchone()[0]
failed = c.execute("SELECT COUNT(*) FROM forms WHERE status='not_found'").fetchone()[0]

output.append(f"\nTotal registros: {total}")
output.append(f"Descargados: {downloaded}")
output.append(f"No encontrados: {failed}")

# Tamaño
size = c.execute("SELECT SUM(file_size) FROM forms WHERE status='downloaded'").fetchone()[0] or 0
output.append(f"\nTamanio total: {size/(1024*1024):.2f} MB")

# PDFs físicos
pdfs = len([f for f in os.listdir('uscis_forms/pdfs') if f.endswith('.pdf')])
output.append(f"Archivos PDF fisicos: {pdfs}")

# Consistencia
status_check = 'OK' if pdfs == downloaded else 'ERROR'
output.append(f"\nConsistencia BD/Archivos: {status_check}")

# Por serie
output.append("\nFormularios descargados por serie:")
series = {}
for (num,) in c.execute("SELECT form_number FROM forms WHERE status='downloaded'"):
    prefix = num.split('-')[0] if '-' in num else 'Otros'
    series[prefix] = series.get(prefix, 0) + 1

for prefix in sorted(series.keys()):
    output.append(f"  {prefix:8}: {series[prefix]:3} formularios")

# Top 15
output.append("\nLista de formularios (muestra de 15):")
for (num,) in c.execute("SELECT form_number FROM forms WHERE status='downloaded' ORDER BY form_number LIMIT 15"):
    output.append(f"  - {num}")

output.append("\n" + "=" * 70)
output.append("Base de datos: uscis_forms/uscis_forms.db")
output.append("PDFs: uscis_forms/pdfs/")
output.append("=" * 70)

conn.close()

# Guardar y mostrar
result = '\n'.join(output)
with open('db_status.txt', 'w', encoding='utf-8') as f:
    f.write(result)

print(result)
