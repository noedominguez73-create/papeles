# Base de Datos de Formularios USCIS

Sistema completo para acceder y gestionar 100 formularios de inmigración de USCIS.

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor Web

```bash
python server.py
```

### 2. Abrir en el Navegador

Navega a: **http://localhost:5000**

## ✨ Características

- **Búsqueda en Tiempo Real** - Encuentra formularios por número o palabra clave
- **Filtros por Serie** - I, N, G, AR, EOIR
- **Descarga Directa** - Un clic para descargar cualquier PDF
- **Interfaz Moderna** - Diseño responsivo y atractivo
- **100 Formularios** - 57.53 MB de formularios listos para usar
- **Base de Datos SQLite** - Acceso rápido y confiable

## 📊 Contenido

### Formularios Disponibles

- **Serie I (Immigration):** 72 formularios
  - I-9, I-90, I-102, I-129, I-130, I-131, I-140, I-360, I-485, I-526, I-539, I-589, etc.
  
- **Serie N (Naturalization):** 10 formularios
  - N-300, N-336, N-400, N-426, N-470, N-565, N-600, N-600K, N-644, N-648
  
- **Serie G (General):** 16 formularios
  - G-28, G-28I, G-325A, G-639, G-845, G-1041, G-1145, G-1450, etc.
  
- **Otros:** AR-11, EOIR-29

## 🔧 Scripts Disponibles

### Descargar Formularios
```bash
python quick_download.py
```

### Verificar Base de Datos
```bash
python db_summary.py
```

### Comparar con Lista Oficial
```bash
python compare_forms.py
```

### Iniciar Servidor Web
```bash
python server.py
```

## 📁 Estructura de Archivos

```
c:\papeles\
├── index.html              # Interfaz web principal
├── server.py               # Servidor Flask
├── quick_download.py       # Descargador de formularios
├── db_summary.py           # Verificador de BD
├── compare_forms.py        # Comparador con lista oficial
├── uscis_forms/
│   ├── uscis_forms.db     # Base de datos SQLite
│   └── pdfs/              # 100 PDFs descargados
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

## 🌐 API Endpoints

### Obtener Todos los Formularios
```
GET /api/forms
```

### Buscar Formularios
```
GET /api/search/<query>
```

### Descargar PDF
```
GET /download/<filename>
```

## 💾 Uso de la Base de Datos

### Consultas SQL Útiles

**Buscar formulario específico:**
```sql
SELECT * FROM forms WHERE form_number = 'I-485';
```

**Formularios de naturalización:**
```sql
SELECT form_number, pdf_filename 
FROM forms 
WHERE form_number LIKE 'N-%' 
AND status='downloaded';
```

**Estadísticas:**
```sql
SELECT status, COUNT(*), SUM(file_size)/(1024*1024) as total_mb 
FROM forms 
GROUP BY status;
```

## 📈 Estadísticas

- **Cobertura:** 99/102 formularios de la lista oficial (97.1%)
- **Total Descargado:** 100 formularios
- **Tamaño Total:** 57.53 MB
- **Última Actualización:** Enero 2026

## 🛠️ Tecnologías

- **Backend:** Python + Flask
- **Base de Datos:** SQLite
- **Frontend:** HTML5 + CSS3 + JavaScript Vanilla
- **Web Scraping:** Requests + BeautifulSoup + Selenium

## 📝 Notas

Los formularios se descargan directamente de USCIS.gov usando patrones de URL predecibles.
Todos los formularios son gratuitos y oficiales de USCIS.

---

**Desarrollado para facilitar el acceso a formularios de inmigración** ✨
