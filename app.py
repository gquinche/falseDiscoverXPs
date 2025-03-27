import streamlit as st
import plotly.graph_objects as go

def compute_values(phi, alpha, beta):
    false_ideas = phi
    true_ideas = 1 - phi
    
    false_positives = alpha * false_ideas
    true_negatives = (1 - alpha) * false_ideas
    true_positives = (1 - beta) * true_ideas
    false_negatives = beta * true_ideas
    
    fpr = (false_positives / (false_positives + true_negatives) * 100) if (false_positives + true_negatives) > 0 else 0
    fdr = (false_positives / (false_positives + true_positives) * 100) if (false_positives + true_positives) > 0 else 0
    
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
            pad=20, thickness=25,
            label=labels,
            x=[0.1, 0.1, 0.4, 0.4, 0.8, 0.8],
            y=[0.2, 0.8, 0, 0.4, 0.6, 1],
            color=["blue", "darkblue", "red", "gray", "green", "teal"]
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=["rgba(255,0,0,0.5)", "rgba(150,150,150,0.5)",
                   "rgba(0,255,0,0.5)", "rgba(0,150,150,0.5)"]
        )
    ))

    fig.add_annotation(x=0.5, y=-0.1, text=f" FDR: {fdr:.1f}%", 
                       showarrow=False, font=dict(size=14, color="white"),
                       bgcolor="black", bordercolor="white", borderwidth=2)

    return fig

st.title("XPs False Discovery Rate")

st.markdown("""
# **Why Experimentation Matters & How to Use It Wisely**  

Science has faced scrutiny due to reproducibility issues, often linked to the widespread use of the **0.05 significance threshold**. When many tested ideas are false, **false positives** (statistically significant but incorrect results) become more common. However, the impact of false positives depends on **how results are used**.

## **What Do We Mean by "False Positives"?**  
A common misunderstanding is equating **false positive rate (FPR)** with the probability that a given statistically significant result is actually false. These are **not the same**:

- **False Positive Rate (FPR):** The probability that a test detects an effect **when there is none** (controlled directly by α, e.g., 0.05).
            False Positives / False Positives + True negatives  
- **False Discovery Rate (FDR):** The proportion of statistically significant results that are actually false positives. This depends **not just on α, but also on power and how many tested hypotheses are actually true**.
            False Positives / False Positives + **True positives**  

When you are looking at an incredible result and wondering if it is real (in your company or on scientific literature), you are wondering about FDR, and not about the FPR. Only when you are very diligent on what you test and the power of the XP does FPR approximate FDR.

For teams making **investment decisions** based on experiment results, **FDR is what matters**—because it tells us how often we’re acting on misleading results. If many tested ideas are false (which is common in speculative research), then **FDR can be much higher than 0.05, even if α is set at 0.05**.
""")

phi = st.slider("Proportion of False Ideas", 0.1, 0.9, 0.8, 0.01)
alpha = st.slider("Significance Level (α)", 0.01, 0.1, 0.05, 0.01)
beta = 1 - st.slider("Power (1-β)", 0.1, 1.0, 0.6, 0.01)

st.plotly_chart(create_sankey(phi, alpha, beta))
st.markdown("""
## **When Is Power Less Critical? 🔑**  

Many teams avoid power analysis, but this **isn’t always a major issue**. If experiments are used **mainly to prevent bad changes** (e.g., rolling back features that show significant negative impact), then false positives are **low-cost and reversible**. This makes **FDR less of a concern** because:

1. **Most false positives are neutral or slightly negative, not truly beneficial.**  
2. **Rolling back a feature doesn’t waste significant resources**, unlike scaling up a false positive as a "win."  

## **Takeaway for Experimentation**  
- **If you’re using experiments for launching & investing in new ideas**, controlling FDR is crucial to avoid wasting resources.  
- **If you’re using experiments to prevent harm**, running XPs without perfect power is still better than launching blindly.  

###  Context in Tech-Led Experiments
In tech-driven experimentation, the goal often extends beyond binary success or failure—it's about learning quickly and iterating. Unlike scientific research, where most investment happens after an idea is validated, in product development, a significant portion of the opportunity cost is already sunk by the time an experiment is launched.

This changes the implications of false positives:

- Higher α can accelerate iteration, accepting more false positives but enabling teams to quickly discard bad ideas.

- False positives may not be as harmful as they probably lead to neutral (rather than negative) outcomes.

- Most experiments test incremental improvements, so even true negatives (ideas that don't work) provide valuable insights for refining future tests.

However, when experiments directly influence business investment decisions, FDR remains crucial. If a team prioritizes speed but lacks a structured approach to filter out false discoveries post-experiment, they risk scaling misleading results.

In short: **Not all false positives are equally harmful—what matters is how they shape decisions.**

### **Citations**  
Redefine statistical significance:  
We propose to change the default P-value threshold for statistical significance from 0.05 to 0.005 for claims of new discoveries.  
Daniel J. Benjamin, James O. Berger, Magnus Johannesson et al.  
[https://www.nature.com/articles/s41562-017-0189-z.pdf](https://www.nature.com/articles/s41562-017-0189-z.pdf)

False Positives in A/B Tests:  
© Kohavi, Chen 2024. This is the author's version of the work. It is posted here for your personal use. Not for redistribution.  
The definitive version was published in KDD 2024 at [https://doi.org/10.1145/3637528.3671631](https://doi.org/10.1145/3637528.3671631)  
Ron Kohavi, Los Altos, CA, USA, ronnyk@live.com  
Nanyu Chen, Expedia Group, San Francisco, CA, USA, nc361sirg@gmail.com  
""")

