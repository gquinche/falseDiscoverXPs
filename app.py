import streamlit as st
import plotly.graph_objects as go

def compute_values(phi, alpha, beta):
    false_ideas = phi
    true_ideas = 1 - phi
    
    false_positives = alpha * false_ideas
    true_negatives = (1 - alpha) * false_ideas
    true_positives = (1 - beta) * true_ideas
    false_negatives = beta * true_ideas
    
    fpr = false_positives / (false_positives + true_negatives)
    fdr = false_positives / (false_positives + true_positives)
    
    return [false_positives, true_negatives, true_positives, false_negatives], fpr, fdr

def create_sankey(phi, alpha, beta):
    labels = [
        "False Ideas (H₀ true)", "True Ideas (H₁ true)",
        "False Positives (α)", "True Negatives",
        "True Positives (Power)", "False Negatives (β)"
    ]
    
    source = [0, 0, 1, 1]
    target = [2, 3, 4, 5]
    values, fpr, fdr = compute_values(phi, alpha, beta)
    
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=20,
            label=labels,
            x=[0, 0, 0.5, 0.5, 1, 1],
            y=[0.2, 0.8, 0, 0.4, 0.6, 1]
        ),
        link=dict(
            source=source,
            target=target,
            value=values
        )
    ))
    
    fig.add_annotation(x=0.5, y=-0.2, text=f"FPR: {fpr:.3f} | FDR: {fdr:.3f}",
                       showarrow=False, font=dict(size=14, color="black"))
    
    return fig

st.title("Hypothesis Testing Sankey Diagram")

phi = st.slider("Proportion of False Ideas", 0.1, 0.9, 0.5, 0.01)
alpha = st.slider("False Positive Rate (α)", 0.01, 0.1, 0.05, 0.01)
beta = st.slider("False Negative Rate (β)", 0.01, 0.5, 0.2, 0.01)

st.plotly_chart(create_sankey(phi, alpha, beta))

st.write("Adjust the sliders to see how experiment settings impact outcomes.")
