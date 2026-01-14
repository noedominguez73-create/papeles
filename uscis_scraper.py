#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USCIS Forms Scraper v3 - Direct API approach
Uses USCIS API endpoint to get forms data
"""

import os
import sqlite3
import requests
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re

class USCISFormsScraper:
    def __init__(self, output_dir='uscis_forms'):
        self.base_url = 'https://www.uscis.gov'
        # Try multiple possible API endpoints
        self.api_endpoints = [
            'https://www.uscis.gov/api/forms',
            'https://www.uscis.gov/tools/all-forms-api',
            'https://egov.uscis.gov/forms/api/forms'
        ]
        self.output_dir = output_dir
        self.pdfs_dir = os.path.join(output_dir, 'pdfs')
        self.db_path = os.path.join(output_dir, 'uscis_forms.db')
        
        os.makedirs(self.pdfs_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        }
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_number TEXT UNIQUE,
                form_title TEXT,
                form_description TEXT,
                edition_date TEXT,
                pdf_url TEXT,
                pdf_filename TEXT,
                instructions_url TEXT,
                download_date TEXT,
                file_size INTEGER,
                category TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scrape_date TEXT,
                total_forms INTEGER,
                downloaded INTEGER,
                failed INTEGER,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ Base de datos inicializada: {self.db_path}")
    
    def try_api_endpoints(self):
        """Try different API endpoints to get forms data"""
        for endpoint in self.api_endpoints:
            print(f"\nProbando API: {endpoint}")
            try:
                response = requests.get(endpoint, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✓ API funciona! Encontrados datos")
                        return data
                    except:
                        pass
            except Exception as e:
                print(f"  ✗ No funciona: {e}")
        
        return None
    
    def scrape_with_selenium_wait(self):
        """Use Selenium with extended waits for dynamic content"""
        print("\nUsando Selenium con espera extendida...")
        
        chrome_options = Options()
        # Don't use headless - sometimes pages don't render properly headless
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = None
        forms = []
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get('https://www.uscis.gov/es/formularios/todos-los-formularios')
            
            print("Esperando que carguen los formularios...")
            time.sleep(10)  # Wait longer for JavaScript
            
            # Scroll to load lazy content
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Try to find any form elements
            page_text = driver.page_source
            
            # Save for debugging
            with open(os.path.join(self.output_dir, 'debug_page.html'), 'w', encoding='utf-8') as f:
                f.write(page_text)
            
            # Look for form numbers in text
            form_pattern = re.compile(r'([A-Z]-\d+[A-Z]?)', re.IGNORECASE)
            matches = set(form_pattern.findall(page_text))
            
            print(f"Encontrados {len(matches)} números de formulario en el HTML")
            
            # Try to find links to forms
            elements = driver.find_elements(By.TAG_NAME, 'a')
            
            for elem in elements:
                try:
                    href = elem.get_attribute('href') or ''
                    text = elem.text.strip()
                    
                    # Check if this is likely a form
                    form_num_match = form_pattern.search(text)
                    
                    if form_num_match:
                        form_number = form_num_match.group(1).upper()
                        
                        form_data = {
                            'form_number': form_number,
                            'title': text,
                            'url': href
                        }
                        
                        if '.pdf' in href.lower():
                            form_data['pdf_url'] = href
                        
                        forms.append(form_data)
                
                except Exception as e:
                    continue
            
            # Remove duplicates
            unique_forms = {f['form_number']: f for f in forms}.values()
            
            return list(unique_forms)
            
        except Exception as e:
            print(f"✗ Error con Selenium: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def get_common_forms_manually(self):
        """
        Fallback: Get a list of most common USCIS forms manually
        This is based on USCIS public information
        """
        print("\nUsando lista manual de formularios comunes...")
        
        common_forms = [
            {"number": "I-90", "title": "Solicitud para Reemplazar la Tarjeta de Residente Permanente"},
            {"number": "I-130", "title": "Petición de Familiar Extranjero"},
            {"number": "I-131", "title": "Solicitud de Documento de Viaje"},
            {"number": "I-140", "title": "Petición de Trabajador Inmigrante"},
            {"number": "I-360", "title": "Petición de Amerasiático, Viudo(a) o Inmigrante Especial"},
            {"number": "I-485", "title": "Solicitud de Registro de Residencia Permanente o Ajuste de Estatus"},
            {"number": "I-539", "title": "Solicitud de Extensión/Cambio de Estatus de No Inmigrante"},
            {"number": "I-601", "title": "Solicitud de Exención de Causales de Inadmisibilidad"},
            {"number": "I-693", "title": "Informe de Examen Médico y Registro de Vacunación"},
            {"number": "I-751", "title": "Petición para Remover las Condiciones de Residencia"},
            {"number": "I-765", "title": "Solicitud de Autorización de Empleo"},
            {"number": "I-800", "title": "Petición para Clasificar Huérfano Convencional como Pariente Inmediato"},
            {"number": "I-821", "title": "Solicitud de Estatus de Protección Temporal"},
            {"number": "I-824", "title": "Solicitud de Acción sobre una Solicitud o Petición Aprobada"},
            {"number": "I-829", "title": "Petición de Empresario para Remover Condiciones"},
            {"number": "I-864", "title": "Declaración Jurada de Patrocinio Económico"},
            {"number": "I-90", "title": "Aplic to Replace Permanent Resident Card"},
            {"number": "I-912", "title": "Solicitud de Exención de Pago de Tarifas"},
            {"number": "I-918", "title": "Petición de Estatus de No Inmigrante U"},
            {"number": "I-929", "title": "Petición para Familiar Calificador de Titular de U-1 o U-2"},
            {"number": "N-400", "title": "Solicitud de Naturalización"},
            {"number": "N-565", "title": "Solicitud de Reposición de Documento de Naturalización/Ciudadanía"},
            {"number": "N-600", "title": "Solicitud de Certificado de Ciudadanía"},
            {"number": "N-648", "title": "Certificación Médica para Excepciones por Discapacidad"},
            {"number": "G-28", "title": "Aviso de Comparecencia como Abogado o Representante Acreditado"},
            {"number": "G-325A", "title": "Información Biográfica"},
            {"number": "G-639", "title": "Solicitud de Libertad de Información/Privacidad"},
            {"number": "G-845", "title": "Hoja de Verificación de Documentos"},
            {"number": "G-1145", "title": "Notificación Electrónica de Aceptación de Solicitud/Petición"},
            {"number": "AR-11", "title": "Cambio de Dirección de Extranjero"},
        ]
        
        forms = []
        for form in common_forms:
            # Construct likely PDF URL
            form_num = form['number'].lower()
            pdf_url = f"https://www.uscis.gov/sites/default/files/document/forms/{form_num}.pdf"
            
            forms.append({
                'form_number': form['number'],
                'title': form['title'],
                'pdf_url': pdf_url,
                'source': 'manual_list'
            })
        
        print(f"✓ Cargados {len(forms)} formularios comunes")
        return forms
    
    def download_pdf(self, pdf_url, form_number):
        """Download PDF file"""
        try:
            filename = f"{form_number}.pdf"
            filepath = os.path.join(self.pdfs_dir, filename)
            
            if os.path.exists(filepath):
                print(f"  ↷ Ya existe: {filename}")
                return filepath, os.path.getsize(filepath)
            
            response = requests.get(pdf_url, headers=self.headers, timeout=60, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            print(f"  ✓ Descargado: {filename} ({file_size:,} bytes)")
            return filepath, file_size
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  ⚠ No encontrado (404): {pdf_url}")
            else:
                print(f"  ✗ Error HTTP {e.response.status_code}")
            return None, 0
        except Exception as e:
            print(f"  ✗ Error descargando: {e}")
            return None, 0
    
    def save_to_database(self, form_data):
        """Save form data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO forms 
                (form_number, form_title, form_description, pdf_url, pdf_filename, 
                 download_date, file_size, edition_date, category, status, instructions_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form_data.get('form_number'),
                form_data.get('title', ''),
                form_data.get('description', ''),
                form_data.get('pdf_url', ''),
                form_data.get('pdf_filename', ''),
                datetime.now().isoformat(),
                form_data.get('file_size', 0),
                form_data.get('edition_date', ''),
                form_data.get('category', form_data.get('source', '')),
                form_data.get('status', 'downloaded'),
                form_data.get('instructions_url', '')
            ))
            conn.commit()
        except Exception as e:
            print(f"  ✗ Error guardando en BD: {e}")
        finally:
            conn.close()
    
    def run(self):
        """Main execution"""
        print("=" * 70)
        print("USCIS Forms Scraper v3")
        print("=" * 70)
        
        self.init_database()
        
        # Strategy 1: Try API
        api_data = self.try_api_endpoints()
        
        forms = []
        
        # Strategy 2: Try Selenium with extended wait
        if not api_data:
            forms = self.scrape_with_selenium_wait()
        
        # Strategy 3: Use manual list of common forms
        if not forms:
            print("\n⚠ No se pudieron obtener formularios automáticamente")
            forms = self.get_common_forms_manually()
        
        if not forms:
            print("\n✗ No se pudo obtener ningún formulario")
            return
        
        print(f"\nIniciando descarga de {len(forms)} formularios...")
        print("-" * 70)
        
        downloaded = 0
        failed = 0
        
        for i, form in enumerate(forms, 1):
            form_number = form.get('form_number', f'FORM_{i}')
            print(f"\n[{i}/{len(forms)}] {form_number}: {form.get('title', 'Sin título')[:50]}")
            
            if 'pdf_url' in form:
                filepath, file_size = self.download_pdf(form['pdf_url'], form_number)
                
                if filepath:
                    form['pdf_filename'] = os.path.basename(filepath)
                    form['file_size'] = file_size
                    form['status'] = 'downloaded'
                    downloaded += 1
                else:
                    form['status'] = 'failed'
                    failed += 1
                
                self.save_to_database(form)
                time.sleep(0.5)
            else:
                print(f"  ⚠ No se encontró URL de PDF")
                form['status'] = 'no_pdf'
                failed += 1
                self.save_to_database(form)
        
        # Log results
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scrape_log (scrape_date, total_forms, downloaded, failed, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), len(forms), downloaded, failed, 'completed'))
        conn.commit()
        conn.close()
        
        # Summary
        print("\n" + "=" * 70)
        print("RESUMEN")
        print("=" * 70)
        print(f"Total formularios procesados: {len(forms)}")
        print(f"Descargados exitosamente: {downloaded}")
        print(f"Fallidos: {failed}")
        print(f"\nArchivos guardados en: {self.output_dir}")
        print(f"PDFs en: {self.pdfs_dir}")
        print(f"Base de datos: {self.db_path}")
        print("=" * 70)

if __name__ == '__main__':
    scraper = USCISFormsScraper()
    scraper.run()
