# Hypothesis Lab 🧪📊

> **Hypothesis Lab** is an interactive, premium, client-side data science dashboard designed to make statistical hypothesis testing visual, intuitive, and highly educational. 

Run t-tests, Chi-Square tests, and ANOVA completely within your browser. Visualize exact probability distribution curves, shade rejection zones, mark observed statistics, and read deep, step-by-step, plain-English report interpretations.

## 🌟 Key Features

* **Pure client-side computations** in pure JavaScript (`stats.js`) with high-precision cumulative distribution function (CDF) approximations.
* **Dynamic Distribution Plotting** (`charts.js` + Chart.js) that renders the exact probability density functions (PDF) for Student's $t$, $\chi^2$, and $F$-distributions, drawing critical bounds and test statistics.
* **Instant CSV profiling** (`app.js` + PapaParse) which parses datasets locally and auto-detects column data types.
* **Predefined Curated Datasets** (`samples.js`) to let users test medical trials, market preferences, and crop yields instantly with one click.
* **Self-Explaining Reports** (`explainer.js`) that state Null and Alternative hypotheses, validate underlying statistical assumptions, and formulate plain-English interpretations.
* **100% Secure & Private**: No data is uploaded to any server. All calculations are executed on your local machine.

---

## 🛠️ Architecture & Modules

```
hypothesis-lab/
│
├── index.html            # Main SPA dashboard entry point
├── styles.css            # Dark-slate & cyberpunk indigo design system
│
├── js/
│   ├── app.js            # Frontend orchestrator and state management
│   ├── stats.js          # Pure-math statistical engine (CDFs & tests)
│   ├── samples.js        # Built-in curated scientific sample datasets
│   ├── charts.js         # Chart.js handler for PDF curves and error plots
│   └── explainer.js      # Natural language report generation system
│
└── .gitignore            # Clean git exclusion rules
```

---

## 📐 Mathematical Solvers Implemented

Hypothesis Lab implements high-precision, stable numerical solvers with zero external computation libraries:

### 1. Cumulative Distributions (CDF)
* **Standard Normal ($Z$):** High-precision Abramowitz & Stegun rational approximation ($|\text{error}| < 1.5 \times 10^{-7}$).
* **Student's $t$:** Exact trigonometric/series expansion for small or moderate degrees of freedom; normal approximation for $df \ge 1000$:
  $$P(T \le t) = 0.5 + \frac{\theta}{\pi} + \frac{\sin\theta\cos\theta}{\pi} \sum_{r=0}^{(df-3)/2} \frac{2^r r!}{\prod (2j+1)} \cos^{2r}\theta \quad (\text{for odd } df)$$
* **Chi-Square ($\chi^2$):** Exact standard forms for $df=1, 2$; Wilson-Hilferty transformation for $df \ge 3$.
* **F-Distribution ($F$):** Highly precise Paulson transformation mapping the F-ratio to a normal deviate.

### 2. Statistical Tests
* **t-test:**
  * **One-Sample:** $t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}}$
  * **Independent Two-Sample:** Student's Pooled (equal variance) and Welch's Satterthwaite correction (unequal variance):
    $$t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$
  * **Paired Two-Sample:** $t = \frac{\bar{d}}{s_d / \sqrt{n}}$
* **Chi-Square Independence Test:** Contingency table builder with standardized residuals:
  $$\chi^2 = \sum \frac{(O_{i,j} - E_{i,j})^2}{E_{i,j}} \quad \text{where} \quad E_{i,j} = \frac{\text{RowTotal}_i \times \text{ColTotal}_j}{\text{GrandTotal}}$$
* **One-Way ANOVA:** Partitioning of sums of squares (SS Between, SS Within) to compute MS, F-ratio, and Eta-squared ($\eta^2$).

---

## 🚀 Running Locally

Since Hypothesis Lab is entirely static, there is no setup required! You can open it in two ways:

### Method 1: Double-Click
Simply double-click `index.html` in your file explorer to open it directly in any modern browser.

### Method 2: Local Server (Recommended)
If you want to run it on a local server (highly recommended for live debugging), navigate to the directory and run:

**Using Python:**
```bash
python -m http.server 8000
```
Then visit `http://localhost:8000`.

**Using Node.js (`live-server`):**
```bash
npx live-server
```
It will automatically launch `http://127.0.0.1:8080` in your default browser.

---

## 📤 Pushing to GitHub & Deploying

To share your dashboard with the world, push it to GitHub and deploy it for free using **GitHub Pages**:

### Step 1: Initialize Git and Commit
Open your command terminal in this project folder and run:
```bash
git init
git add .
git commit -m "feat: initial release of Hypothesis Lab"
git branch -M main
```

### Step 2: Push to Your Remote Repository
Create a new blank repository on GitHub, copy its URL, and run:
```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### Step 3: Deploy to GitHub Pages (Free!)
1. Go to your repository on **GitHub.com**.
2. Click **Settings** (top tab) -> **Pages** (sidebar menu under "Code and automation").
3. Under **Build and deployment**, change the Source dropdown to **Deploy from a branch**.
4. Set the branch to `main` and the folder to `/ (root)`.
5. Click **Save**.
6. Wait 1-2 minutes, and GitHub will provide your live website link! (e.g., `https://username.github.io/repository-name/`).

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.
