# 🚦 Madrid Traffic Explorer

Dashboard interactivo para analizar el **tráfico de Madrid en tiempo real**, consultar su evolución histórica y realizar preguntas sobre los datos mediante **Inteligencia Artificial**.

## URL : https://trafico-madrid-arfjzfkr2gt5wptwyghpk7.streamlit.app/

## 🎯 Objetivo

El proyecto transforma los datos abiertos de tráfico del **Ayuntamiento de Madrid** en información visual y comprensible para el usuario.

Integra en una misma aplicación:

- 🚦 Estado del tráfico en tiempo real
- 🗺️ Mapa interactivo de Madrid
- 📈 Análisis histórico
- 💬 Chat con Inteligencia Artificial

## ✨ Funcionalidades

### 🚦 Tráfico actual
Consulta y procesa miles de puntos de medición, mostrando:

- Flujo de vehículos (veh/h)
- Ocupación de la vía (%)
- Saturación (%)
- Estado: **Fluido, Lento, Retenciones o Congestión**

### 🗺️ Mapa interactivo
Permite explorar los puntos de medición sobre Madrid, filtrar por estado del tráfico y consultar información detallada de cada punto.

### 📈 Histórico
Las capturas se almacenan en **SQLite** para analizar la evolución del tráfico y comparar diferentes momentos.

### 💬 Chat IA
Asistente desarrollado con **Ollama + Llama 3.2** que utiliza los datos reales del tráfico como contexto.

Ejemplos:

> ¿Cómo está la calle Princesa?  
> ¿Dónde hay más congestión ahora?  
> ¿Cuántos puntos tienen retenciones?

Se utiliza **RapidFuzz** para mejorar la búsqueda de calles y puntos aunque el usuario no escriba exactamente su nombre.

## 🛠️ Tecnologías

`Python` · `Pandas` · `Streamlit` · `Plotly` · `SQLite` · `Ollama` · `Llama 3.2` · `RapidFuzz` · `Git`

## 🧠 Arquitectura

```text
Datos Ayuntamiento de Madrid
           ↓
     Python + Pandas
           ↓
   Limpieza y análisis
           ↓
    ┌──────┴──────┐
    ↓             ↓
Datos actuales   SQLite
    └──────┬──────┘
           ↓
       Streamlit
    ┌──────┼──────┐
    ↓      ↓      ↓
  KPIs    Mapa  Histórico
                  ↓
               Chat IA
                  ↓
          Ollama + Llama 3.2
```

## 🚀 Ejecutar el proyecto

```bash
pip install -r requirements.txt
ollama pull llama3.2:3b
python -m streamlit run app.py
```

## 👤 Autor

**Diego Vega**

Proyecto de portfolio desarrollado dentro de mi formación en **Data Analytics & IA**.

