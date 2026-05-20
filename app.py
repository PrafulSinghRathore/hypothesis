import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.graph_objects as go
import plotly.express as px

# --- Page Config & Aesthetics ---
st.set_page_config(
    page_title="Hypothesis Lab - Interactive Statistical Dashboard",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via markdown
st.markdown("""
<style>
    .report-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.5rem;
        font-weight: 600;
        color: #fb7185;
    }
    .narrative-box {
        padding: 1.5rem;
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 5px solid #10b981;
        border-radius: 4px;
        margin-bottom: 1.5rem;
    }
    .latex-eq {
        font-family: monospace;
        background-color: rgba(0, 0, 0, 0.2);
        padding: 10px;
        border-radius: 4px;
        text-align: center;
        margin: 10px 0;
    }
</style>
""", unsafe_style_html=True)

# --- Sample Datasets Initializer ---
@st.cache_data
def get_sample_datasets():
    # 1. Hypertension Trial
    bp_data = pd.DataFrame({
        "PatientID": [f"P{i:03d}" for i in range(1, 31)],
        "TreatmentGroup": ["Active"] * 15 + ["Placebo"] * 15,
        "SBP_Before": [145, 152, 140, 158, 148, 162, 141, 150, 155, 147, 160, 144, 153, 149, 156,
                       142, 148, 150, 145, 156, 140, 152, 144, 158, 147, 153, 141, 149, 146, 151],
        "SBP_After": [128, 132, 130, 135, 131, 140, 129, 133, 136, 130, 138, 132, 134, 131, 135,
                      139, 146, 152, 141, 150, 138, 147, 145, 153, 145, 149, 140, 144, 145, 149]
    })
    bp_data["BP_Reduction"] = bp_data["SBP_Before"] - bp_data["SBP_After"]

    # 2. Tech preference
    tech_data = pd.DataFrame({
        "AgeGroup": ["Young (18-30)"] * 50 + ["Adult (31-50)"] * 55 + ["Senior (51+)"] * 45,
        "PrimaryDevice": ["Smartphone"] * 35 + ["Laptop"] * 12 + ["Tablet"] * 3 +
                         ["Smartphone"] * 15 + ["Laptop"] * 28 + ["Tablet"] * 12 +
                         ["Smartphone"] * 8 + ["Laptop"] * 10 + ["Tablet"] * 27
    })
    
    # 3. Crop Yields
    yield_data = pd.DataFrame({
        "PlotID": [f"PL-{i:02d}" for i in range(1, 31)],
        "FertilizerType": ["Formula A"] * 10 + ["Formula B"] * 10 + ["Formula C"] * 10,
        "Yield_Kg": [20.3, 18.5, 21.4, 19.8, 20.9, 17.6, 19.1, 22.0, 18.9, 20.5,
                     24.5, 22.1, 25.8, 23.9, 24.0, 21.5, 23.2, 26.1, 24.8, 22.9,
                     17.2, 15.1, 18.6, 16.3, 17.5, 14.9, 16.8, 19.0, 17.1, 15.8]
    })
    
    return {
        "Hypertension Trial (t-test)": (bp_data, "t-test"),
        "Consumer Tech Studies (Chi-Square)": (tech_data, "chi-square"),
        "Agricultural Crop Yields (ANOVA)": (yield_data, "anova")
    }

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### 🧪 Navigation")
    active_test = st.radio(
        "Choose Statistical Test",
        ["Student's t-test", "Chi-Square Independence", "One-Way ANOVA"]
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Analysis Parameters")
    alpha = st.selectbox("Significance Level (α)", [0.01, 0.05, 0.10], index=1)
    
    st.markdown("---")
    st.markdown("### 📁 Data Source")
    data_source = st.radio("Load Method", ["Upload CSV File", "Load Prebuilt Sample"])
    
    uploaded_df = None
    if data_source == "Upload CSV File":
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded_file is not None:
            uploaded_df = pd.read_csv(uploaded_file)
    else:
        samples = get_sample_datasets()
        sample_choice = st.selectbox("Select Sample Dataset", [""] + list(samples.keys()))
        if sample_choice:
            uploaded_df, recommended_test = samples[sample_choice]
            # Auto-align selection indicator
            st.info(f"Recommended Test for this dataset: **{recommended_test.upper()}**")

# --- Main Page Layout ---
st.markdown('<div class="report-title">Hypothesis Lab 🧪📊</div>', unsafe_style_html=True)
st.write("Perform statistical tests, view exact probability distribution curves, and receive detailed plain-English findings.")

if uploaded_df is None:
    st.warning("Please upload a CSV file or load a prebuilt sample dataset in the sidebar to begin.")
else:
    col_left, col_right = st.columns([1, 1.3])
    
    with col_left:
        st.markdown("### 📁 Data Preview & Variable Mapping")
        
        # Grid spreadsheet preview
        with st.expander("📝 Spreadsheet Preview (First 10 rows)", expanded=False):
            st.dataframe(uploaded_df.head(10), use_container_width=True)
            
        st.markdown("#### Map variables:")
        
        # Filter numeric and categorical columns
        numeric_cols = uploaded_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = uploaded_df.select_dtypes(exclude=[np.number]).columns.tolist()
        all_cols = uploaded_df.columns.tolist()
        
        # Test configurations mapping
        if active_test == "Student's t-test":
            subtype = st.selectbox(
                "t-test Subtype",
                ["Independent Two-Sample (A vs B)", "Paired Two-Sample (Before vs After)", "One-Sample (vs Constant)"]
            )
            
            tail = st.selectbox("Alternative Hypothesis (Tail)", ["two-sided", "greater", "less"])
            
            if subtype == "One-Sample (vs Constant)":
                target_col = st.selectbox("Target Variable (Numerical)", numeric_cols if numeric_cols else all_cols)
                mu_input = st.number_input("Hypothesized Population Mean (μ₀)", value=0.0)
            elif subtype == "Paired Two-Sample (Before vs After)":
                val1_col = st.selectbox("Baseline Variable (Pre-treatment)", numeric_cols if numeric_cols else all_cols)
                val2_col = st.selectbox("Post Variable (Post-treatment)", numeric_cols if numeric_cols else all_cols)
            else:
                target_col = st.selectbox("Numerical Variable (Response)", numeric_cols if numeric_cols else all_cols)
                group_col = st.selectbox("Grouping Factor (Categorical)", categorical_cols if categorical_cols else all_cols)
                equal_var = st.checkbox("Assume Equal Variances (Pooled)", value=False)
                
        elif active_test == "Chi-Square Independence":
            col1 = st.selectbox("First Classification Variable (Categorical)", categorical_cols if categorical_cols else all_cols, index=0)
            col2 = st.selectbox("Second Classification Variable (Categorical)", categorical_cols if categorical_cols else all_cols, index=min(1, len(all_cols)-1))
            
        elif active_test == "One-Way ANOVA":
            target_col = st.selectbox("Continuous Response Variable (Numerical)", numeric_cols if numeric_cols else all_cols)
            group_col = st.selectbox("Independent Grouping Factor (Categorical)", categorical_cols if categorical_cols else all_cols)
            
    with col_right:
        st.markdown("### 📊 Interactive Visualizations & Reports")
        tab_curve, tab_descr, tab_report = st.tabs(["📈 Probability Curve", "📊 Descriptive Plots", "📝 Self-Explaining Report"])
        
        # Trigger statistical solvers and plotting
        try:
            if active_test == "Student's t-test":
                if subtype == "One-Sample (vs Constant)":
                    data = uploaded_df[target_col].dropna()
                    if len(data) < 2:
                        st.error("Insufficient samples (N < 2).")
                    else:
                        t_stat, p_val = stats.ttest_1samp(data, popmean=mu_input, alternative=tail)
                        df = len(data) - 1
                        mean_val = np.mean(data)
                        std_val = np.std(data, ddof=1)
                        stderr = std_val / np.sqrt(len(data))
                        ci = stats.t.interval(1 - alpha, df, loc=mean_val, scale=stderr)
                        effect_size = (mean_val - mu_input) / std_val if std_val > 0 else 0
                        
                        # --- Tab 1: Curve Plotting ---
                        with tab_curve:
                            fig = go.Figure()
                            x = np.linspace(-4.5, 4.5, 500)
                            y = stats.t.pdf(x, df)
                            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Student-t Density', line=dict(color='#6366f1', width=3.5)))
                            
                            # Shade rejection regions
                            if tail == "two-sided":
                                t_crit = stats.t.ppf(1 - alpha/2, df)
                                x_rej1 = np.linspace(-4.5, -t_crit, 100)
                                x_rej2 = np.linspace(t_crit, 4.5, 100)
                                fig.add_trace(go.Scatter(x=x_rej1, y=stats.t.pdf(x_rej1, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                                fig.add_trace(go.Scatter(x=x_rej2, y=stats.t.pdf(x_rej2, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', showlegend=False))
                            elif tail == "greater":
                                t_crit = stats.t.ppf(1 - alpha, df)
                                x_rej = np.linspace(t_crit, 4.5, 100)
                                fig.add_trace(go.Scatter(x=x_rej, y=stats.t.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                            else:
                                t_crit = stats.t.ppf(alpha, df)
                                x_rej = np.linspace(-4.5, t_crit, 100)
                                fig.add_trace(go.Scatter(x=x_rej, y=stats.t.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                            
                            # Observed t-statistic line
                            fig.add_shape(type="line", x0=t_stat, y0=0, x1=t_stat, y1=max(y)*1.1, line=dict(color="#f59e0b", width=3, dash="dash"))
                            fig.update_layout(title="Student's t Probability Density Curve", xaxis_title="t-value", yaxis_title="Density", template="plotly_dark", height=380)
                            st.plotly_chart(fig, use_container_width=True)
                            st.info("The **Red Region** shows critical rejection boundaries. The **Dashed Amber Line** indicates your calculated test statistic. If it falls inside the red zone, the difference is statistically significant!")
                        
                        # --- Tab 2: Descriptive Plot ---
                        with tab_descr:
                            fig_box = px.box(uploaded_df, y=target_col, points="all", title=f"Distribution of {target_col}", template="plotly_dark")
                            st.plotly_chart(fig_box, use_container_width=True)
                            
                        # --- Tab 3: Explainer Report ---
                        with tab_report:
                            reject = p_val < alpha
                            p_class = "badge-success" if p_val < 0.05 else "badge-neutral"
                            st.markdown(f"""
                            ### 1. Hypotheses Under Evaluation
                            * **Null Hypothesis (H₀):** The population mean of *{target_col}* is equal to {mu_input:.2f} (μ = {mu_input:.2f})
                            * **Alternative Hypothesis (H₁):** The population mean of *{target_col}* {'differs from' if tail=='two-sided' else ('is greater than' if tail=='greater' else 'is less than')} {mu_input:.2f}
                            
                            ### 2. Statistical Summary
                            * **Sample size (N):** {len(data)}
                            * **Calculated t-statistic:** `{t_stat:.4f}`
                            * **Degrees of Freedom (df):** {df}
                            * **p-value:** `{p_val:.6f}`
                            * **Confidence Interval (95% CI):** `[{ci[0]:.4f}, {ci[1]:.4f}]`
                            
                            <div class="narrative-box" style="border-left-color: {'#10b981' if reject else '#64748b'};">
                                <strong>Conclusion:</strong> {'REJECT' if reject else 'FAIL TO REJECT'} the Null Hypothesis at α = {alpha}.<br><br>
                                The sample mean is <strong>{mean_val:.4f}</strong>, deviating from hypothesized μ₀ = <strong>{mu_input:.2f}</strong> by <strong>{abs(mean_val - mu_input):.4f}</strong>. 
                                The probability of getting this result by random chance alone is <strong>{p_val*100:.4f}%</strong>.
                            </div>
                            """, unsafe_style_html=True)
                            
                elif subtype == "Independent Two-Sample (A vs B)":
                    grps = uploaded_df.groupby(group_col)[target_col]
                    keys = list(grps.groups.keys())
                    if len(keys) < 2:
                        st.error(f"Grouping factor '{group_col}' must contain at least 2 categories. Found: {keys}")
                    else:
                        g1_label, g2_label = keys[0], keys[1]
                        g1_data = grps.get_group(g1_label).dropna()
                        g2_data = grps.get_group(g2_label).dropna()
                        
                        t_stat, p_val = stats.ttest_ind(g1_data, g2_data, equal_var=equal_var, alternative=tail)
                        df = len(g1_data) + len(g2_data) - 2 if equal_var else stats.ttest_ind(g1_data, g2_data, equal_var=False).df
                        
                        mean1, mean2 = np.mean(g1_data), np.mean(g2_data)
                        var1, var2 = np.var(g1_data, ddof=1), np.var(g2_data, ddof=1)
                        
                        # --- Tab 1: Curve Plotting ---
                        with tab_curve:
                            fig = go.Figure()
                            x = np.linspace(-4.5, 4.5, 500)
                            y = stats.t.pdf(x, df)
                            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Student-t Density', line=dict(color='#6366f1', width=3.5)))
                            
                            # Shade rejection regions
                            if tail == "two-sided":
                                t_crit = stats.t.ppf(1 - alpha/2, df)
                                x_rej1 = np.linspace(-4.5, -t_crit, 100)
                                x_rej2 = np.linspace(t_crit, 4.5, 100)
                                fig.add_trace(go.Scatter(x=x_rej1, y=stats.t.pdf(x_rej1, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                                fig.add_trace(go.Scatter(x=x_rej2, y=stats.t.pdf(x_rej2, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', showlegend=False))
                            elif tail == "greater":
                                t_crit = stats.t.ppf(1 - alpha, df)
                                x_rej = np.linspace(t_crit, 4.5, 100)
                                fig.add_trace(go.Scatter(x=x_rej, y=stats.t.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                            else:
                                t_crit = stats.t.ppf(alpha, df)
                                x_rej = np.linspace(-4.5, t_crit, 100)
                                fig.add_trace(go.Scatter(x=x_rej, y=stats.t.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                            
                            # Observed t-statistic line
                            fig.add_shape(type="line", x0=t_stat, y0=0, x1=t_stat, y1=max(y)*1.1, line=dict(color="#f59e0b", width=3, dash="dash"))
                            fig.update_layout(title="Student's t Probability Density Curve", xaxis_title="t-value", yaxis_title="Density", template="plotly_dark", height=380)
                            st.plotly_chart(fig, use_container_width=True)
                            
                        # --- Tab 2: Descriptive Plot ---
                        with tab_descr:
                            fig_box = px.box(uploaded_df[uploaded_df[group_col].isin([g1_label, g2_label])], x=group_col, y=target_col, color=group_col, points="all", title=f"{target_col} by {group_col}", template="plotly_dark")
                            st.plotly_chart(fig_box, use_container_width=True)
                            
                        # --- Tab 3: Report ---
                        with tab_report:
                            reject = p_val < alpha
                            st.markdown(f"""
                            ### 1. Hypotheses Under Evaluation
                            * **Null Hypothesis (H₀):** The true mean of *{target_col}* is identical between **{g1_label}** and **{g2_label}** (μ₁ = μ₂)
                            * **Alternative Hypothesis (H₁):** The true mean of *{target_col}* in **{g1_label}** {'differs from' if tail=='two-sided' else ('is greater than' if tail=='greater' else 'is less than')} **{g2_label}** (μ₁ ≠ μ₂)
                            
                            ### 2. Group Descriptive Summary
                            * **{g1_label}:** N = {len(g1_data)}, Mean = {mean1:.4f}, Variance = {var1:.4f}
                            * **{g2_label}:** N = {len(g2_data)}, Mean = {mean2:.4f}, Variance = {var2:.4f}
                            * **Observed Mean Difference (Δ):** {mean1 - mean2:.4f}
                            
                            ### 3. Test Parameter Results
                            * **Test Method:** {"Student's Pooled t-test" if equal_var else "Welch's correction t-test"}
                            * **Calculated t-statistic:** `{t_stat:.4f}`
                            * **Degrees of Freedom (df):** {df:.2f}
                            * **p-value:** `{p_val:.6f}`
                            
                            <div class="narrative-box" style="border-left-color: {'#10b981' if reject else '#64748b'};">
                                <strong>Conclusion:</strong> {'REJECT' if reject else 'FAIL TO REJECT'} the Null Hypothesis at α = {alpha}.<br><br>
                                The average of Group <strong>{g1_label}</strong> is <strong>{mean1:.4f}</strong>, while Group <strong>{g2_label}</strong> is <strong>{mean2:.4f}</strong>.
                                Because the p-value is <strong>{p_val:.6f}</strong>, the difference is <strong>{'statistically significant' if reject else 'statistically indistinguishable from random noise'}</strong>.
                            </div>
                            """, unsafe_style_html=True)
                            
                elif subtype == "Paired Two-Sample (Before vs After)":
                    g1_data = uploaded_df[val1_col].dropna()
                    g2_data = uploaded_df[val2_col].dropna()
                    if len(g1_data) != len(g2_data):
                        st.error("Paired variables must possess matching sample sizes.")
                    else:
                        diffs = g1_data.values - g2_data.values
                        t_stat, p_val = stats.ttest_rel(g1_data, g2_data, alternative=tail)
                        df = len(g1_data) - 1
                        mean_diff = np.mean(diffs)
                        std_diff = np.std(diffs, ddof=1)
                        
                        # --- Tab 1: Curve Plotting ---
                        with tab_curve:
                            fig = go.Figure()
                            x = np.linspace(-4.5, 4.5, 500)
                            y = stats.t.pdf(x, df)
                            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Student-t Density', line=dict(color='#6366f1', width=3.5)))
                            
                            # Shade rejection regions
                            if tail == "two-sided":
                                t_crit = stats.t.ppf(1 - alpha/2, df)
                                x_rej1 = np.linspace(-4.5, -t_crit, 100)
                                x_rej2 = np.linspace(t_crit, 4.5, 100)
                                fig.add_trace(go.Scatter(x=x_rej1, y=stats.t.pdf(x_rej1, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                                fig.add_trace(go.Scatter(x=x_rej2, y=stats.t.pdf(x_rej2, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', showlegend=False))
                            elif tail == "greater":
                                t_crit = stats.t.ppf(1 - alpha, df)
                                x_rej = np.linspace(t_crit, 4.5, 100)
                                fig.add_trace(go.Scatter(x=x_rej, y=stats.t.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                            else:
                                t_crit = stats.t.ppf(alpha, df)
                                x_rej = np.linspace(-4.5, t_crit, 100)
                                fig.add_trace(go.Scatter(x=x_rej, y=stats.t.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                            
                            # Observed t-statistic line
                            fig.add_shape(type="line", x0=t_stat, y0=0, x1=t_stat, y1=max(y)*1.1, line=dict(color="#f59e0b", width=3, dash="dash"))
                            fig.update_layout(title="Student's t Probability Density Curve (Paired)", xaxis_title="t-value", yaxis_title="Density", template="plotly_dark", height=380)
                            st.plotly_chart(fig, use_container_width=True)
                            
                        # --- Tab 2: Descriptive Plot ---
                        with tab_descr:
                            # Spaghetti before-after plot
                            pairs_df = pd.DataFrame({
                                "Baseline": g1_data.values,
                                "Post": g2_data.values,
                                "PairID": [f"Pair {i}" for i in range(1, len(g1_data)+1)]
                            }).melt(id_vars=["PairID"], value_vars=["Baseline", "Post"], var_name="Timepoint", value_name="Measurement")
                            
                            fig_spag = px.line(pairs_df, x="Timepoint", y="Measurement", color="PairID", title="Matched Pair Shift Comparison", template="plotly_dark")
                            st.plotly_chart(fig_spag, use_container_width=True)
                            
                        # --- Tab 3: Report ---
                        with tab_report:
                            reject = p_val < alpha
                            st.markdown(f"""
                            ### 1. Hypotheses Under Evaluation
                            * **Null Hypothesis (H₀):** The true mean difference (μ_d) between *{val1_col}* and *{val2_col}* is zero (μ_d = 0).
                            * **Alternative Hypothesis (H₁):** The true mean difference (μ_d) {'differs from' if tail=='two-sided' else ('is greater than' if tail=='greater' else 'is less than')} zero.
                            
                            ### 2. Paired Summary Statistics
                            * **Number of matched pairs (N):** {len(g1_data)}
                            * **Mean difference (Before - After):** {mean_diff:.4f}
                            * **Standard Deviation of differences:** {std_diff:.4f}
                            * **Calculated t-statistic:** `{t_stat:.4f}`
                            * **p-value:** `{p_val:.6f}`
                            
                            <div class="narrative-box" style="border-left-color: {'#10b981' if reject else '#64748b'};">
                                <strong>Conclusion:</strong> {'REJECT' if reject else 'FAIL TO REJECT'} the Null Hypothesis at α = {alpha}.<br><br>
                                The average shift between the pairs is <strong>{mean_diff:.4f}</strong>. Because the p-value is <strong>{p_val:.6f}</strong>,
                                the observed shift is <strong>{'highly unlikely to be random sampling fluctuation, indicating a real systemic shift' if reject else 'statistically indistinguishable from random fluctuations'}</strong>.
                            </div>
                            """, unsafe_style_html=True)
                            
            elif active_test == "Chi-Square Independence":
                # Create contingency table
                contingency = pd.crosstab(uploaded_df[col1], uploaded_df[col2])
                chi2_stat, p_val, df, expected = stats.chi2_contingency(contingency)
                
                # --- Tab 1: Curve Plotting ---
                with tab_curve:
                    fig = go.Figure()
                    x_max = max(12, df + 4 * np.sqrt(2*df))
                    x = np.linspace(0, x_max, 500)
                    y = stats.chi2.pdf(x, df)
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Chi-Square Density', line=dict(color='#6366f1', width=3.5)))
                    
                    # Shade rejection regions
                    chi_crit = stats.chi2.ppf(1 - alpha, df)
                    x_rej = np.linspace(chi_crit, x_max, 100)
                    fig.add_trace(go.Scatter(x=x_rej, y=stats.chi2.pdf(x_rej, df), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                    
                    # Observed line
                    fig.add_shape(type="line", x0=chi2_stat, y0=0, x1=chi2_stat, y1=max(y)*1.1, line=dict(color="#f59e0b", width=3, dash="dash"))
                    fig.update_layout(title="Chi-Square Probability Density Curve", xaxis_title="Chi2 Value", yaxis_title="Density", template="plotly_dark", height=380)
                    st.plotly_chart(fig, use_container_width=True)
                    
                # --- Tab 2: Descriptive Plot ---
                with tab_descr:
                    flat_contingency = contingency.reset_index().melt(id_vars=[col1])
                    fig_bar = px.bar(flat_contingency, x=col1, y="value", color=col2, barmode="group", title="Observed Contingency Counts", template="plotly_dark")
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                # --- Tab 3: Report ---
                with tab_report:
                    reject = p_val < alpha
                    st.markdown(f"""
                    ### 1. Hypotheses Under Evaluation
                    * **Null Hypothesis (H₀):** The classifications *{col1}* and *{col2}* are completely independent. No systemic association exists.
                    * **Alternative Hypothesis (H₁):** The classifications *{col1}* and *{col2}* are dependent (systemically linked).
                    
                    ### 2. Contingency Frequencies
                    **Observed Counts Table:**
                    """)
                    st.dataframe(contingency, use_container_width=True)
                    
                    st.markdown("""
                    **Expected Counts Table (under Independence assumption):**
                    """)
                    st.dataframe(pd.DataFrame(expected, index=contingency.index, columns=contingency.columns), use_container_width=True)
                    
                    st.markdown(f"""
                    ### 3. Test Statistics Summary
                    * **Chi-Square (χ²) Statistic:** `{chi2_stat:.4f}`
                    * **Degrees of Freedom (df):** {df}
                    * **p-value:** `{p_val:.6f}`
                    
                    <div class="narrative-box" style="border-left-color: {'#10b981' if reject else '#64748b'};">
                        <strong>Conclusion:</strong> {'REJECT' if reject else 'FAIL TO REJECT'} the Null Hypothesis at α = {alpha}.<br><br>
                        The observed categories deviate from the expected frequencies under independence. 
                        Because the p-value is <strong>{p_val:.6f}</strong>, the association is <strong>{'highly statistically significant, proving the two factors are closely linked' if reject else 'statistically insignificant, meaning the observations are fully compatible with random sampling variations'}</strong>.
                    </div>
                    """, unsafe_style_html=True)
                    
            elif active_test == "One-Way ANOVA":
                grps = uploaded_df.groupby(group_col)[target_col]
                keys = list(grps.groups.keys())
                groups_list = [grps.get_group(k).dropna() for k in keys]
                
                f_stat, p_val = stats.f_oneway(*groups_list)
                dfn = len(keys) - 1
                dfd = sum(len(g) for g in groups_list) - len(keys)
                
                # --- Tab 1: Curve Plotting ---
                with tab_curve:
                    fig = go.Figure()
                    x_max = max(6, 3 * dfn / max(1, dfn - 2) + 4)
                    x = np.linspace(0, x_max, 500)
                    y = stats.f.pdf(x, dfn, dfd)
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='F-Density', line=dict(color='#6366f1', width=3.5)))
                    
                    # Shade rejection regions
                    f_crit = stats.f.ppf(1 - alpha, dfn, dfd)
                    x_rej = np.linspace(f_crit, x_max, 100)
                    fig.add_trace(go.Scatter(x=x_rej, y=stats.f.pdf(x_rej, dfn, dfd), fill='tozeroy', mode='none', fillcolor='rgba(239, 68, 68, 0.3)', name='Rejection Boundary'))
                    
                    # Observed line
                    fig.add_shape(type="line", x0=f_stat, y0=0, x1=f_stat, y1=max(y)*1.1, line=dict(color="#f59e0b", width=3, dash="dash"))
                    fig.update_layout(title="ANOVA F Probability Density Curve", xaxis_title="F-Value", yaxis_title="Density", template="plotly_dark", height=380)
                    st.plotly_chart(fig, use_container_width=True)
                    
                # --- Tab 2: Descriptive Plot ---
                with tab_descr:
                    fig_box = px.box(uploaded_df, x=group_col, y=target_col, color=group_col, points="all", title=f"{target_col} by {group_col}", template="plotly_dark")
                    st.plotly_chart(fig_box, use_container_width=True)
                    
                # --- Tab 3: Report ---
                with tab_report:
                    reject = p_val < alpha
                    st.markdown(f"""
                    ### 1. Hypotheses Under Evaluation
                    * **Null Hypothesis (H₀):** The true population means of all **{len(keys)}** groups are completely identical (μ₁ = μ₂ = ... = μ_k).
                    * **Alternative Hypothesis (H₁):** At least one group mean is systemically different from the others.
                    
                    ### 2. Group Descriptive Averages
                    """)
                    desc_list = []
                    for k, g in zip(keys, groups_list):
                        desc_list.append({
                            "Group Level": k,
                            "Sample Size (n)": len(g),
                            "Mean": np.mean(g),
                            "Variance": np.var(g, ddof=1)
                        })
                    st.table(pd.DataFrame(desc_list))
                    
                    st.markdown(f"""
                    ### 3. ANOVA F-Table Results
                    * **F-statistic:** `{f_stat:.4f}`
                    * **Degrees of Freedom (Between Groups, dfn):** {dfn}
                    * **Degrees of Freedom (Within Groups, dfd):** {dfd}
                    * **p-value:** `{p_val:.6f}`
                    
                    <div class="narrative-box" style="border-left-color: {'#10b981' if reject else '#64748b'};">
                        <strong>Conclusion:</strong> {'REJECT' if reject else 'FAIL TO REJECT'} the Null Hypothesis at α = {alpha}.<br><br>
                        One-Way ANOVA analyzes whether the variance <em>between</em> the group averages is significantly larger than the variance <em>within</em> the groups. 
                        Because the p-value is <strong>{p_val:.6f}</strong>, the difference is <strong>{'highly significant, meaning at least one group level has a systemically different mean than others' if reject else 'statistically insignificant, meaning any group deviations are likely due to simple random variation'}</strong>.
                    </div>
                    """, unsafe_style_html=True)
                    
        except Exception as e:
            st.error(f"Statistical Computation Error: {str(e)}")
            st.info("Ensure the mapped variables contain correct data ranges (numerical columns should have numeric values and categorical variables should separate records).")
