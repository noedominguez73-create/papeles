#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparador guardando resultados en archivo
"""

import sqlite3

# Lista oficial
OFFICIAL_FORMS = [
    "AR-11", "EOIR-29", "G-28", "G-28I", "G-325A", "G-325R", "G-639", "G-845",
    "G-845 Supplement", "G-884", "G-1041", "G-1041A", "G-1055", "G-1145", "G-1256",
    "G-1450", "G-1566", "G-1650", "G-1651", "I-9", "I-90", "I-102", "I-129",
    "I-129CW", "I-129CWR", "I-129F", "I-129S", "I-130", "I-131", "I-131A", "I-134",
    "I-140", "I-140G", "I-191", "I-192", "I-193", "I-212", "I-290B", "I-356",
    "I-360", "I-361", "I-363", "I-407", "I-485", "I-485 Supplement A",
    "I-485 Supplement J", "I-508", "I-526", "I-526E", "I-539", "I-566", "I-589",
    "I-600", "I-600A", "I-601", "I-601A", "I-602", "I-612", "I-687", "I-690",
    "I-693", "I-694", "I-698", "I-730", "I-751", "I-765", "I-765V", "I-800",
    "I-800A", "I-817", "I-821", "I-821D", "I-824", "I-829", "I-854", "I-864",
    "I-864A", "I-864EZ", "I-864P", "I-865", "I-881", "I-905", "I-907", "I-910",
    "I-912", "I-914", "I-918", "I-929", "I-941", "I-945", "I-956", "I-956F",
    "I-956G", "I-956H", "I-956K", "N-300", "N-336", "N-400", "N-426", "N-470",
    "N-565", "N-600", "N-600K", "N-644", "N-648"
]

def normalize(form):
    return form.split()[0].upper()

official_normalized = set([normalize(f) for f in OFFICIAL_FORMS])

conn = sqlite3.connect('uscis_forms/uscis_forms.db')
cursor = conn.cursor()

cursor.execute("SELECT form_number, status FROM forms WHERE status='downloaded'")
downloaded = cursor.fetchall()
downloaded_set = set([f[0].upper() for f in downloaded])

cursor.execute("SELECT form_number FROM forms")
all_tried = cursor.fetchall()
tried_set = set([f[0].upper() for f in all_tried])

conn.close()

# Escribir reporte
with open('comparison_report.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("COMPARACION: Formularios Descargados vs Lista Oficial USCIS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("ESTADISTICAS\n")
    f.write(f"  Lista oficial USCIS: {len(official_normalized)} formularios unicos\n")
    f.write(f"  Descargados exitosamente: {len(downloaded_set)} formularios\n")
    f.write(f"  Intentados total: {len(tried_set)} formularios\n\n")
    
    in_both = official_normalized & downloaded_set
    f.write(f"[OK] DESCARGADOS DE LA LISTA OFICIAL: {len(in_both)}\n")
    for form in sorted(in_both):
        f.write(f"   [OK] {form}\n")
    
    missing = official_normalized - downloaded_set
    f.write(f"\n[FALTA] FALTANTES DE LA LISTA OFICIAL: {len(missing)}\n")
    for form in sorted(missing):
        tried = "intentado sin exito" if form in tried_set else "no intentado"
        f.write(f"   [X] {form:15} ({tried})\n")
    
    extra = downloaded_set - official_normalized
    if extra:
        f.write(f"\n[EXTRA] Descargados pero NO en lista oficial: {len(extra)}\n")
        for form in sorted(extra):
            f.write(f"   [+] {form}\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("RESUMEN\n")
    f.write("=" * 80 + "\n")
    coverage = (len(in_both) / len(official_normalized)) * 100
    f.write(f"Cobertura: {len(in_both)}/{len(official_normalized)} ({coverage:.1f}%)\n")
    f.write(f"Faltantes: {len(missing)} formularios\n")
    f.write("=" * 80 + "\n")

print("Reporte guardado en: comparison_report.txt")
