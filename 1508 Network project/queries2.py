ROUTING_DATASET_200 = [
    # ============================================================
    # 1–80: OBVIOUS SINGLE-AGENT QUERIES (SHORT + COMPLEX)
    # ============================================================

    # ---------- DataEngAgent obvious (1–20) ----------
    # Short, clearly data-engineering
    # 1
    (
        "Load the raw CSV files from the data lake, inspect the schema, and fix obvious type mismatches.",
        "DataEngAgent",
    ),
    # 2
    (
        "Connect to the production database and profile the main fact table for missing values and duplicates.",
        "DataEngAgent",
    ),
    # 3
    (
        "Build a simple ETL job that merges these daily log files into a single clean table.",
        "DataEngAgent",
    ),
    # 4
    (
        "Normalize this denormalized spreadsheet into a proper relational schema with clear keys.",
        "DataEngAgent",
    ),
    # 5
    (
        "Rewrite this slow SQL query so it runs efficiently on the warehouse.",
        "DataEngAgent",
    ),
    # 6
    (
        "Set up a pipeline that ingests JSON events and enforces a consistent schema over time.",
        "DataEngAgent",
    ),
    # 7
    (
        "Aggregate the raw clickstream logs into user-level daily sessions ready for analysis.",
        "DataEngAgent",
    ),
    # 8
    (
        "Create indexes on the columns most frequently used in our analytical queries.",
        "DataEngAgent",
    ),
    # 9
    (
        "Backfill missing records in this partitioned table using the archived raw data.",
        "DataEngAgent",
    ),
    # 10
    (
        "Design a star schema for our sales reporting use case.",
        "DataEngAgent",
    ),

    # Complex, still purely data-engineering
    # 11
    (
        "We receive monthly Excel workbooks from different regions with inconsistent headers, currencies, and date formats. "
        "Your job is to design and implement a repeatable ETL process that extracts the relevant sheets, standardizes units "
        "and timestamps, merges all regions into a coherent fact table, and documents the resulting schema for downstream use.",
        "DataEngAgent",
    ),
    # 12
    (
        "Our clickstream events are stored as semi-structured JSON blobs, with schema drift and occasional malformed records. "
        "Begin by building a robust ingestion pipeline that parses these events, enforces a stable schema, quarantines bad rows, "
        "and writes a clean session table that analysts and modelers can safely query later.",
        "DataEngAgent",
    ),
    # 13
    (
        "The legacy transactional database was never meant for analytics and now powers slow dashboards. Start by profiling the "
        "current schema, identifying core entities, designing a warehouse model with fact and dimension tables, and creating the "
        "necessary transformation jobs to keep that model in sync with production data.",
        "DataEngAgent",
    ),
    # 14
    (
        "We are migrating from an on-prem OLTP system to a cloud data warehouse. Plan and implement a migration strategy that "
        "cleans up obsolete columns, standardizes encodings, validates row counts, and ensures that the resulting warehouse "
        "tables are ready for querying by statistics and visualization tools.",
        "DataEngAgent",
    ),
    # 15
    (
        "Different teams have copied and modified product spreadsheets over the years, leading to inconsistent names, missing "
        "keys, and duplicated rows. Consolidate these files into a single master product table, resolve conflicts with clear "
        "rules, and enforce integrity constraints that prevent future divergence.",
        "DataEngAgent",
    ),
    # 16
    (
        "Our IoT sensors send events from multiple time zones and sometimes out of order. Build a data pipeline that parses "
        "these events, normalizes timestamps, deduplicates records, and produces a clean time-series dataset at a consistent "
        "granularity for later modeling and reporting.",
        "DataEngAgent",
    ),
    # 17
    (
        "The marketing tracking data contains bot traffic, test events, and malformed campaign parameters. Create an ETL flow "
        "that filters out clearly invalid events, reconciles campaign identifiers against a reference table, and exposes a "
        "stable, well-documented dataset for campaign analysis.",
        "DataEngAgent",
    ),
    # 18
    (
        "We want standardized metrics for active users across several products. Define and build the data transformations that "
        "combine logins, feature usage, and subscription status into a reliable activity table that can be reused by analysts.",
        "DataEngAgent",
    ),
    # 19
    (
        "Our data lake has accumulated many similar tables with unclear provenance. Start by cataloging these datasets, "
        "identifying canonical versions, removing redundant or obsolete copies, and publishing a clean layer that other teams can trust.",
        "DataEngAgent",
    ),
    # 20
    (
        "Support tickets, billing records, and CRM contacts each contain partial customer information. Design a robust matching "
        "and merging process that produces a single master customer table with stable IDs and documented data lineage.",
        "DataEngAgent",
    ),

    # ---------- StatisticsAgent obvious (21–40) ----------
    # Short
    # 21
    (
        "Test whether the average conversion rate differs between control and treatment groups.",
        "StatisticsAgent",
    ),
    # 22
    (
        "Compute confidence intervals for this proportion and explain what they mean.",
        "StatisticsAgent",
    ),
    # 23
    (
        "Check if this variable is approximately normally distributed using appropriate tests.",
        "StatisticsAgent",
    ),
    # 24
    (
        "Run an ANOVA comparing mean outcomes across these four experimental conditions.",
        "StatisticsAgent",
    ),
    # 25
    (
        "Perform a chi-square test of independence between these two categorical variables.",
        "StatisticsAgent",
    ),
    # 26
    (
        "Fit a simple linear regression and report the slope, p-values, and R-squared.",
        "StatisticsAgent",
    ),
    # 27
    (
        "Calculate the correlation between these two features and interpret its strength.",
        "StatisticsAgent",
    ),
    # 28
    (
        "Estimate the sample size needed to detect a given effect size with 80% power.",
        "StatisticsAgent",
    ),
    # 29
    (
        "Check regression residuals for nonlinearity, heteroscedasticity, and outliers.",
        "StatisticsAgent",
    ),
    # 30
    (
        "Perform a paired t-test on these before-and-after measurements.",
        "StatisticsAgent",
    ),
    # 31
    (
        "Compute a Bayesian credible interval for this parameter and summarize the result.",
        "StatisticsAgent",
    ),
    # 32
    (
        "Summarize this dataset using descriptive statistics and basic distribution plots.",
        "StatisticsAgent",
    ),

    # Complex, still purely statistical
    # 33
    (
        "Given a cleaned dataset from a recent A/B experiment, formulate precise null and alternative hypotheses, "
        "check randomization quality, and run appropriate significance tests. Report effect sizes with confidence "
        "intervals and clear interpretations before any dashboards or machine learning models are considered.",
        "StatisticsAgent",
    ),
    # 34
    (
        "We track monthly revenue by region and marketing channel. Start with a thorough exploratory analysis, "
        "including correlations, basic regression models, and residual diagnostics. Determine whether apparent "
        "patterns are statistically meaningful or just noise, and quantify uncertainty around key estimates.",
        "StatisticsAgent",
    ),
    # 35
    (
        "Product wants to know if a new onboarding flow improves engagement. Use the experimental data to test this "
        "hypothesis, account for potential confounders, compute effect sizes, and provide a clear recommendation "
        "based on statistical evidence rather than anecdotal impressions.",
        "StatisticsAgent",
    ),
    # 36
    (
        "A clinical trial compared treatment and control groups but has some missing outcomes. Choose an appropriate "
        "strategy for handling missing data, verify baseline balance, run the main inferential tests, and communicate "
        "the magnitude and uncertainty of treatment effects in accessible language.",
        "StatisticsAgent",
    ),
    # 37
    (
        "Our churn dataset includes many predictors and we suspect multicollinearity. Begin by analyzing feature "
        "distributions, computing correlations and variance inflation factors, and fitting interpretable baseline "
        "models. Use diagnostics and hypothesis tests to understand which signals are reliable.",
        "StatisticsAgent",
    ),
    # 38
    (
        "We suspect that a recent pricing change affected purchase behavior. Design a quasi-experimental analysis or "
        "time-series intervention model, estimate the effect, and present confidence intervals and caveats so that "
        "business leaders can judge whether the policy should be kept or rolled back.",
        "StatisticsAgent",
    ),
    # 39
    (
        "Survey data includes Likert-scale responses and demographics. Start by summarizing response distributions, "
        "testing group differences with appropriate methods, and carefully interpreting effect sizes without "
        "overstating small but statistically significant differences.",
        "StatisticsAgent",
    ),
    # 40
    (
        "Operations changed a process mid-year and claims defects dropped. Build a statistical analysis that compares "
        "pre- and post-change defect rates, handles overdispersion if necessary, and clearly explains whether the "
        "observed improvement is likely to be real or just random variation.",
        "StatisticsAgent",
    ),

    # ---------- MLAgent obvious (41–60) ----------
    # Short
    # 41
    (
        "Train a random forest classifier on these labeled features and report its performance.",
        "MLAgent",
    ),
    # 42
    (
        "Build a gradient boosting model for this regression problem and evaluate it with RMSE.",
        "MLAgent",
    ),
    # 43
    (
        "Construct a neural network for this image classification dataset.",
        "MLAgent",
    ),
    # 44
    (
        "Tune hyperparameters for this model using cross-validation and a validation set.",
        "MLAgent",
    ),
    # 45
    (
        "Train a support vector machine for binary classification and compare kernels.",
        "MLAgent",
    ),
    # 46
    (
        "Perform feature selection to improve prediction quality and reduce overfitting.",
        "MLAgent",
    ),
    # 47
    (
        "Build a clustering model to discover natural customer segments in this dataset.",
        "MLAgent",
    ),
    # 48
    (
        "Create an ML pipeline that scales features and trains a logistic regression classifier.",
        "MLAgent",
    ),
    # 49
    (
        "Evaluate this classifier using precision, recall, F1 score, and ROC-AUC.",
        "MLAgent",
    ),
    # 50
    (
        "Calibrate the probability outputs of this existing classification model.",
        "MLAgent",
    ),
    # 51
    (
        "Train a time-series forecasting model on these historical demand values.",
        "MLAgent",
    ),
    # 52
    (
        "Use model stacking to combine several base learners and improve accuracy.",
        "MLAgent",
    ),

    # Complex, still purely ML
    # 53
    (
        "Assume the features and labels for churn prediction have already been cleaned and validated. Your first task "
        "is to design and train a robust classification pipeline that includes feature engineering, model selection, "
        "hyperparameter tuning, and evaluation with appropriate metrics, such as AUC and calibration plots.",
        "MLAgent",
    ),
    # 54
    (
        "Given a prepared dataset of historical orders, benchmark several regression algorithms to predict future "
        "revenue at the customer level. Use cross-validation, tune key hyperparameters, compare performance, and "
        "select a model that balances accuracy with interpretability.",
        "MLAgent",
    ),
    # 55
    (
        "For this product image dataset, assume preprocessing and labels are ready. Build and train a convolutional "
        "neural network, experiment with data augmentation and architecture choices, and report the best model’s "
        "performance on a held-out test set.",
        "MLAgent",
    ),
    # 56
    (
        "We have user interaction logs summarized into features by a data engineering pipeline. Start by training "
        "recommendation or ranking models, such as matrix factorization or neural recommenders, tune them for ranking "
        "metrics, and compare offline evaluation results.",
        "MLAgent",
    ),
    # 57
    (
        "Sensor readings and failure labels are available in a clean time-series format. Build forecasting and anomaly "
        "detection models that can flag imminent failures, evaluate them with appropriate metrics, and discuss the trade-offs "
        "between false positives and missed failures.",
        "MLAgent",
    ),
    # 58
    (
        "For this textual corpus of customer reviews, tokens and basic features are already prepared. Train sentiment "
        "classification models using both classical approaches and transformer-based architectures, tune them, and determine "
        "which approach offers the best balance of performance and cost.",
        "MLAgent",
    ),
    # 59
    (
        "We want to segment customers into useful groups. Experiment with multiple clustering algorithms and distance "
        "measures, determine the number of clusters using quantitative criteria, and propose segments that could be "
        "interpreted and acted on by non-technical stakeholders.",
        "MLAgent",
    ),
    # 60
    (
        "The fraud team needs a model that flags suspicious transactions. With a prepared dataset, train and evaluate "
        "several classification algorithms, prioritize recall at a fixed precision, and recommend a model configuration "
        "that balances detection power and investigation workload.",
        "MLAgent",
    ),

    # ---------- VizAgent obvious (61–80) ----------
    # Short
    # 61
    (
        "Create a line chart showing revenue by month for the last two years.",
        "VizAgent",
    ),
    # 62
    (
        "Make a bar chart comparing sales across product categories.",
        "VizAgent",
    ),
    # 63
    (
        "Plot a scatter diagram of price versus units sold with a trend line.",
        "VizAgent",
    ),
    # 64
    (
        "Draw a histogram of this metric to show its distribution.",
        "VizAgent",
    ),
    # 65
    (
        "Build a dashboard with a few key KPIs and simple filters.",
        "VizAgent",
    ),
    # 66
    (
        "Create a box plot to highlight outliers in delivery times.",
        "VizAgent",
    ),
    # 67
    (
        "Design a heatmap of the correlation matrix for these features.",
        "VizAgent",
    ),
    # 68
    (
        "Make a pie chart showing market share by region.",
        "VizAgent",
    ),
    # 69
    (
        "Visualize this confusion matrix as a clear annotated chart.",
        "VizAgent",
    ),
    # 70
    (
        "Build an interactive dashboard for monitoring daily signups.",
        "VizAgent",
    ),
    # 71
    (
        "Create small multiple charts showing trends for each country.",
        "VizAgent",
    ),
    # 72
    (
        "Design a funnel visualization for the acquisition pipeline.",
        "VizAgent",
    ),

    # Complex, still purely viz
    # 73
    (
        "Leadership wants a single dashboard that clearly shows revenue, churn, and acquisition trends over time. "
        "Assume the metrics are already computed and trustworthy. Focus on designing concise, interactive visualizations "
        "that highlight trends, anomalies, and seasonality while remaining understandable to non-technical viewers.",
        "VizAgent",
    ),
    # 74
    (
        "The growth team needs to explore the user funnel visually. Create a set of linked visualizations that show "
        "drop-off at each stage, allow filtering by segment, and make bottlenecks obvious, relying on upstream data "
        "engineering work to supply accurate aggregated numbers.",
        "VizAgent",
    ),
    # 75
    (
        "We track many KPIs across products and regions, and stakeholders feel overwhelmed. Design an information-dense "
        "yet readable dashboard that organizes metrics into coherent sections, uses appropriate chart types, and supports "
        "basic interactions without requiring people to write queries.",
        "VizAgent",
    ),
    # 76
    (
        "The data science team has evaluation results for several models but executives only see raw numbers. Build "
        "visualizations that communicate model performance, feature importance, and uncertainty in an accessible way, "
        "helping decision-makers understand trade-offs without reading a technical report.",
        "VizAgent",
    ),
    # 77
    (
        "Customer success needs a live view of support volume, resolution time, and backlog. Create an operational dashboard "
        "with real-time or near-real-time charts, sensible thresholds, and views that can quickly surface emerging problems.",
        "VizAgent",
    ),
    # 78
    (
        "We plan to host an interactive analytics page for customers on our website. Design intuitive, responsive visuals with "
        "tooltips, filters, and clear defaults so non-technical users can explore their own data safely, assuming governance "
        "and aggregation have already been handled.",
        "VizAgent",
    ),
    # 79
    (
        "Operations wants to understand warehouse bottlenecks throughout the day. Build time-of-day and station-level "
        "visualizations that reveal queue lengths, processing rates, and utilization patterns so they can spot recurring issues.",
        "VizAgent",
    ),
    # 80
    (
        "We have many legacy dashboards that conflict with each other. Propose and design a consolidated visual interface "
        "that emphasizes clarity, reduces duplication, and highlights the most decision-relevant views, assuming data quality "
        "has been addressed upstream.",
        "VizAgent",
    ),

    # ============================================================
    # 81–120: COMPLEX MULTI-AGENT QUERIES (WE LABEL FIRST AGENT)
    # ============================================================

    # ---------- DataEngAgent-first multi-agent (81–90) ----------
    # 81
    (
        "We have messy CSV exports from three different CRMs, all with slightly different field names and encodings. "
        "First, consolidate and clean these sources into a single reliable customer table, and only after that should "
        "anyone attempt churn modeling, statistical tests, or dashboards.",
        "DataEngAgent",
    ),
    # 82
    (
        "Our clickstream data is raw and unfiltered, with bots and broken URLs mixed in. Start by building a pipeline "
        "that cleans and aggregates sessions at the user-day level, then others can compute metrics, run experiments, "
        "and visualize conversion funnels.",
        "DataEngAgent",
    ),
    # 83
    (
        "Support ticket logs live in different systems, some structured and some free-text. Begin by unifying and "
        "cleaning these sources into a consistent schema, after which statisticians can explore patterns and machine "
        "learning models can be trained to predict escalations.",
        "DataEngAgent",
    ),
    # 84
    (
        "We want an end-to-end pipeline that takes raw IoT events, cleans them, stores them in a warehouse, and then "
        "feeds forecasting models and monitoring dashboards. Focus first on schema design, data quality checks, and "
        "robust ingestion jobs before any modeling or visualization.",
        "DataEngAgent",
    ),
    # 85
    (
        "Three systems track orders, payments, and shipments with overlapping but inconsistent keys. Your first task is "
        "to create a unified, cleaned order history table. Afterwards, statistical analysts can study delays and an ML "
        "agent can predict which orders are likely to be late.",
        "DataEngAgent",
    ),
    # 86
    (
        "The growth and data science teams both want to experiment on user behavior, but current tables are hard to join. "
        "Start by building a well-documented experiment schema with user IDs, variants, and outcomes, then other agents "
        "can run tests, build models, and create experiment dashboards.",
        "DataEngAgent",
    ),
    # 87
    (
        "Finance wants to forecast revenue by product and region using historical data scattered across spreadsheets. "
        "First, design and populate a clean fact table that combines these spreadsheets, then a statistics agent can "
        "analyze trends and an ML agent can build forecasting models.",
        "DataEngAgent",
    ),
    # 88
    (
        "Marketing wants automated reporting and predictive scoring, but the raw campaign logs contain junk data. "
        "Begin with data engineering work to filter, standardize, and join these logs with customer attributes so that "
        "statistical and ML agents downstream can trust the inputs.",
        "DataEngAgent",
    ),
    # 89
    (
        "Executives asked for a real-time operations dashboard, but log formats differ between services. Focus first on "
        "creating a unified, cleaned event stream and warehouse schema. Once that’s stable, other agents can do anomaly "
        "detection, alerting, and visualization.",
        "DataEngAgent",
    ),
    # 90
    (
        "We want a full analytics stack for our new product: raw events, metrics, experiments, models, and dashboards. "
        "Start by setting up the foundational data engineering pipelines and warehouse tables, then hand off to statistics "
        "and ML agents for analysis and forecasting, and finally to visualization for dashboards.",
        "DataEngAgent",
    ),

    # ---------- StatisticsAgent-first multi-agent (91–100) ----------
    # 91
    (
        "We ran an A/B test on a new signup flow, and now everyone wants dashboards and predictive models. First, perform "
        "a rigorous statistical analysis of the experiment results, including power, effect sizes, and significance, and "
        "then others can build visualizations and long-term models if warranted.",
        "StatisticsAgent",
    ),
    # 92
    (
        "Monthly revenue appears to spike after certain campaigns, and marketing wants a forecasting model. Start with a "
        "statistical analysis that disentangles seasonality, campaign effects, and noise, then decide whether more complex "
        "machine learning models and dashboards are necessary.",
        "StatisticsAgent",
    ),
    # 93
    (
        "The product team thinks our new pricing increased average order value, and they’re asking for a fancy dashboard. "
        "Begin by designing and running the correct hypothesis tests, controlling for confounders, and summarizing the "
        "results statistically before any visualization polish or modeling.",
        "StatisticsAgent",
    ),
    # 94
    (
        "We have several years of clinical measurements and want a predictive model of patient outcomes. First, use "
        "statistical methods to understand which variables matter, check assumptions, and quantify uncertainty, then an "
        "ML agent can build more complex models informed by those findings.",
        "StatisticsAgent",
    ),
    # 95
    (
        "Survey responses show changes over time, and leadership wants a story with charts and maybe a classifier. "
        "Start by analyzing the survey data statistically, comparing groups, testing trends, and estimating effect sizes. "
        "Only then should downstream agents build predictive models or dashboards.",
        "StatisticsAgent",
    ),
    # 96
    (
        "Marketing wants a model to predict which campaigns are likely to succeed. First, analyze historical campaign "
        "results with proper statistical techniques to see which factors have robust, consistent relationships with "
        "success, and then pass those insights to an ML agent.",
        "StatisticsAgent",
    ),
    # 97
    (
        "Operations believes a process change reduced defect rates, and they also want a live monitoring dashboard. Begin "
        "by conducting a statistical analysis of pre- and post-change data, estimating the size and reliability of the "
        "improvement, and only then move on to visual monitoring tools.",
        "StatisticsAgent",
    ),
    # 98
    (
        "We’re considering segment-based personalization, and there’s pressure to build clustering models immediately. "
        "First, perform statistical exploration of segments, test whether key metrics differ meaningfully, and determine "
        "which segment definitions are stable before engaging ML and viz agents.",
        "StatisticsAgent",
    ),
    # 99
    (
        "Executives want a single number that captures overall product health, plus predictive alerts. Start by defining "
        "and validating a composite metric statistically, ensuring it correlates sensibly with outcomes, and then pass it "
        "to ML and visualization agents for forecasting and dashboards.",
        "StatisticsAgent",
    ),
    # 100
    (
        "The organization tracks many performance indicators, but it’s unclear which ones meaningfully predict success. "
        "Begin with rigorous statistical modeling that tests relationships and controls for confounders, and only after "
        "that should other agents construct predictive pipelines and visual stories.",
        "StatisticsAgent",
    ),

    # ---------- MLAgent-first multi-agent (101–110) ----------
    # 101
    (
        "We already have a clean customer feature table and have run some basic statistical checks. Now build a robust "
        "churn prediction model, evaluate it thoroughly, and then others can create dashboards and detailed reports to "
        "communicate the results.",
        "MLAgent",
    ),
    # 102
    (
        "Finance prepared a cleaned time-series of daily revenue, and simple statistical models have been tried. Focus on "
        "building and tuning machine learning forecasting models that outperform those baselines, and later a viz agent "
        "can turn the forecasts into dashboards.",
        "MLAgent",
    ),
    # 103
    (
        "We have labeled support tickets for prior escalations, and basic analysis is done. Your first task is to train "
        "and evaluate escalation prediction models so that downstream visualization tools can show risk scores and trends.",
        "MLAgent",
    ),
    # 104
    (
        "A statistics agent has identified strong predictors of churn and checked assumptions. Now design and train a "
        "machine learning pipeline that leverages those predictors, tunes hyperparameters, and provides probability scores "
        "that can later be visualized in reports.",
        "MLAgent",
    ),
    # 105
    (
        "Our marketing team wants uplift modeling for targeting offers. Data is cleaned and exploratory statistics are done. "
        "Start by constructing appropriate treatment and control features, training uplift models, and validating their "
        "performance, after which other agents can visualize and explain the results.",
        "MLAgent",
    ),
    # 106
    (
        "Product wants a recommendation system for content, and we already have user-item interaction features prepared. "
        "Focus on training and evaluating recommendation models, then work with visualization and statistics agents to "
        "make their behavior understandable to stakeholders.",
        "MLAgent",
    ),
    # 107
    (
        "The risk team provided a curated dataset and baseline logistic regressions for default prediction. Now build "
        "more advanced machine learning models, such as gradient boosting or ensembles, and then pass the outputs to viz "
        "agents for executive-friendly dashboards.",
        "MLAgent",
    ),
    # 108
    (
        "We have logs of model predictions and actual outcomes over time, and stats show some drift. Start by training "
        "meta-models or diagnostic ML tools that detect and characterize drift, then work with visualization to present "
        "these insights to model owners.",
        "MLAgent",
    ),
    # 109
    (
        "The company wants a lead scoring system for sales. With features and labels ready and some statistical sanity "
        "checks done, your first role is to design an interpretable ML pipeline, tune it, and provide scores that can be "
        "surfaced in dashboards and CRM tools.",
        "MLAgent",
    ),
    # 110
    (
        "We’re planning an automated anomaly detection system for infrastructure metrics. Data pipelines and baseline "
        "statistics are in place. Start by training and comparing ML-based anomaly detectors, then coordinate with viz "
        "agents to visualize anomalies clearly.",
        "MLAgent",
    ),

    # ---------- VizAgent-first multi-agent (111–120) ----------
    # 111
    (
        "Executives complain they can’t see a clear story in our existing reports. Assume metrics are already computed and "
        "tested. Your first task is to create a coherent, interactive dashboard that pulls together key KPIs; other agents "
        "can refine models and metrics later if gaps appear.",
        "VizAgent",
    ),
    # 112
    (
        "The experimentation platform produces detailed tables and model outputs, but product managers are overwhelmed. "
        "Begin by designing visual summaries of experiment results, including effect sizes and uncertainty, then invite "
        "statistics and ML agents to refine analyses where needed.",
        "VizAgent",
    ),
    # 113
    (
        "Operations wants a command-center view of system health that combines metrics, anomalies, and alerts. With data "
        "already flowing in, focus on building clear, real-time visualizations while leaving deeper modeling and root-cause "
        "analysis to other agents.",
        "VizAgent",
    ),
    # 114
    (
        "We have multiple models in production but no unified way to see how they’re doing. Start by creating a model "
        "performance dashboard that surfaces key metrics and trends, and then work with statistics and ML agents if the "
        "visuals reveal suspicious behavior.",
        "VizAgent",
    ),
    # 115
    (
        "Stakeholders want to explore retention patterns without running SQL. Metrics tables are already curated. Your "
        "first responsibility is to build exploratory visualizations of cohorts and churn curves, after which statistics "
        "and ML agents can dig deeper into causal factors.",
        "VizAgent",
    ),
    # 116
    (
        "Customer success needs an easy interface to explore support topics, backlogs, and satisfaction scores. With data "
        "pipelines in place, create dashboards that expose these patterns graphically, and rely on statistical and ML agents "
        "only when new questions arise.",
        "VizAgent",
    ),
    # 117
    (
        "Product wants an internal analytics portal instead of many isolated reports. Start by designing a cohesive visual "
        "experience that integrates core metrics and model outputs; if inconsistencies appear, data and statistics agents "
        "can be consulted to fix them.",
        "VizAgent",
    ),
    # 118
    (
        "The research team has complex clustering and embedding results that nobody outside the team understands. Focus on "
        "turning these outputs into intuitive visualizations—such as projection plots and cluster summaries—so that non-experts "
        "can grasp the high-level structure before more detailed analysis is done.",
        "VizAgent",
    ),
    # 119
    (
        "We have dozens of siloed KPIs in separate dashboards that tell conflicting stories. Begin by designing a single "
        "visual layer that reconciles and prioritizes these metrics, while coordinating with upstream agents only when data "
        "issues surface through visual inconsistencies.",
        "VizAgent",
    ),
    # 120
    (
        "Leadership wants a visual narrative for the last year: launches, outages, experiments, and business outcomes. "
        "Metrics and events are all available; your first step is to craft a set of interconnected visuals that tell this "
        "story, and then other agents can refine or extend the analysis.",
        "VizAgent",
    ),

    # ============================================================
    # 121–200: EDGE CASES, VAGUE, AMBIGUOUS, HARD-TO-DISTINGUISH
    # ============================================================

    # Some are vague but we choose a reasonable first agent.

    # 121
    (
        "This dataset looks messy and I’m not even sure what columns are trustworthy. Where should we start?",
        "DataEngAgent",
    ),
    # 122
    (
        "We keep getting different numbers for the same KPI from different reports, and nobody trusts the data anymore.",
        "DataEngAgent",
    ),
    # 123
    (
        "Before we build anything fancy, I want to be sure the raw logs and warehouse tables are actually consistent.",
        "DataEngAgent",
    ),
    # 124
    (
        "People say the dashboards are wrong, but I suspect the problem is upstream in how we ingest and join the data.",
        "DataEngAgent",
    ),
    # 125
    (
        "We merged several tables by hand and now results feel off; I need someone to untangle this mess and rebuild it properly.",
        "DataEngAgent",
    ),

    # 126
    (
        "I just want to understand whether these differences we are seeing could have happened by chance or not.",
        "StatisticsAgent",
    ),
    # 127
    (
        "Leadership keeps asking if the new feature actually moved the needle or if we’re just seeing random noise.",
        "StatisticsAgent",
    ),
    # 128
    (
        "These metrics are going up and down every week; can you tell if there is any meaningful trend here?",
        "StatisticsAgent",
    ),
    # 129
    (
        "We tried a bunch of changes at once and now it’s unclear which, if any, made a real impact.",
        "StatisticsAgent",
    ),
    # 130
    (
        "I have a small sample and I’m not sure we can draw reliable conclusions from it.",
        "StatisticsAgent",
    ),

    # 131
    (
        "The team wants something that predicts which users matter most, but they’re vague about what that means exactly.",
        "MLAgent",
    ),
    # 132
    (
        "Everyone is saying we need AI to score leads, even though we’re not sure what data is available or useful.",
        "MLAgent",
    ),
    # 133
    (
        "We have lots of behavioral data and leadership just says, ‘Turn this into a model that helps us grow.’",
        "MLAgent",
    ),
    # 134
    (
        "People ask for a system that flags risky customers ahead of time, but don’t agree on the exact definition of risk.",
        "MLAgent",
    ),
    # 135
    (
        "We want to explore what machine learning could do with our current data without committing to a specific use case yet.",
        "MLAgent",
    ),

    # 136
    (
        "Right now we have tables, reports, and models, but no one can quickly see the big picture in one place.",
        "VizAgent",
    ),
    # 137
    (
        "Stakeholders keep asking for something visual that helps them ‘get it’ without reading long documents.",
        "VizAgent",
    ),
    # 138
    (
        "Our existing dashboards feel cluttered and confusing; people scroll around and still don’t know what’s happening.",
        "VizAgent",
    ),
    # 139
    (
        "I need a way to explore this data interactively because static tables aren’t helping me see any patterns.",
        "VizAgent",
    ),
    # 140
    (
        "Executives just say, ‘Make the data tell a story,’ but they won’t specify which metrics or models they care about.",
        "VizAgent",
    ),

    # Mixed or misleading edge cases

    # 141
    (
        "Can you take this gigantic CSV from marketing, clean it up, and then tell me whether the new campaigns worked?",
        "DataEngAgent",
    ),
    # 142
    (
        "We’ve already cleaned most of the data, but I want to know if there is real evidence that this redesign improved retention.",
        "StatisticsAgent",
    ),
    # 143
    (
        "Once the numbers are trustworthy, I’d like a model that predicts which customers are likely to buy again.",
        "MLAgent",
    ),
    # 144
    (
        "After we figure out what’s actually going on in the data, I want a dashboard that makes it obvious to everyone.",
        "VizAgent",
    ),
    # 145
    (
        "Help me figure out if the way the data is stored is the real reason our reports keep contradicting each other.",
        "DataEngAgent",
    ),

    # 146
    (
        "I don’t know if we should start with visual exploration, formal tests, or just build a model and see what happens.",
        "StatisticsAgent",
    ),
    # 147
    (
        "There are so many potential inputs that I’d rather see a model try to tease out the important ones first.",
        "MLAgent",
    ),
    # 148
    (
        "We need something visual that can quickly reveal whether the last few changes made things better or worse.",
        "VizAgent",
    ),
    # 149
    (
        "The main complaint is that people can’t find a single trusted definition of ‘active user’ across systems.",
        "DataEngAgent",
    ),
    # 150
    (
        "I suspect we’re overreacting to noise, but we lack a disciplined way to check which changes truly matter.",
        "StatisticsAgent",
    ),

    # more ambiguous / tricky ones

    # 151
    (
        "Can you look at this dataset and tell us what kind of questions we can realistically answer with it?",
        "StatisticsAgent",
    ),
    # 152
    (
        "We have dashboards, but they never quite match what people are seeing in the raw logs.",
        "DataEngAgent",
    ),
    # 153
    (
        "Everyone says we should use machine learning because the relationships are probably nonlinear and complicated.",
        "MLAgent",
    ),
    # 154
    (
        "I want a visual overview that makes it clear where our data is solid and where it’s too noisy to trust.",
        "VizAgent",
    ),
    # 155
    (
        "Our experiment results look promising, but I’m worried we might be cherry-picking metrics that happened to move.",
        "StatisticsAgent",
    ),

    # 156
    (
        "We keep bolting on new derived tables, and it’s unclear which ones are still correct or even used.",
        "DataEngAgent",
    ),
    # 157
    (
        "There are a bunch of ad-hoc models in notebooks, and leadership wants something more systematic.",
        "MLAgent",
    ),
    # 158
    (
        "I need a way to visually compare what multiple models are doing without reading through hundreds of log lines.",
        "VizAgent",
    ),
    # 159
    (
        "Before we forecast anything, I’d like to know whether past patterns are stable enough to justify a model.",
        "StatisticsAgent",
    ),
    # 160
    (
        "Our main metric jumped last quarter, but we also changed tracking, pricing, and onboarding at the same time.",
        "StatisticsAgent",
    ),

    # 161
    (
        "The ETL jobs ‘succeed’ but analysts keep finding missing or duplicated records in their queries.",
        "DataEngAgent",
    ),
    # 162
    (
        "We want to explore whether a small proof-of-concept model can meaningfully help decisions before doing a big project.",
        "MLAgent",
    ),
    # 163
    (
        "Non-technical stakeholders say they’ll only trust the work if they can see it explained visually.",
        "VizAgent",
    ),
    # 164
    (
        "Right now, we sample just a subset of data for analysis; I’m worried this might bias our conclusions.",
        "StatisticsAgent",
    ),
    # 165
    (
        "Even simple queries are slow, and people resort to exporting data and hacking in spreadsheets.",
        "DataEngAgent",
    ),

    # 166
    (
        "Executives want a predictive ‘early warning system’ but have not specified which signals would count as a warning.",
        "MLAgent",
    ),
    # 167
    (
        "The design team wants to show our impact with visuals that are compelling but not misleading.",
        "VizAgent",
    ),
    # 168
    (
        "This is an old dataset with unclear provenance; we need to decide whether it’s even usable.",
        "DataEngAgent",
    ),
    # 169
    (
        "Stakeholders are skeptical of the model because they never saw any basic descriptive statistics.",
        "StatisticsAgent",
    ),
    # 170
    (
        "We log a ton of features and events, and leadership wants ‘some kind of AI’ to summarize what matters.",
        "MLAgent",
    ),

    # 171
    (
        "The most common request is ‘just give me one page where I can see what’s happening right now.’",
        "VizAgent",
    ),
    # 172
    (
        "Our schema has evolved so many times that even simple joins are error-prone.",
        "DataEngAgent",
    ),
    # 173
    (
        "We’ve launched many small changes, and I’d like to know whether overall they helped or hurt key outcomes.",
        "StatisticsAgent",
    ),
    # 174
    (
        "People ask for lead scoring, churn prediction, and anomaly detection all at once, without choosing priorities.",
        "MLAgent",
    ),
    # 175
    (
        "Different teams screenshot different parts of dashboards to make their case; there’s no single agreed-upon view.",
        "VizAgent",
    ),

    # 176
    (
        "Our raw logs keep changing shape when new features are added, and downstream queries break unexpectedly.",
        "DataEngAgent",
    ),
    # 177
    (
        "We sometimes see huge spikes in metrics that might be bugs, bots, or genuine events; it’s hard to tell.",
        "StatisticsAgent",
    ),
    # 178
    (
        "Management wants the system to ‘learn from experience’ and improve predictions over time.",
        "MLAgent",
    ),
    # 179
    (
        "People mostly ignore the existing dashboards, saying they’re too noisy and don’t highlight what matters.",
        "VizAgent",
    ),
    # 180
    (
        "We suspect that different regions follow different patterns, but our current data setup doesn’t make that obvious.",
        "DataEngAgent",
    ),

    # 181
    (
        "Most arguments in meetings boil down to ‘is this change real or just noise in the data.’",
        "StatisticsAgent",
    ),
    # 182
    (
        "We’d like to see if simple baseline models are already good enough before investing in anything more complex.",
        "MLAgent",
    ),
    # 183
    (
        "The CEO wants a single picture that explains why last quarter looked so strange.",
        "VizAgent",
    ),
    # 184
    (
        "There are rows with impossible dates and negative counts showing up in multiple tables.",
        "DataEngAgent",
    ),
    # 185
    (
        "Analysts are running many hypothesis tests and I’m concerned about false discoveries and p-hacking.",
        "StatisticsAgent",
    ),

    # 186
    (
        "We don’t know which combination of features, if any, can predict long-term customer success.",
        "MLAgent",
    ),
    # 187
    (
        "Our key charts don’t adapt well to new metrics or changes in the business, and become outdated quickly.",
        "VizAgent",
    ),
    # 188
    (
        "The same user seems to appear under multiple IDs, making all downstream analysis a little suspicious.",
        "DataEngAgent",
    ),
    # 189
    (
        "We keep seeing nice looking graphs attached to weak statistical arguments in internal docs.",
        "StatisticsAgent",
    ),
    # 190
    (
        "Leadership has heard about deep learning and keeps asking whether we’re ‘using it yet’ anywhere.",
        "MLAgent",
    ),

    # 191
    (
        "Teams screenshot different parts of different dashboards to support conflicting stories about performance.",
        "VizAgent",
    ),
    # 192
    (
        "We changed our definition of an active user several times and never fully backfilled the historical data.",
        "DataEngAgent",
    ),
    # 193
    (
        "I’d like a principled way to decide which metrics we should pay attention to and which to ignore.",
        "StatisticsAgent",
    ),
    # 194
    (
        "Whenever a new feature launches, the first question is always ‘can we train a model on this?’",
        "MLAgent",
    ),
    # 195
    (
        "People scroll through dashboards without a clear sense of what they’re supposed to be looking for.",
        "VizAgent",
    ),

    # 196
    (
        "Different analysts create slightly different transformations of the same source data, leading to quiet divergence.",
        "DataEngAgent",
    ),
    # 197
    (
        "We’ve never really checked whether our favorite metrics are actually predictive of the outcomes we care about.",
        "StatisticsAgent",
    ),
    # 198
    (
        "The company wants to be seen as ‘AI-powered’, but we’re not sure which problems are actually good candidates.",
        "MLAgent",
    ),
    # 199
    (
        "Executives want a single, coherent visual that connects experiments, outages, and metrics into one narrative.",
        "VizAgent",
    ),
    # 200
    (
        "Our entire stack has grown organically, and we need to decide where to begin fixing data, analysis, models, and reporting.",
        "DataEngAgent",
    ),
]
