#!/usr/bin/env python3
"""
Servidor web simple para la base de datos de formularios USCIS
"""
from flask import Flask, jsonify, send_file, render_template
import sqlite3
import os

app = Flask(__name__, static_folder='.', static_url_path='')

DB_PATH = 'uscis_forms/uscis_forms.db'
PDFS_PATH = 'uscis_forms/pdfs'

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/forms')
def get_forms():
    """Obtener todos los formularios descargados"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Obtener formularios
    c.execute("""
        SELECT form_number, form_title, pdf_filename, file_size 
        FROM forms 
        WHERE status='downloaded' 
        ORDER BY form_number
    """)
    
    forms = []
    for row in c.fetchall():
        forms.append({
            'number': row[0],
            'title': row[1] or f'Formulario {row[0]}',
            'filename': row[2],
            'size': row[3]
        })
    
    # Estadísticas
    total = len(forms)
    total_size = sum(f['size'] for f in forms if f['size'])
    series = len(set(f['number'].split('-')[0] for f in forms))
    
    conn.close()
    
    return jsonify({
        'forms': forms,
        'stats': {
            'total': total,
            'size': f'{total_size/(1024*1024):.2f} MB',
            'series': series
        }
    })

@app.route('/download/<filename>')
def download_form(filename):
    """Descargar un formulario PDF"""
    filepath = os.path.join(PDFS_PATH, filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'Archivo no encontrado'}), 404

@app.route('/api/search/<query>')
def search_forms(query):
    """Buscar formularios"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT form_number, form_title, pdf_filename, file_size 
        FROM forms 
        WHERE status='downloaded' 
        AND (form_number LIKE ? OR form_title LIKE ?)
        ORDER BY form_number
    """, (f'%{query}%', f'%{query}%'))
    
    forms = []
    for row in c.fetchall():
        forms.append({
            'number': row[0],
            'title': row[1] or f'Formulario {row[0]}',
            'filename': row[2],
            'size': row[3]
        })
    
    conn.close()
    return jsonify({'forms': forms})

if __name__ == '__main__':
    print("=" * 70)
    print("Servidor de Formularios USCIS")
    print("=" * 70)
    print(f"\nBase de datos: {DB_PATH}")
    print(f"PDFs: {PDFS_PATH}")
    print("\nNavega a: http://localhost:5000")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("=" * 70)
    
    app.run(debug=True, port=5000)
