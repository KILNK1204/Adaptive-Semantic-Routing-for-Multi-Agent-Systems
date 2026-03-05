# 100 labelled training queries for the success-rate / performance router.
# Each entry is (query_text, expected_first_agent).
# Agents: "DataEngAgent", "StatisticsAgent", "MLAgent", "VizAgent"

TRAINING_QUERIES = [

    # =========================
    # 50 SHORT QUERIES
    # =========================

    # --- DataEngAgent short ---
    
    (
        "Load the raw CSV files and fix obvious schema inconsistencies first.",
        "DataEngAgent",
    ),
    (
        "Connect to the database and check for missing values in key columns.",
        "DataEngAgent",
    ),
    (
        "Build an ETL job that merges these daily logs into a clean table.",
        "DataEngAgent",
    ),
    (
        "Normalize these messy spreadsheets into a proper relational schema.",
        "DataEngAgent",
    ),
    (
        "Profile this sales table and flag clearly corrupt or duplicated rows.",
        "DataEngAgent",
    ),
    (
        "Set up a pipeline that ingests JSON events and enforces a fixed schema.",
        "DataEngAgent",
    ),
    (
        "Aggregate raw clickstream logs into hourly sessions ready for analysis.",
        "DataEngAgent",
    ),
    (
        "Backfill missing metrics in this warehouse table using existing history.",
        "DataEngAgent",
    ),
    (
        "Design an efficient partitioning strategy for this very large fact table.",
        "DataEngAgent",
    ),
    (
        "Rewrite these slow SQL queries so they perform well on our warehouse.",
        "DataEngAgent",
    ),
    (
        "Migrate this legacy denormalized layout into a star schema for BI use.",
        "DataEngAgent",
    ),
    (
        "Validate data quality across regions before anyone starts analyzing it.",
        "DataEngAgent",
    ),

    # --- StatisticsAgent short ---
    (
        "Test whether the average conversion rate differs between these two groups.",
        "StatisticsAgent",
    ),
    (
        "Compute confidence intervals for this proportion and interpret them.",
        "StatisticsAgent",
    ),
    (
        "Check if this numeric variable is approximately normally distributed.",
        "StatisticsAgent",
    ),
    (
        "Run an ANOVA to compare means across these four experimental conditions.",
        "StatisticsAgent",
    ),
    (
        "Perform a chi-square test of independence between these two categorical variables.",
        "StatisticsAgent",
    ),
    (
        "Fit a simple linear regression and report the slope and p-value.",
        "StatisticsAgent",
    ),
    (
        "Calculate correlation between these features and discuss its strength.",
        "StatisticsAgent",
    ),
    (
        "Estimate the required sample size for achieving a desired power level.",
        "StatisticsAgent",
    ),
    (
        "Check regression residuals for violations of model assumptions.",
        "StatisticsAgent",
    ),
    (
        "Compare these two proportions and tell me if they differ significantly.",
        "StatisticsAgent",
    ),
    (
        "Summarize this dataset with descriptive statistics and basic plots.",
        "StatisticsAgent",
    ),
    (
        "Perform a paired t-test on before-and-after measurements.",
        "StatisticsAgent",
    ),
    (
        "Compute a Bayesian credible interval for this parameter.",
        "StatisticsAgent",
    ),

    # --- MLAgent short ---
    (
        "Train a random forest classifier on these labeled features.",
        "MLAgent",
    ),
    (
        "Build a gradient boosting model and evaluate its performance.",
        "MLAgent",
    ),
    (
        "Construct a neural network for this image classification task.",
        "MLAgent",
    ),
    (
        "Tune hyperparameters for this model using cross-validation.",
        "MLAgent",
    ),
    (
        "Train a support vector machine for binary classification.",
        "MLAgent",
    ),
    (
        "Perform feature selection to improve prediction quality.",
        "MLAgent",
    ),
    (
        "Build a regression model and compare several algorithms.",
        "MLAgent",
    ),
    (
        "Train a clustering model to discover groups in this dataset.",
        "MLAgent",
    ),
    (
        "Create a pipeline that scales features and trains a classifier.",
        "MLAgent",
    ),
    (
        "Evaluate this model with precision, recall, and F1 score.",
        "MLAgent",
    ),
    (
        "Calibrate the probabilities of this existing classification model.",
        "MLAgent",
    ),
    (
        "Perform model stacking to improve prediction accuracy.",
        "MLAgent",
    ),
    (
        "Train a time-series forecasting model for these demand values.",
        "MLAgent",
    ),

    # --- VizAgent short ---
    (
        "Create a line chart showing revenue by month for the last two years.",
        "VizAgent",
    ),
    (
        "Make a bar chart comparing sales across product categories.",
        "VizAgent",
    ),
    (
        "Plot a scatter diagram of price versus units sold.",
        "VizAgent",
    ),
    (
        "Build a dashboard with key KPIs and simple filters.",
        "VizAgent",
    ),
    (
        "Draw a histogram of this variable to show its distribution.",
        "VizAgent",
    ),
    (
        "Create a box plot to highlight outliers in delivery times.",
        "VizAgent",
    ),
    (
        "Design a heatmap of the correlation matrix for these features.",
        "VizAgent",
    ),
    (
        "Make a pie chart showing market share by region.",
        "VizAgent",
    ),
    (
        "Build an interactive dashboard for monitoring daily signups.",
        "VizAgent",
    ),
    (
        "Visualize this confusion matrix as a clear annotated chart.",
        "VizAgent",
    ),
    (
        "Create a set of small multiples showing trends per country.",
        "VizAgent",
    ),
    (
        "Design a simple funnel visualization for the acquisition pipeline.",
        "VizAgent",
    ),

    # Extra short, slightly tricky multi-goal ones
    (
        "First clean this export from the CRM, then others can explore it further.",
        "DataEngAgent",
    ),
    (
        "Start by testing whether this new feature really improves key metrics.",
        "StatisticsAgent",
    ),

    # =========================
    # 50 COMPLEX QUERIES
    # =========================

    # --- DataEngAgent complex ---
    (
        "We have a collection of inconsistent CSVs exported by different teams over several years. "
        "Begin by standardizing column names and types, resolving conflicting encodings, removing "
        "obviously corrupted rows, and producing a single trusted table that statistics, machine "
        "learning, and visualization agents can safely build on later.",
        "DataEngAgent",
    ),
    (
        "Our clickstream is stored as semi-structured JSON blobs in an object store, with frequent "
        "schema drift and missing fields. Start by designing and implementing a robust ingestion "
        "pipeline that parses the events, enforces a stable schema, and materializes clean session "
        "tables before anyone attempts modelling or dashboarding.",
        "DataEngAgent",
    ),
    (
        "The finance department sends monthly Excel workbooks with slightly different layouts, "
        "header names, and currency formats. First design a repeatable ETL process that extracts "
        "the relevant sheets, normalizes the units, merges all months into a coherent fact table, "
        "and documents assumptions for downstream analytical agents.",
        "DataEngAgent",
    ),
    (
        "Our legacy transactional database was never designed for analytics and now powers several "
        "dashboards that time out. Start by profiling the current schema, identifying the core fact "
        "and dimension entities, and building a warehouse-style model with appropriate indexes and "
        "materialized views so analysts and statisticians can query efficiently.",
        "DataEngAgent",
    ),
    (
        "Sensor events from multiple factories arrive with inconsistent timestamps, missing device "
        "identifiers, and occasional duplicate records. Your first responsibility is to build a "
        "data engineering pipeline that aligns time zones, deduplicates events, imputes reasonable "
        "defaults where possible, and outputs a clean time-series dataset for further analysis.",
        "DataEngAgent",
    ),
    (
        "The CRM, billing system, and support ticketing tool each hold partial views of the customer. "
        "Start by designing a reliable master customer table that reconciles identifiers, resolves "
        "conflicts between sources, and exposes unified attributes before any statistical modeling "
        "or churn prediction models are considered.",
        "DataEngAgent",
    ),
    (
        "We are migrating from on-prem databases to a cloud warehouse, and historical tables contain "
        "both obsolete columns and outdated encodings. Begin by planning and implementing the data "
        "migration, cleaning and restructuring tables so that later agents focusing on forecasting or "
        "visualization can treat the new warehouse as their single source of truth.",
        "DataEngAgent",
    ),
    (
        "Marketing wants to analyze campaign performance, but the raw tracking logs contain bots, "
        "test events, and malformed URLs. First construct a robust ETL job that filters out invalid "
        "events, resolves campaign identifiers, and aggregates metrics at the right grain before "
        "any significance testing or causal inference is attempted.",
        "DataEngAgent",
    ),
    (
        "For our analytics platform, we need a consistent definition of an active user. Begin by "
        "engineering data transformations that combine login events, feature usage, and subscription "
        "status into a clear activity table, which statisticians and machine learning agents can then "
        "use for retention and engagement studies.",
        "DataEngAgent",
    ),
    (
        "Different teams have been manually editing spreadsheets of product information, leading to "
        "inconsistent names, duplicated rows, and missing keys. Start by consolidating these sheets, "
        "building reference tables, and enforcing constraints so that later forecasting and reporting "
        "work is grounded on a trusted product catalog.",
        "DataEngAgent",
    ),
    (
        "We want a near-real-time view of orders, but current batch jobs run nightly and often fail. "
        "Your first task is to design a streaming or micro-batch data pipeline that reliably captures "
        "new orders, handles retries, and updates a central orders table, which downstream agents "
        "can then analyze or visualize.",
        "DataEngAgent",
    ),
    (
        "Our data lake has grown organically without governance, with duplicated folders and "
        "mysterious tables. Begin by cataloging the existing datasets, removing obsolete copies, and "
        "establishing clear, well-documented canonical tables to be used by statistical and machine "
        "learning workflows going forward.",
        "DataEngAgent",
    ),

    # --- StatisticsAgent complex ---
    (
        "Given a cleaned dataset from a recent A/B experiment, start by formulating precise null and "
        "alternative hypotheses, checking randomization quality, and running appropriate significance "
        "tests. Only after we understand the statistical evidence should we ask other agents to build "
        "fancy predictive models or dashboards around the results.",
        "StatisticsAgent",
    ),
    (
        "We have monthly revenue data across several regions and marketing channels. First perform a "
        "thorough exploratory analysis, compute correlations, fit basic regression models with clear "
        "diagnostics, and assess seasonality before suggesting any complex forecasting pipelines or "
        "visualizations for stakeholders.",
        "StatisticsAgent",
    ),
    (
        "Our product team suspects that a new onboarding flow improves user engagement. Begin by "
        "testing this hypothesis using the experimental data, accounting for potential confounders, "
        "computing effect sizes and confidence intervals, and only then consider involving machine "
        "learning agents to predict long-term retention.",
        "StatisticsAgent",
    ),
    (
        "A clinical study has collected outcomes for treatment and control groups with some missing "
        "values. Start with an appropriate missing-data strategy, evaluate baseline balance, run "
        "the main inferential tests, and quantify uncertainty before asking others to build any "
        "visual storytelling or predictive risk scores on top.",
        "StatisticsAgent",
    ),
    (
        "We track customer satisfaction scores over time and by segment. First use statistical models "
        "to understand which segments truly differ, account for multiple comparisons, and determine "
        "whether observed changes are likely due to chance before any dashboards or ML models are "
        "positioned as evidence of improvement.",
        "StatisticsAgent",
    ),
    (
        "Our churn dataset has many potential predictors. Begin by exploring the distributions, "
        "checking multicollinearity, and fitting interpretable baseline models with well-examined "
        "residuals. Only after the statistical groundwork is solid should more complex machine "
        "learning pipelines be proposed.",
        "StatisticsAgent",
    ),
    (
        "We want to know if recent marketing campaigns have changed the distribution of purchases. "
        "First design the right significance tests or time-series interventions, evaluate their "
        "results with confidence intervals and visual diagnostics, and then decide whether creating "
        "predictive models is justified.",
        "StatisticsAgent",
    ),
    (
        "The company suspects that seasonality masks the effect of a new pricing strategy. Begin by "
        "using appropriate statistical decomposition and modeling, evaluate interactions between "
        "season and price, and clearly quantify uncertainty before recommending any automated "
        "forecasting tools or dashboards.",
        "StatisticsAgent",
    ),
    (
        "We collected survey responses with Likert-scale questions and demographic attributes. Start "
        "by summarizing response distributions, testing group differences with robust methods, and "
        "carefully interpreting effect sizes before anyone designs dashboards or recommendation "
        "models based on these attitudes.",
        "StatisticsAgent",
    ),
    (
        "Our operations team wants to detect whether process changes truly reduced defect rates. "
        "First analyze the pre- and post-change data using proper statistical tests, handle any "
        "overdispersion or time trends, and report clear conclusions before suggesting real-time "
        "monitoring or predictive models.",
        "StatisticsAgent",
    ),
    (
        "We need to understand the drivers of employee attrition. Begin with statistical modeling "
        "that includes confidence intervals, hypothesis tests, and diagnostics for assumptions, and "
        "only then escalate to more opaque machine learning models if they offer a measurable "
        "benefit over interpretable baselines.",
        "StatisticsAgent",
    ),
    (
        "A new policy was introduced midyear, and leadership wants to know if it improved key "
        "metrics. Start by designing a quasi-experimental analysis, checking for parallel trends, "
        "quantifying uncertainty, and explaining limitations before translating the findings into "
        "dashboards or ML-powered alerts.",
        "StatisticsAgent",
    ),

    # --- MLAgent complex ---
    (
        "Assume we already have a clean feature table and some basic statistical checks completed. "
        "Your first task is to design and train a robust classification pipeline for churn prediction, "
        "including feature engineering, model selection, hyperparameter tuning, and evaluation using "
        "appropriate metrics before any visualization polish is added.",
        "MLAgent",
    ),
    (
        "Given a prepared dataset of historical orders with many attributes, start by benchmarking "
        "several regression algorithms for revenue prediction, perform cross-validation, tune key "
        "hyperparameters, and compare models using both accuracy and calibration before asking other "
        "agents to produce explanatory charts for executives.",
        "MLAgent",
    ),
    (
        "For this image dataset of product photos, assume the labels and preprocessing are already "
        "handled. Focus on building and training a convolutional neural network, experimenting with "
        "data augmentation and architecture choices, and report the best model's performance so that "
        "visualization agents can later create interpretability plots.",
        "MLAgent",
    ),
    (
        "We have user interaction logs summarized into features by a data engineering pipeline. "
        "Begin by training ranking or recommendation models, such as matrix factorization or neural "
        "recommendation systems, tuning them for precision and recall, and only afterwards consider "
        "how to depict their behavior in dashboards.",
        "MLAgent",
    ),
    (
        "There is a multivariate time-series of sensor readings with known failure events. Start by "
        "building forecasting and anomaly detection models that can predict failures in advance, "
        "train and evaluate them rigorously, and leave the creation of monitoring dashboards to a "
        "visualization specialist afterward.",
        "MLAgent",
    ),
    (
        "For this text dataset of customer reviews, suppose we already have tokenized inputs. Focus "
        "first on training sentiment analysis models, comparing classical approaches to transformer "
        "architectures, tuning them for robust performance, and later invite statistics or viz agents "
        "to help interpret aggregate effects.",
        "MLAgent",
    ),
    (
        "We want to segment our customers into actionable groups. Start by experimenting with "
        "different clustering algorithms, selecting meaningful features, choosing the number of "
        "clusters based on quantitative criteria, and then hand off the resulting segments to "
        "visualization agents for storytelling.",
        "MLAgent",
    ),
    (
        "Our fraud team needs a model that flags suspicious transactions. Assume the data is "
        "prepared and balanced as much as possible. Begin by training and evaluating multiple "
        "classification algorithms with careful attention to recall and false positives, and then "
        "share the best model's outputs for further analysis.",
        "MLAgent",
    ),
    (
        "Marketing wants uplift modeling to target users who respond positively to offers. Start by "
        "constructing appropriate treatment and control features, training uplift or causal models, "
        "and evaluating them, leaving any detailed statistical interpretation or visualization to "
        "other agents once the model works well.",
        "MLAgent",
    ),
    (
        "Our demand forecasting currently uses simple spreadsheets. With a clean historical series "
        "already available, begin by building machine learning forecasting models, such as gradient "
        "boosting or deep learning approaches, compare them to baselines, and only afterwards decide "
        "which views a dashboard should show.",
        "MLAgent",
    ),
    (
        "We maintain several models in production and suspect they are drifting. Starting from logs "
        "of predictions and outcomes that have been preprocessed, train diagnostic models or build "
        "meta-learners to detect drift and performance degradation before involving visualization "
        "specialists to present the findings.",
        "MLAgent",
    ),
    (
        "The company wants a lead scoring model that sales can trust. Assume features and labels are "
        "clean. First design an interpretable machine learning pipeline that balances performance and "
        "explainability, validate it thoroughly, and then pass summary results to visualization and "
        "statistics agents for communication.",
        "MLAgent",
    ),

    # --- VizAgent complex ---
    (
        "Leadership needs a single dashboard that tells a clear story about revenue, churn, and "
        "acquisition over time. Assume the metrics are already computed and trustworthy. Your first "
        "job is to design concise, interactive visualizations that highlight trends and anomalies, "
        "while deferring any new modeling or data fixes to other agents.",
        "VizAgent",
    ),
    (
        "The growth team wants to explore the user funnel visually. Start by creating a set of "
        "linked visualizations that show drop-off at each stage, allow filtering by segment, and "
        "make bottlenecks obvious, assuming that upstream agents have already prepared the necessary "
        "aggregated tables and metrics.",
        "VizAgent",
    ),
    (
        "We have many KPIs tracked across products and regions, and stakeholders are overwhelmed. "
        "Begin by designing an information-dense yet readable dashboard that organizes these metrics "
        "into coherent sections, uses appropriate chart types, and supports simple interactions, "
        "leaving any additional statistical modeling to specialists.",
        "VizAgent",
    ),
    (
        "The data science team has built several models, but executives only see raw numbers. Your "
        "first task is to craft visualizations that explain model performance, feature importance, "
        "and uncertainty in an accessible way, assuming that the underlying evaluation results are "
        "already computed by other agents.",
        "VizAgent",
    ),
    (
        "Customer success needs a live view of support volume, resolution time, and backlog. Start "
        "by creating an operational dashboard with real-time charts, thresholds, and alerts-friendly "
        "views, relying on upstream data engineering work to keep the metrics accurate and timely.",
        "VizAgent",
    ),
    (
        "Our public website will host an interactive analytics page for users to explore their own "
        "activity. Begin by designing intuitive, responsive visualizations with tooltips, filters, "
        "and sensible defaults, while assuming that all sensitive aggregation and data governance "
        "has already been handled by backend agents.",
        "VizAgent",
    ),
    (
        "The operations team wants to understand where warehouse bottlenecks occur during the day. "
        "Start by building time-of-day and station-level visualizations that reveal queue lengths, "
        "processing rates, and utilization, counting on data engineers and statisticians to ensure "
        "the underlying metrics are correct.",
        "VizAgent",
    ),
    (
        "Product managers need a way to quickly compare experiment results without reading long "
        "statistical reports. Your first role is to create clear experiment dashboards that show "
        "effect sizes, confidence intervals, and key metrics in visual form, built on top of data "
        "and statistics already vetted by other agents.",
        "VizAgent",
    ),
    (
        "We want to democratize data exploration for non-technical colleagues. Begin by designing an "
        "exploratory dashboard with simple controls, sensible defaults, and guardrails against "
        "misinterpretation, assuming that upstream ETL and metric definitions are stable and well "
        "documented.",
        "VizAgent",
    ),
    (
        "A complex network of services produces logs that are hard to reason about in text. Start by "
        "creating visualizations of dependencies, error rates, and latencies that help engineers "
        "spot problematic services quickly, leaving deeper causal analysis or modeling to other "
        "agents once patterns are visible.",
        "VizAgent",
    ),
    (
        "We have dozens of cohorts in our retention analysis and static tables are unreadable. Your "
        "first job is to build cohort plots and interactive charts that let analysts see retention "
        "patterns over time, assuming that cohort assignments were already computed upstream.",
        "VizAgent",
    ),
    (
        "Stakeholders are confused by multiple competing dashboards. Start by consolidating the most "
        "important views into a single, coherent visual interface that emphasizes clarity, reduces "
        "duplicate charts, and highlights key decisions, relying on upstream agents to ensure data "
        "quality and metric correctness.",
        "VizAgent",
    ),
    
    # --- DataEng-leaning edge cases ---
    (
        "Our dashboards keep disagreeing on basic KPIs, and I’m not sure whether the problem is in the raw logs, the joins, or the metrics.",
        "DataEngAgent",
    ),
    (
        "This CSV export looks suspicious with strange nulls and duplicated user IDs; before we do any analysis, someone needs to untangle it.",
        "DataEngAgent",
    ),
    (
        "Analysts keep rewriting the same joins in different ways and getting slightly different results; we need to sort out the underlying data model first.",
        "DataEngAgent",
    ),
    (
        "Even simple queries are slow and sometimes return inconsistent row counts; I suspect something is wrong in how the tables are built.",
        "DataEngAgent",
    ),
    (
        "I want to trust the numbers on our dashboards again, but I’m not convinced the upstream ETL jobs are doing what we think they are.",
        "DataEngAgent",
    ),

    # --- Statistics-leaning edge cases ---
    (
        "These metrics jump around every week and people keep overreacting; I need to know which changes are statistically meaningful and which are noise.",
        "StatisticsAgent",
    ),
    (
        "We tried several product tweaks at once and now conversions look different, but I’m not sure we can attribute the change to any single factor.",
        "StatisticsAgent",
    ),
    (
        "Two teams are arguing: one says the new feature helped, the other says the effect is random; I want a principled answer based on the data.",
        "StatisticsAgent",
    ),
    (
        "The sample size for our experiment is small and the results look dramatic; I need to know how much confidence we can reasonably have.",
        "StatisticsAgent",
    ),
    (
        "People keep cherry-picking metrics that moved in their favor; we need a disciplined way to test our hypotheses and avoid false discoveries.",
        "StatisticsAgent",
    ),

    # --- ML-leaning edge cases ---
    (
        "Leadership wants ‘some kind of AI’ that can look at all our historical behavior and surface which customers are truly high value.",
        "MLAgent",
    ),
    (
        "We have tons of logged features and outcomes, and the question is basically: can a model find useful patterns that humans keep missing?",
        "MLAgent",
    ),
    (
        "Everyone is asking for a predictive early-warning system for churn, even though they can’t agree on the exact definition of churn yet.",
        "MLAgent",
    ),
    (
        "We already did basic descriptive stats, but now we want to see how far we can push predictive performance on this outcome.",
        "MLAgent",
    ),
    (
        "The business wants to experiment with a small proof-of-concept model first, just to see whether prediction is even feasible with our data.",
        "MLAgent",
    ),

    # --- Viz-leaning edge cases ---
    (
        "Right now we have tables, metrics, and even a model, but no single visual overview that helps non-technical stakeholders understand the story.",
        "VizAgent",
    ),
    (
        "People scroll through pages of dashboards and still can’t tell whether the situation is good or bad; we need something clearer and more focused.",
        "VizAgent",
    ),
    (
        "Executives keep asking for ‘one page’ that shows what’s happening across products and regions without them having to dig into details.",
        "VizAgent",
    ),
    (
        "We already ran some analyses and models, but they’re stuck in notebooks; we need visuals that make the main insights obvious at a glance.",
        "VizAgent",
    ),
    (
        "Different teams screenshot different charts to support conflicting stories; I want a unified visual that reduces ambiguity instead of amplifying it.",
        "VizAgent",
    ),
]
