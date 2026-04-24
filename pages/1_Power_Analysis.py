import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import t
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="Power Analysis & Heterogeneity", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        max-width: 1400px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        padding: 12px 24px;
    }
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
""", unsafe_allow_html=True)

st.title("🎯 Power Analysis: Beyond the Textbook")
st.markdown("Understanding p-values as random variables and the hidden cost of heterogeneity")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎓 Discovery 1: P-Values Are Random",
    "📊 Discovery 2: MDE ≠ p=0.05",
    "⚠️ Discovery 3: Heterogeneity Tax",
    "💡 Implementation Guide",
    "📝 Quick Summary"
])

with tab1:
    st.markdown("""
    ## Discovery 1: P-Values Are Random Variables

    The standard textbook presentation hides a critical insight: **p-values aren't fixed — they're random.**
    Every time you run an experiment, you get a different p-value because you're sampling from random distributions.
    """)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Parameters")
        n = st.slider("Sample size per group", 20, 500, 100, key="n_tab1")
        true_effect = st.slider("True effect (MDE)", 0.0, 2.0, 0.5, step=0.1, key="te_tab1")
        num_sims = st.slider("Simulations", 1000, 10000, 5000, key="ns_tab1")

    with col2:
        st.markdown("### What's Happening")
        st.info("""
        **Question: Where does randomness in power come from?**

        Answer: From sampling. You draw two random samples, compute a t-statistic, and convert it to a p-value. Every sample produces a different p-value.

        Each simulation:
        1. **Sample 1** from Group A → different each time
        2. **Sample 2** from Group B → different each time
        3. **Calculate** t-statistic = different each time
        4. **Convert** to p-value = different each time

        The **histogram shows**: p-values bounce around because sampling is random, not fixed.
        **Key Insight:** Power = % of experiments where p < 0.05
        """)

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
        st.code("""
p_values = []
for i in range(10000):
    group1 = np.random.normal(0, 1, n=100)
    group2 = np.random.normal(0.5, 1, n=100)  # effect = 0.5

    # Explicit t-statistic calculation
    t_stat = (np.mean(group2) - np.mean(group1)) / (np.sqrt(2/n)) # SE

    # Convert to p-value
    p_val = 2 * (1 - t.cdf(np.abs(t_stat), df=2*n-2))
    p_values.append(p_val)

# Result: p-values are random, not fixed!
power = np.mean(np.array(p_values) < 0.05)
        """, language="python")

with tab2:
    st.markdown("""
    ## Discovery 2: Measuring Exactly the MDE Does NOT Give p = 0.05

    **Question: Does measuring exactly the MDE give p = 0.05?**

    **Flashcard Answer:** No. p ≈ 0.005 (not 0.05). When you observe data where the true effect equals MDE, the p-value is ~0.005, not 0.05. This is because MDE is a "safe bet" against unlucky sampling.
    """)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Parameters")
        n2 = st.slider("Sample size per group", 20, 500, 100, key="n2")
        mde = st.slider("MDE value", 0.1, 2.0, 0.5, step=0.1, key="mde")
        num_sims2 = st.slider("Simulations", 1000, 10000, 5000, key="sims2")

    with col2:
        st.markdown("### The Key Insight")
        st.warning("""
        **Why is the p-value so small when effect = MDE?**

        MDE is designed so that 80% of the time, you *exceed* the rejection threshold.
        This means:
        - The median p-value is much smaller than 0.05 (~0.005)
        - Only 20% of experiments fail to reject
        - You're typically far into the rejection region

        **The 0.05 threshold is a boundary, not a typical value.**
        """)

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

    st.markdown("""
    ### Why This Matters

    The **0.05 threshold is a boundary**, not a typical value. When your effect truly equals MDE:
    - You're typically **far past** that boundary
    - Most p-values cluster around 0.001–0.01
    - Only ~20% fail to reject (your Type II error rate)

    This is why power ≠ "achieving p=0.05" — it's about consistency of detection.
    """)

    with st.expander("📝 View Calculation Code"):
        st.code("""
# Theoretical p-value at MDE
t_stat_mde = MDE / sqrt(2/n)
p_val_mde = 2 * (1 - cdf_t(abs(t_stat_mde), df=2n-2))

# Result: p ≈ 0.005, not 0.05!
# This is the "safe bet" — you're not at the threshold,
# you're well into the rejection region.
        """, language="python")

with tab3:
    st.markdown("""
    ## Discovery 3: The Hidden Cost of Heterogeneity

    **Question: How does effect variability affect power?**
    **Answer:** It reduces power without adjustment.

    **The Problem:** Standard power calculations assume **constant treatment effects** across all units.
    In reality, effects are heterogeneous — some people respond more, some less, some negatively.

    **The Consequence:** Heterogeneity increases noise, reducing power without adjustment.
    """)

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("### Setup")
        n3 = st.slider("Sample size per group", 20, 500, 100, key="n3")
        true_effect3 = st.slider("Average treatment effect", 0.1, 2.0, 0.5, step=0.1, key="effect3")
        sigma_het = st.slider("Heterogeneity (σ of effect)", 0.0, 1.5, 0.3, step=0.1, key="het")
        num_sims3 = st.slider("Simulations", 1000, 10000, 5000, key="sims3")

    with col2:
        st.markdown("### What Changes")
        st.info("""
        **Textbook assumes (Homogeneous):**
        - Sample 1: all values from N(0, σ²)
        - Sample 2: all values from N(MDE, σ²)
        - simple model!

        **Reality (Heterogeneous):**
        - Treatment effect varies by person
        - Sample 2: N(0, σ²) + N(MDE, σ_het²)

        **Result:**
        Total noise increases → t-statistic shrinks → power drops
        """)

        st.markdown("""
        ### The Math (Heterogeneity Tax)
        **Standard (naive):**
        `σ_total² = σ_baseline²`

        **Corrected:**
        `σ_total² = σ_baseline² + σ_het²`
        """)

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
        st.markdown(f"""
        ### The Heterogeneity Tax

        By introducing effect heterogeneity (σ = {sigma_het:.2f}):
        - **Power dropped by {power_loss:.1%}**
        - To recover power, you'd need a larger sample size
        - This cost is **hidden in standard power calculations**

        **Required sample size multiplier to recover power:**
        """)

        # Estimate required multiplier
        required_mult = (homo_power / het_power) ** 2 if het_power > 0 else float('inf')
        if required_mult < 10:
            st.warning(f"≈ {required_mult:.2f}x (roughly {int(n3 * required_mult)} instead of {n3})")
        else:
            st.error(f"Power unrecoverable with reasonable sample size increase")

    st.markdown("""
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
    """)

    with st.expander("📝 View Heterogeneity Code"):
        st.code("""
# Naive (textbook)
effect = 0.5
sample2 = sample1 + effect

# Realistic (with heterogeneity)
effects = np.random.normal(0.5, 0.3, n)  # varies per person
sample2 = sample1 + effects

# Same average effect, but higher variance
# → smaller t-statistic
# → lower power
        """, language="python")

with tab4:
    st.markdown("""
    ## 💡 Implementation Guide: Better Power Analysis Workflow
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        #### 1. ESTIMATE PARAMETERS

        Before power analysis, you need:
        - **MDE:** What effect would you care about detecting?
        - **σ_baseline:** How much noise in control group?
        - **σ_het:** How much does effect vary per person?
        - **Sample size (n):** Practical constraints

        **How to estimate σ_het:**
        - Pilot study with small sample
        - Historical data from similar experiments
        - Theory or subject matter expertise
        """)

        st.markdown("""
        #### 2. SIMULATE (don't just use formulas)

        - Run 10,000 experiments
        - Each one: sample, compute t-stat, get p-value
        - Calculate power = % of p < 0.05
        """)

    with col2:
        st.markdown("""
        #### 3. CHECK ASSUMPTIONS

        - Does power match your goal (e.g., 80%)?
        - If not, adjust n or effect size
        - Test sensitivity (±10% variance, ±20% effect)
        """)

        st.markdown("""
        #### 4. DESIGN FOR REALISTIC, NOT BEST CASE

        - Use σ_het from conservative estimate
        - Account for dropout, non-compliance
        - Target 75-80% power, not 80% exactly
        """)

    st.markdown("---")

    st.markdown("""
    ### Complete Python Template
    """)

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

with tab5:
    st.markdown("""
    ## 📝 Quick Summary

    ### 🔑 Key Numbers to Remember
    - **Power target:** 80% is standard (20% Type II error)
    - **α (significance level):** 0.05 standard (5% Type I error)
    - **Median p at MDE:** ~0.005 (not 0.05!)
    - **Heterogeneity cost:** Can reduce power by 10-30% if ignored
    - **Sample size multiplier:** ~1.5-2x if you account for σ_het

    ### 🛑 Common Mistakes to Avoid

    | ❌ Wrong | ✅ Right |
    |---|---|
    | "MDE of 0.5 means p = 0.05" | "MDE of 0.5 means p ≈ 0.005 and 80% power" |
    | Assume effects are homogeneous | Estimate heterogeneity from pilot data |
    | Use formulas without checking | Simulate to verify your assumptions |
    | Design for 80% power exactly | Design for 75% realistic power |
    | Ignore heterogeneity in planning | Include σ_het in power calculations |
    | Trust software defaults | Understand what assumptions are baked in |

    ### 📇 Flashcard Answers
    - **Q1: Where does randomness in power come from?**
      - **A:** From sampling two distributions. Each experiment draws different samples → different t-statistics → different p-values.
    - **Q2: Does measuring MDE mean p = 0.05?**
      - **A:** No. MDE gives p ≈ 0.005 because it's designed for 80% power, well past the rejection threshold.
    - **Q3: Does heterogeneity affect power?**
      - **A:** Yes. Heterogeneous effects add noise, reducing power. Correction: `σ_total² = σ_baseline² + σ_het²`

    ### 🗺️ When to Use the App
    - **"Why is power probabilistic?"** → Use *Discovery 1*
    - **"Why isn't MDE the critical value?"** → Use *Discovery 2*
    - **"How much sample size do I need?"** → Use *Discovery 3*
    - **"I want to design a real experiment"** → Use *Implementation Guide*

    ---
    **Bottom Line:** P-values are random. MDE isn't p=0.05. Heterogeneity costs power. Simulate. Design for realistic variance.
    """)
