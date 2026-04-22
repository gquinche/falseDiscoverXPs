import streamlit as st
import plotly.graph_objects as go

# Initialize session state
if "initial_phi" not in st.session_state:
    st.session_state.initial_phi = 0.8  # Default value

initial_alpha = 0.05
initial_beta = 0.5
max_phi = 1.0

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
        "False Positives ", "True Negatives",
        "True Positives ", "False Negatives"
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

    fig.add_annotation(x=0.5, y=-0.1, text=f" FDR: {fdr:.1f}% (red to green ratio)", 
                       showarrow=False, font=dict(size=14, color="white"),
                       bgcolor="black", bordercolor="white", borderwidth=2)

    return fig, fdr / 100

# **Define placeholders to control layout**

st.markdown("""
# **Understanding Scientific Criticism and p-Values**

Scientific research has faced scrutiny due to reproducibility issues, often tied to the widespread use of the **0.05 significance threshold** for p-values. When many tested hypotheses are false, **false discoveries** (statistically significant but incorrect results) become more frequent. This challenges the misconception that 95% (1 - 0.05) of statistically significant results are true.

In this app, you can visualize an estimation of the number of false discoveries based on your chosen significance level, statistical power, and the proportion of true ideas. Additionally, we explore how the impact of false discoveries depends on **how the results are applied**.

## **What Is a "False Positive"?**

A common misunderstanding is equating the **false positive rate (FPR)** with the probability that a statistically significant result is actually false, which is the **false discovery rate (FDR)**. These are **not the same**:

- **False Positive Rate (FPR):** The probability of detecting an effect **when none exists**. This is directly controlled by **α** (e.g., 0.05) and is calculated as:
""")
st.latex(r"FPR = \frac{\text{False Positives}}{\text{False Positives} + \text{True Negatives}}")

st.markdown("""
- **False Discovery Rate (FDR):** The proportion of statistically significant results that are actually false positives. This depends on **α**, statistical power, and the proportion of true hypotheses, and is calculated as:
""")
st.latex(r"FDR = \frac{\text{False Positives}}{\text{False Positives} + \text{True Positives}}")
st.markdown("""
## **Why FDR Matters**


When evaluating an impressive result—whether in a research study or a company experiment—you are actually concerned with **FDR**, not FPR. Only when experiments are designed with high statistical power and strong hypotheses does **FPR approximate FDR**, meaning a 5% significance threshold could translate into a 95% probability that a result is real.

For teams making **investment decisions** or **long-term plans** based on experimental results, **FDR is critical**. In speculative research, where many tested ideas are false, **FDR can be as much as 4 times α**, meaning 20% of discoveries are false even with α set at 0.05.

            

People often confuse FPR and FDR because both use false positives in the numerator and their namings, but their denominators differ. This app focuses on **FDR**, clarifying that **α alone does not determine the number of false discoveries** in an experiment.
One could argue that FDR is more relevant for the general public as it allows them to quantify how much a experiment in science or technology should make them adjust their beliefs, whereas alpha is more relevant
 for the researchers as it influences policies related to getting published, product launches etc.

The graph below illustrates how the proportion of false ideas, significance level, and statistical power influence the number of false discoveries, represented by the red-to-green ratio.
            """)


graph_placeholder = st.empty()   # Placeholder for graph (top)
slider_placeholder = st.empty()  # Placeholder for sliders (bottom)
st.text(f"You can simulate rerunning the XP and updating the prior (or false idea probability) using the FDR, this shows the importance of replication, as it make us more and more certain with each rerun..""")
button_placeholder = st.empty()  # Placeholder for "Repeat XP" button (middle)
# **Sliders (keep them together in a container)**
with slider_placeholder.container():
    phi = st.slider("Proportion of False Ideas Φ", 0.0, max_phi, st.session_state.initial_phi, 0.01)
    alpha = st.slider("Significance Level (α)", 0.01, 0.1, initial_alpha, 0.01)
    beta = 1 - st.slider("Power (1-β)", 0.1, 1.0, 1-initial_beta, 0.01)

# **Generate the graph**
plot, fdr = create_sankey(phi, alpha, beta)
graph_placeholder.plotly_chart(plot)  # Graph appears first

# **Button (below graph)**
with button_placeholder:
    if st.button("Simulate rerunning stat sig XP"):
        st.session_state.initial_phi = min(fdr, max_phi)


st.markdown("""

## **When Is Power Less Critical?** 🔑  

Many teams avoid power analysis or lack sufficient power to approximate the 5% FDR they believe they achieve. While this isn't ideal, it is better to experiment than not experiment at all. If experiments are primarily used to prevent harmful changes (e.g., rolling back features with significant negative impact), false discoveries are often low-cost and reversible. This makes FDR less of a concern because:

- Negative false discoveries are likely neutral or slightly negative, rather than truly beneficial.
- Rolling back a feature doesn’t waste significant resources, unlike scaling up a false discovery as a "win."

### **Takeaways for Experimentation**
- **If experiments guide major investments or product launches**, controlling FDR is crucial to avoid wasted resources.
- **If experiments primarily prevent harm**, running tests—even with imperfect power—is better than making blind decisions.

### **Context in Tech-Led Experiments**

In technology-driven experimentation, the primary goal is to learn quickly and iterate. Unlike scientific research—where most investment happens after validation—product development often involves significant effort before an experiment is conducted.

This changes the implications of false discoveries:

- False discoveries are less costly since the product is already developed.
- Misinformation and usage can be corrected quickly through centralized means.
- Scaling false discoveries often leads to neutral, rather than negative, outcomes.
- Most experiments test **incremental improvements** with fewer ethical implications.

### **Is α Too High?**

The choice of α is still a debated topic. Some fields, like physics and genomics, have adopted much lower α thresholds, while online experimentation services often use higher values (e.g., up to 0.2).

### **Conclusion**

Not all false discoveries are equally harmful—what matters is how they shape decisions. This app demonstrates how false idea proportions, significance levels, and statistical power influence false discovery rates. Use this tool to understand trade-offs in experimental design and balance statistical rigor with practical decision-making.""")


import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from math import erf, sqrt

# Approximation of inverse error function (erfinv)
def erfinv_approx(x):
    a = 0.147
    sign = 1 if x >= 0 else -1
    ln = np.log(1 - x ** 2)
    part1 = 2 / (np.pi * a) + ln / 2
    part2 = (ln / a) + np.sqrt((ln / a) ** 2 + (2 / a) * ln)
    return sign * np.sqrt(np.sqrt(part1 ** 2 - part2) - part1)

# Normal CDF using error function
def norm_cdf(x, mean, std):
    return 0.5 * (1 + erf((x - mean) / (std * sqrt(2))))

# Normal PPF (inverse CDF)
def norm_ppf(p, mean, std):
    return mean + std * sqrt(2) * erfinv_approx(2 * p - 1)

# Generate normal distributions
def plot_power(mean_diff, sample_size, std_ratio):
    base_std = 2  # Increased baseline std to avoid pulse-like effect
    std1 = base_std * std_ratio  # Apply std_ratio to both groups
    std2 = base_std * std_ratio

    se1 = std1 / sqrt(sample_size)  # Standard error for both groups
    se2 = std2 / sqrt(sample_size)

    x = np.linspace(-3, mean_diff + 3, 1000)
    dist1 = np.exp(-0.5 * ((x - 0) / se1) ** 2) / (se1 * np.sqrt(2 * np.pi))
    dist2 = np.exp(-0.5 * ((x - mean_diff) / se2) ** 2) / (se2 * np.sqrt(2 * np.pi))

    # Compute critical value and power
    alpha = 0.05
    critical_value = norm_ppf(1 - alpha, 0, se1)
    power = 1 - norm_cdf(critical_value, mean_diff, se2)

    plt.figure(figsize=(7, 5))
    plt.plot(x, dist1, label="Sample Mean 1 (Control)", color="blue")
    plt.plot(x, dist2, label="Sample Mean 2 (Treatment)", color="red")
    plt.axvline(critical_value, linestyle="dashed", color="black", label="Critical Value")
    plt.axvline(mean_diff, linestyle="dotted", color="green", label="ATE (Effect Size)")
    plt.fill_between(x, dist2, where=x > critical_value, color="red", alpha=0.3, label="Power (1-β)")
    plt.legend()
    plt.xlabel("Sample Mean")
    plt.ylabel("Density")
    plt.title(f"Power Visualization\nATE = {mean_diff:.2f}, Power = {power:.2f}")
    st.pyplot(plt)

# Streamlit UI
st.title("Power Visualizer WIP")

mean_diff = st.slider("Mean Difference (Effect Size)", 0.1, 3.0, 0.6, 0.1)
sample_size = st.slider("Sample Size per Group", 1000, 100000, 1000, 10)  # Lowered min sample size for more flexibility
std_ratio = st.slider("Std Ratio (Variance Ratio)", 0.5, 4.0, 3.0, 0.1)
st.markdown(" Power is the proportion or probability of measuring a difference over a setted threshold when there's actually a difference")
plot_power(mean_diff, sample_size, std_ratio)
st.markdown("""
### **Citations**  

- **Redefine Statistical Significance**  
  Daniel J. Benjamin, James O. Berger, Magnus Johannesson et al.  
  [https://www.nature.com/articles/s41562-017-0189-z.pdf](https://www.nature.com/articles/s41562-017-0189-z.pdf)

- **False Positives in A/B Tests**  
  Kohavi, Chen (2024).  
  [https://doi.org/10.1145/3637528.3671631](https://doi.org/10.1145/3637528.3671631)
""")