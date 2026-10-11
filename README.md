# GraphMind AI

**Graph-Based Pattern Discovery and Relationship Intelligence System**

GraphMind AI is a student project prototype for exploring relationships in connected data, visualizing networks, and flagging potentially unusual nodes.

## Features
- Interactive graph visualization
- CSV upload (`source`, `target`, optional `weight`)
- Network summary metrics
- Basic high-degree anomaly flagging
- Downloadable node summary

## Run locally
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Open the terminal in VS Code.
4. Create and activate a virtual environment if desired.
5. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

## CSV format
Your CSV should contain `source` and `target` columns. `weight` is optional.

```csv
source,target,weight
Alice,Bob,1
Alice,Charlie,1
Bob,Charlie,2
```

## Project status
Starter version / in development. The anomaly detector uses a simple degree-based rule and is intended for educational demonstration, not for making high-stakes decisions.

## Technologies
Python, Streamlit, Pandas, NetworkX, Plotly
