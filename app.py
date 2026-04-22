import streamlit as st
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import t
import plotly.express as px
from plotly.subplots import make_subplots

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

st.markdown("---")
st.markdown("# 🎯 Power Analysis: Beyond the Textbook")
st.markdown("Understanding p-values as random variables and the hidden cost of heterogeneity")

st.markdown('''
<style>
    .discovery-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .warning-box {
        background: #fff3cd;
        padding: 15px;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
''', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🎓 Discovery 1: P-Values Are Random",
    "📊 Discovery 2: MDE ≠ p=0.05",
    "⚠️ Discovery 3: Heterogeneity Tax",
    "💡 Implementation Guide"
])

with tab1:
    st.markdown('''
    ## Discovery 1: P-Values Are Random Variables

    The standard textbook presentation hides a critical insight: **p-values aren't fixed — they're random.**
    Every time you run an experiment, you get a different p-value because you're sampling from random distributions.
    ''')

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Parameters")
        n = st.slider("Sample size per group", 20, 500, 100, key="n_tab1")
        true_effect = st.slider("True effect (MDE)", 0.0, 2.0, 0.5, step=0.1, key="te_tab1")
        num_sims = st.slider("Simulations", 1000, 10000, 5000, key="ns_tab1")

    with col2:
        st.markdown("### What's Happening")
        st.info('''
        Each simulation:
        1. **Sample** from two groups (control + treatment shifted by MDE)
        2. **Calculate** t-statistic from the sample data
        3. **Convert** to p-value using the t-distribution

        The **histogram shows**: p-values bounce around because sampling is random, not fixed.
        ''')

    # Run simulation
    p_values = []
    for _ in range(num_sims):
        sample1 = np.random.normal(0, 1, n)
        sample2 = np.random.normal(true_effect, 1, n)

        t_stat = (np.mean(sample2) - np.mean(sample1)) / (np.sqrt(2/n))
        p_val = 2 * (1 - t.cdf(np.abs(t_stat), df=2*n-2))
        p_values.append(p_val)

    p_values = np.array(p_values)

    # Create visualization
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=p_values,
        nbinsx=50,
        name='P-value distribution',
        marker_color='#667eea',
        opacity=0.8
    ))

    fig.add_vline(x=0.05, line_dash="dash", line_color="red",
                  annotation_text="α = 0.05", annotation_position="top right")

    power = np.mean(p_values < 0.05)
    fig.add_vline(x=np.median(p_values), line_dash="dot", line_color="green",
                  annotation_text=f"Median p = {np.median(p_values):.4f}",
                  annotation_position="top left")

    fig.update_layout(
        title=f"Distribution of P-Values (Power = {power:.1%})",
        xaxis_title="P-Value",
        yaxis_title="Frequency",
        height=500,
        template="plotly_white",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Power (% < 0.05)", f"{power:.1%}")
    col2.metric("Median p-value", f"{np.median(p_values):.4f}")
    col3.metric("Min p-value", f"{np.min(p_values):.4f}")
    col4.metric("Max p-value", f"{np.max(p_values):.4f}")

    # Source code
    with st.expander("📝 View Simulation Code"):
        st.code('''
p_values = []
for _ in range(num_simulations):
    sample1 = np.random.normal(0, 1, n)
    sample2 = np.random.normal(true_effect, 1, n)

    # Explicit t-statistic calculation
    t_stat = (np.mean(sample2) - np.mean(sample1)) / (np.sqrt(2/n))

    # Convert to p-value
    p_val = 2 * (1 - t.cdf(np.abs(t_stat), df=2*n-2))
    p_values.append(p_val)

# Result: p-values are random, not fixed!
power = np.mean(np.array(p_values) < 0.05)
        ''', language="python")


with tab2:
    st.markdown('''
    ## Discovery 2: Measuring Exactly the MDE Does NOT Give p = 0.05

    **Flashcard Answer:** No. When you observe data where the true effect equals MDE,
    the p-value is ~0.005, not 0.05. This is because MDE is a "safe bet" against unlucky sampling.
    ''')

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Parameters")
        n2 = st.slider("Sample size per group", 20, 500, 100, key="n2")
        mde = st.slider("MDE value", 0.1, 2.0, 0.5, step=0.1, key="mde")
        num_sims2 = st.slider("Simulations", 1000, 10000, 5000, key="sims2")

    with col2:
        st.markdown("### The Key Insight")
        st.warning('''
        **Why is the p-value so small when effect = MDE?**

        MDE is designed so that 80% of the time, you *exceed* the rejection threshold.
        This means:
        - The median p-value is much smaller than 0.05
        - Only 20% of experiments fail to reject
        - You're typically far into the rejection region
        ''')

    # Simulation
    p_values2 = []
    for _ in range(num_sims2):
        sample1 = np.random.normal(0, 1, n2)
        sample2 = np.random.normal(mde, 1, n2)

        t_stat = (np.mean(sample2) - np.mean(sample1)) / (np.sqrt(2/n2))
        p_val = 2 * (1 - t.cdf(np.abs(t_stat), df=2*n2-2))
        p_values2.append(p_val)

    p_values2 = np.array(p_values2)

    # Theoretical p-value at MDE
    t_stat_mde = mde / (np.sqrt(2/n2))
    p_val_mde = 2 * (1 - t.cdf(np.abs(t_stat_mde), df=2*n2-2))

    # Visualization
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=p_values2,
        nbinsx=50,
        name='Simulated p-values',
        marker_color='#667eea',
        opacity=0.8
    ))

    fig.add_vline(x=0.05, line_dash="dash", line_color="red",
                  annotation_text="α = 0.05", annotation_position="top right")

    fig.add_vline(x=p_val_mde, line_dash="solid", line_color="green", line_width=3,
                  annotation_text=f"Theoretical p at MDE = {p_val_mde:.4f}",
                  annotation_position="top left")

    fig.update_layout(
        title=f"When True Effect = MDE (Power = {np.mean(p_values2 < 0.05):.1%})",
        xaxis_title="P-Value",
        yaxis_title="Frequency",
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Theoretical p at MDE", f"{p_val_mde:.6f}")
    col2.metric("Median simulated p", f"{np.median(p_values2):.6f}")
    col3.metric("Ratio (Median/Theory)", f"{np.median(p_values2)/p_val_mde:.2f}x")

    st.markdown('''
    ### Why This Matters

    The **0.05 threshold is a boundary**, not a typical value. When your effect truly equals MDE:
    - You're typically **far past** that boundary
    - Most p-values cluster around 0.001–0.01
    - Only ~20% fail to reject (your Type II error rate)

    This is why power ≠ "achieving p=0.05" — it's about consistency of detection.
    ''')

    with st.expander("📝 View Calculation Code"):
        st.code('''
# Theoretical p-value at MDE
t_stat_mde = MDE / sqrt(2/n)
p_val_mde = 2 * (1 - cdf_t(|t_stat_mde|, df=2n-2))

# Result: p ≈ 0.005, not 0.05!
# This is the "safe bet" — you're not at the threshold,
# you're well into the rejection region.
        ''', language="python")


with tab3:
    st.markdown('''
    ## Discovery 3: The Hidden Cost of Heterogeneity

    **The Problem:** Standard power calculations assume **constant treatment effects** across all units.
    In reality, effects are heterogeneous — some people respond more, some less, some negatively.

    **The Consequence:** Heterogeneity increases noise, reducing power without adjustment.
    ''')

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Setup")
        n3 = st.slider("Sample size per group", 20, 500, 100, key="n3")
        true_effect3 = st.slider("Average treatment effect", 0.1, 2.0, 0.5, step=0.1, key="effect3")
        sigma_het = st.slider("Heterogeneity (σ of effect)", 0.0, 1.5, 0.0, step=0.1, key="het")
        num_sims3 = st.slider("Simulations", 1000, 10000, 5000, key="sims3")

    with col2:
        st.markdown("### What Changes")
        st.info('''
        **Homogeneous (σ_het = 0):**
        Everyone shifts by exactly the true effect.

        **Heterogeneous (σ_het > 0):**
        Effects vary by person: N(true_effect, σ_het²)

        **Result:**
        Total noise increases → t-statistic shrinks → power drops
        ''')

    # Run both scenarios
    scenarios = {}

    for scenario_name, het_std in [("Homogeneous", 0.0), ("Heterogeneous", sigma_het)]:
        p_vals = []
        for _ in range(num_sims3):
            sample1 = np.random.normal(0, 1, n3)

            if het_std > 0:
                # Heterogeneous: each person gets different effect
                individual_effects = np.random.normal(true_effect3, het_std, n3)
                sample2 = sample1 + individual_effects
            else:
                # Homogeneous: everyone gets same effect
                sample2 = sample1 + true_effect3

            t_stat = (np.mean(sample2) - np.mean(sample1)) / (np.sqrt(2/n3))
            p_val = 2 * (1 - t.cdf(np.abs(t_stat), df=2*n3-2))
            p_vals.append(p_val)

        scenarios[scenario_name] = np.array(p_vals)

    # Comparison plot
    fig = go.Figure()

    colors = {'Homogeneous': '#667eea', 'Heterogeneous': '#f56565'}
    for scenario_name, p_vals in scenarios.items():
        fig.add_trace(go.Histogram(
            x=p_vals,
            nbinsx=50,
            name=scenario_name,
            marker_color=colors[scenario_name],
            opacity=0.7
        ))

    fig.add_vline(x=0.05, line_dash="dash", line_color="red",
                  annotation_text="α = 0.05", annotation_position="top right")

    fig.update_layout(
        title="Impact of Heterogeneity on P-Value Distribution",
        xaxis_title="P-Value",
        yaxis_title="Frequency",
        barmode='overlay',
        height=500,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Metrics comparison
    col1, col2, col3 = st.columns(3)

    homo_power = np.mean(scenarios['Homogeneous'] < 0.05)
    het_power = np.mean(scenarios['Heterogeneous'] < 0.05)
    power_loss = homo_power - het_power

    col1.metric("Homogeneous Power", f"{homo_power:.1%}")
    col2.metric("Heterogeneous Power", f"{het_power:.1%}")
    col3.metric("Power Lost", f"{power_loss:.1%}", delta=f"-{power_loss:.1%}")

    if sigma_het > 0:
        st.markdown(f'''
        ### The Heterogeneity Tax

        By introducing effect heterogeneity (σ = {sigma_het:.2f}):
        - **Power dropped by {power_loss:.1%}**
        - To recover power, you'd need a larger sample size
        - This cost is **hidden in standard power calculations**

        **Required sample size multiplier to recover power:**
        ''')

        # Estimate required multiplier
        required_mult = (homo_power / het_power) ** 2 if het_power > 0 else float('inf')
        if required_mult < 10:
            st.warning(f"≈ {required_mult:.2f}x (roughly {int(n3 * required_mult)} instead of {n3})")
        else:
            st.error(f"Power unrecoverable with reasonable sample size increase")

    st.markdown('''
    ### Why This Matters for Your Experiment

    **The textbook assumes:**
    - One fixed "treatment effect" applies to everyone
    - Only source of randomness is sampling variation

    **Reality:**
    - Some subgroups respond differently
    - Treatment effect itself is random across units
    - This adds to total variance

    **Solution:**
    - Estimate effect heterogeneity from pilot data
    - Use σ_het in power calculations: σ_total² = σ_pop² + σ_het²
    - Design for realistic variance, not idealised variance
    ''')

    with st.expander("📝 View Heterogeneity Code"):
        st.code('''
# Homogeneous: everyone shifts by same amount
sample2_homo = sample1 + true_effect

# Heterogeneous: each person shifts by different amount
individual_effects = np.random.normal(true_effect, sigma_het, n)
sample2_het = sample1 + individual_effects

# Both are averaged, but het has more variance
# → smaller t-statistic
# → lower power
        ''', language="python")

with tab4:
    st.markdown('''
    ## 💡 Implementation Guide: Better Power Analysis

    ### Summary of Discoveries
    ''')

    st.markdown('''
    <div class="discovery-box">
    <h4>Discovery 1: P-Values Are Random</h4>
    <p>P-values are not fixed — they're random variables that change each time you sample.
    This is why power is probabilistic, not deterministic.</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="discovery-box">
    <h4>Discovery 2: MDE ≠ p=0.05</h4>
    <p>When your true effect equals the MDE, you don't get p=0.05. Instead, p≈0.005 because
    MDE is a "safe bet" — it's designed so you reject H₀ 80% of the time, well past the threshold.</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="discovery-box">
    <h4>Discovery 3: Heterogeneity Tax</h4>
    <p>Standard power calculations hide the cost of heterogeneous treatment effects.
    Real effects vary by person, increasing total noise and reducing achievable power.</p>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Practical Workflow for Better Power Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('''
        #### Step 1: Know Your Parameters

        Before power analysis, you need:
        - **Effect size (MDE):** What's the smallest effect worth detecting?
        - **Baseline variance (σ):** Variability in control group
        - **Heterogeneity (σ_het):** Does effect vary by subgroup/person?
        - **Sample size (n):** Practical constraints

        **How to estimate σ_het:**
        - Pilot study with small sample
        - Historical data from similar experiments
        - Theory or subject matter expertise
        ''')

    with col2:
        st.markdown('''
        #### Step 2: Calculate Corrected Power

        **Standard (naive):**
        ```
        σ_total = σ_baseline
        Power = f(MDE, σ_total, n)
        ```

        **Corrected:**
        ```
        σ_total = sqrt(σ_baseline² + σ_het²)
        Power = f(MDE, σ_total, n)
        ```

        The extra term σ_het² accounts for effect variability.
        ''')

    st.markdown("---")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('''
        #### Step 3: Simulate Before Running

        Don't trust formulas — simulate:
        ```python
        p_values = []
        for i in range(10000):
            # Sample from your realistic scenario
            control = normal(0, sigma_baseline, n)
            effect = normal(mde, sigma_het, n)
            treated = control + effect

            # Calculate p-value
            t_stat = (mean(treated) - mean(control)) / SE
            p_val = cdf_to_pvalue(t_stat)
            p_values.append(p_val)

        power = mean(p_values < 0.05)
        ```
        ''')

    with col2:
        st.markdown('''
        #### Step 4: Sensitivity Analysis

        Test across reasonable ranges:
        - ±10% variance estimates
        - ±20% effect size uncertainty
        - Different subgroup compositions

        **Report:**
        - Best case power (optimistic assumptions)
        - Realistic power (honest estimates)
        - Worst case power (conservative)

        Design for **realistic** or **conservative**, not best case.
        ''')

    st.markdown("---")

    st.markdown('''
    ### Complete Python Template
    ''')

    with st.expander("📋 Full Implementation Template"):
        st.code("""
import numpy as np
from scipy.stats import t

def power_analysis_with_heterogeneity(
    mde, sigma_baseline, sigma_het, n, num_sims=10000
):
    '''
    Calculate power accounting for heterogeneous treatment effects.

    Args:
        mde: Minimum detectable effect (average treatment effect)
        sigma_baseline: Baseline variance in control
        sigma_het: Standard deviation of treatment effect across units
        n: Sample size per group
        num_sims: Number of simulations

    Returns:
        power, median_p_value, p_value_distribution
    '''
    p_values = []

    for _ in range(num_sims):
        # Sample control group
        control = np.random.normal(0, sigma_baseline, n)

        # Sample treatment effects (heterogeneous)
        effects = np.random.normal(mde, sigma_het, n)
        treated = control + effects

        # Calculate t-statistic
        t_stat = (np.mean(treated) - np.mean(control)) / np.sqrt(2 * (np.var(control) + np.var(treated)) / (2*n))

        # Convert to p-value
        p_val = 2 * (1 - t.cdf(np.abs(t_stat), df=2*n-2))
        p_values.append(p_val)

    p_values = np.array(p_values)
    power = np.mean(p_values < 0.05)

    return {
        'power': power,
        'median_p_value': np.median(p_values),
        'p_values': p_values,
        'type2_error': 1 - power
    }

# Example usage
result = power_analysis_with_heterogeneity(
    mde=0.5,
    sigma_baseline=1.0,
    sigma_het=0.3,        # ← This is the key new parameter!
    n=100,
    num_sims=10000
)

print(f"Power: {result['power']:.1%}")
print(f"Type II error: {result['type2_error']:.1%}")
print(f"Median p-value: {result['median_p_value']:.4f}")
        """, language="python")

    st.markdown("---")
    st.markdown('''
    ### Key Takeaways

    1. **P-values are random** — expect variation across experiments
    2. **MDE is not p=0.05** — it's a "safe bet" with median p≈0.005
    3. **Heterogeneity is real** — estimate it and include it in power calculations
    4. **Simulate > formulas** — match realistic assumptions
    5. **Design for realistic variance** — not best-case scenarios
    ''')

st.markdown("""
### **Citations**  

- **Redefine Statistical Significance**  
  Daniel J. Benjamin, James O. Berger, Magnus Johannesson et al.  
  [https://www.nature.com/articles/s41562-017-0189-z.pdf](https://www.nature.com/articles/s41562-017-0189-z.pdf)

- **False Positives in A/B Tests**  
  Kohavi, Chen (2024).  
  [https://doi.org/10.1145/3637528.3671631](https://doi.org/10.1145/3637528.3671631)
""")