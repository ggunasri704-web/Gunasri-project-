import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="GraphMind AI", page_icon="🧠", layout="wide")

st.title("🧠 GraphMind AI")
st.caption("Graph-Based Pattern Discovery and Relationship Intelligence System")
st.write("Explore connections in your data and flag unusual graph relationships.")

SAMPLE_DATA = pd.DataFrame({
    "source": ["A", "A", "B", "B", "C", "C", "D", "E", "F", "F", "G"],
    "target": ["B", "C", "C", "D", "D", "E", "E", "F", "G", "H", "A"],
    "weight": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
})

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload a CSV with source and target columns", type=["csv"])
    st.caption("Required columns: source and target. An optional weight column is supported.")
    show_labels = st.checkbox("Show node labels", value=True)

if uploaded:
    try:
        data = pd.read_csv(uploaded)
        data.columns = [c.strip().lower() for c in data.columns]
        if not {"source", "target"}.issubset(data.columns):
            st.error("CSV must contain columns named 'source' and 'target'.")
            st.stop()
    except Exception as exc:
        st.error(f"Could not read the CSV: {exc}")
        st.stop()
else:
    data = SAMPLE_DATA.copy()
    st.info("Showing sample data. Upload your own CSV using the sidebar.")

data = data.dropna(subset=["source", "target"]).copy()
data["source"] = data["source"].astype(str)
data["target"] = data["target"].astype(str)

G = nx.Graph()
for _, row in data.iterrows():
    source, target = row["source"], row["target"]
    weight = row["weight"] if "weight" in data.columns and pd.notna(row.get("weight")) else 1
    if G.has_edge(source, target):
        G[source][target]["weight"] += float(weight)
    else:
        G.add_edge(source, target, weight=float(weight))

if G.number_of_nodes() == 0:
    st.warning("No graph data found. Upload a CSV containing source and target values.")
    st.stop()

degree = dict(G.degree())
avg_degree = sum(degree.values()) / len(degree) if degree else 0
components = nx.number_connected_components(G) if G.number_of_nodes() else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Nodes", G.number_of_nodes())
c2.metric("Connections", G.number_of_edges())
c3.metric("Connected Groups", components)
c4.metric("Average Degree", f"{avg_degree:.2f}")

st.subheader("Interactive Relationship Graph")
pos = nx.spring_layout(G, seed=42)
edge_x, edge_y = [], []
for u, v in G.edges():
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y, mode="lines",
    line=dict(width=1, color="#9CA3AF"),
    hoverinfo="none"
)

node_x, node_y, node_text, node_sizes, node_colors = [], [], [], [], []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(f"Node: {node}<br>Connections: {degree[node]}")
    node_sizes.append(14 + degree[node] * 4)
    node_colors.append(degree[node])

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text" if show_labels else "markers",
    text=list(G.nodes()) if show_labels else None,
    textposition="top center",
    hovertext=node_text, hoverinfo="text",
    marker=dict(size=node_sizes, color=node_colors, colorscale="Blues",
                showscale=True, colorbar=dict(title="Degree"),
                line=dict(width=1, color="white"))
)

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    height=560, margin=dict(l=10, r=10, t=20, b=10),
    showlegend=False, paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(visible=False), yaxis=dict(visible=False)
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Anomaly Detection")
st.write("This starter version flags nodes with unusually high connection counts compared with the network's average.")
mean_degree = avg_degree
std_degree = pd.Series(list(degree.values()), dtype=float).std(ddof=0) if degree else 0
threshold = mean_degree + std_degree
anomalies = [
    {"Node": node, "Connections": count, "Reason": "Higher-than-usual number of connections"}
    for node, count in degree.items()
    if count > threshold and count >= 2
]
if anomalies:
    st.warning(f"Found {len(anomalies)} potentially unusual node(s). Review these results; they are flags, not proof of suspicious activity.")
    st.dataframe(pd.DataFrame(anomalies), use_container_width=True, hide_index=True)
else:
    st.success("No high-degree anomalies found using the current simple rule.")

st.subheader("Node Summary")
summary = pd.DataFrame({
    "Node": list(degree.keys()),
    "Connections": list(degree.values()),
    "Degree Centrality": [round(v, 4) for v in nx.degree_centrality(G).values()]
}).sort_values("Connections", ascending=False)
st.dataframe(summary, use_container_width=True, hide_index=True)

st.download_button(
    "Download node summary CSV",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name="graphmind_node_summary.csv",
    mime="text/csv"
)

with st.expander("How to format your CSV"):
    st.code("source,target,weight\nAlice,Bob,1\nAlice,Charlie,1\nBob,Charlie,2", language="csv")
    st.write("The weight column is optional. Each row represents a connection between two nodes.")
