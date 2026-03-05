"""10 test queries for DataEngAgent Complex."""

# ============================================================================
# QUERY 1: Domain Classification - IN_DOMAIN (SQL Query)
# ============================================================================
# Task: SQL query generation
# Expected: IN_DOMAIN, task_type=sql_query
# Status: No file I/O

query_1 = """
Write a SQL query that finds all customers who made purchases in the last 30 days 
and have a total spending above $500, ordered by spending in descending order.
"""

# ============================================================================
# QUERY 2: Domain Classification - OUT_OF_DOMAIN (Routing)
# ============================================================================
# Task: Should recommend MLAgent
# Expected: OUT_OF_DOMAIN, recommend=['MLAgent']
# Status: No file I/O

query_2 = """
I have a dataset of customer features. Should I use a neural network or a decision tree 
for predicting customer churn? What's the difference in approach?
"""

# ============================================================================
# QUERY 3: File Reading - Data Quality Analysis
# ============================================================================
# Task: Analyze test_data.csv for data quality issues
# Expected: IN_DOMAIN, task_type=data_cleaning, files_analyzed=1, code_executions>0
# Status: READS FILE - test_data.csv
# Output: Will show data quality metrics

query_3 = """
FILE: test_data.csv
Analyze this dataset for data quality issues. Check for missing values, duplicates, 
outliers, and data type inconsistencies. Provide a summary report.
"""

# ============================================================================
# QUERY 4: File Reading + Output - Data Cleaning Plan
# ============================================================================
# Task: Create a data cleaning script and save it
# Expected: IN_DOMAIN, task_type=data_cleaning, files_analyzed=1
# Files Generated: data_cleaning_script.txt, data_quality_report.txt
# Status: READS test_data.csv, WRITES text files

query_4 = """
FILE: test_data.csv 
Create a data cleaning plan for this dataset. Save a Python script called 
'data_cleaning_script.txt' that shows how to handle missing values, remove duplicates, 
and standardize column names. Also save a summary report to 'data_quality_report.txt'.
"""

# ============================================================================
# QUERY 5: Schema Design from File
# ============================================================================
# Task: Analyze file structure and recommend schema
# Expected: IN_DOMAIN, task_type=schema_design, files_analyzed=1
# Status: READS test_data.csv and analyzes structure

query_5 = """
FILE: test_data.csv
Examine this dataset and design a normalized database schema (3NF) that could store 
this data. Include table definitions with appropriate data types, primary keys, 
and any foreign key relationships you would recommend.
"""

# ============================================================================
# QUERY 6: File Output - SQL Schema Definition
# ============================================================================
# Task: Generate SQL CREATE statements and save
# Expected: IN_DOMAIN, task_type=schema_design
# Files Generated: student_database_schema.sql
# Status: WRITES SQL file

query_6 = """
Design a database schema for a university system with students, courses, enrollments, 
and grades. Generate the SQL CREATE TABLE statements and save them to a file called 
'student_database_schema.sql'. Include all necessary constraints and relationships.
"""

# ============================================================================
# QUERY 7: ETL Pipeline Design with File Output
# ============================================================================
# Task: Design ETL pipeline and save plan
# Expected: IN_DOMAIN, task_type=etl_pipeline
# Files Generated: etl_pipeline_design.txt
# Status: WRITES text file

query_7 = """
Design an ETL pipeline that would:
1. Extract data from multiple CSV files
2. Transform and clean the data
3. Load into a relational database

Save your pipeline design (including pseudocode) to a file called 'etl_pipeline_design.txt' 
with detailed steps, error handling, and performance considerations.
"""

# ============================================================================
# QUERY 8: Performance Tuning Recommendations
# ============================================================================
# Task: Query optimization and indexing strategy
# Expected: IN_DOMAIN, task_type=performance_tuning
# Status: No file I/O (pure explanation)

query_8 = """
I have a query that joins three large tables (customers: 1M rows, orders: 10M rows, 
order_items: 50M rows) and filters by date range. It's currently taking 30 seconds. 
What indexing strategy would you recommend? Write the CREATE INDEX statements.
"""

# ============================================================================
# QUERY 9: File Reading + Multiple Tasks
# ============================================================================
# Task: Comprehensive analysis with multiple recommendations
# Expected: IN_DOMAIN, task_type=data_cleaning or etl_pipeline, files_analyzed=1
# Status: READS test_data.csv, WRITES analysis files

query_9 = """
FILE: test_data.csv 
Perform a comprehensive data engineering assessment:
1. Identify data quality issues
2. Recommend a schema design
3. Suggest an ETL process to load this data
4. Identify performance optimization opportunities

Save all findings to a file called 'comprehensive_data_assessment.txt'.
"""

# ============================================================================
# QUERY 10: Storage Architecture (No File I/O)
# ============================================================================
# Task: Architecture design and recommendations
# Expected: IN_DOMAIN, task_type=storage_architecture
# Status: No file I/O (pure design guidance)

query_10 = """
Design a data warehouse architecture for an e-commerce platform that needs to:
- Store 100GB of customer transaction data
- Support real-time analytics queries
- Handle daily batch processing of 1M new transactions
- Archive historical data after 2 years

Compare data lake vs warehouse approaches and recommend which is best for this scenario.
"""

# ============================================================================
# SUMMARY TABLE
# ============================================================================

QUERIES = [
    {
        "number": 1,
        "title": "SQL Query Generation",
        "query": query_1,
        "files_read": [],
        "files_written": [],
        "expected_task": "sql_query",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 2,
        "title": "OUT_OF_DOMAIN Routing (ML Agent)",
        "query": query_2,
        "files_read": [],
        "files_written": [],
        "expected_task": "other",
        "expected_domain": "OUT_OF_DOMAIN"
    },
    {
        "number": 3,
        "title": "File Reading - Data Quality Check",
        "query": query_3,
        "files_read": ["test_data.csv"],
        "files_written": [],
        "expected_task": "data_cleaning",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 4,
        "title": "File Reading + Output - Data Cleaning Plan",
        "query": query_4,
        "files_read": ["test_data.csv"],
        "files_written": ["data_cleaning_script.txt", "data_quality_report.txt"],
        "expected_task": "data_cleaning",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 5,
        "title": "Schema Design from File Analysis",
        "query": query_5,
        "files_read": ["test_data.csv"],
        "files_written": [],
        "expected_task": "schema_design",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 6,
        "title": "SQL Schema Definition Output",
        "query": query_6,
        "files_read": [],
        "files_written": ["student_database_schema.sql"],
        "expected_task": "schema_design",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 7,
        "title": "ETL Pipeline Design with Output",
        "query": query_7,
        "files_read": [],
        "files_written": ["etl_pipeline_design.txt"],
        "expected_task": "etl_pipeline",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 8,
        "title": "Performance Tuning Recommendations",
        "query": query_8,
        "files_read": [],
        "files_written": [],
        "expected_task": "performance_tuning",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 9,
        "title": "Comprehensive Data Assessment",
        "query": query_9,
        "files_read": ["test_data.csv"],
        "files_written": ["comprehensive_data_assessment.txt"],
        "expected_task": "data_cleaning",
        "expected_domain": "IN_DOMAIN"
    },
    {
        "number": 10,
        "title": "Storage Architecture Design",
        "query": query_10,
        "files_read": [],
        "files_written": [],
        "expected_task": "storage_architecture",
        "expected_domain": "IN_DOMAIN"
    }
]


def print_query_guide():
    print("\n" + "="*80)
    print("DATAENGAGENT COMPLEX - 10 TEST QUERIES")
    print("="*80)
    
    for q in QUERIES:
        print(f"\n{'─'*80}")
        print(f"QUERY {q['number']}: {q['title']}")
        print(f"{'─'*80}")
        print(f"Expected Domain: {q['expected_domain']}")
        print(f"Expected Task Type: {q['expected_task']}")
        print(f"Files to Read: {q['files_read'] if q['files_read'] else 'None'}")
        print(f"Files to Generate: {q['files_written'] if q['files_written'] else 'None'}")
        print(f"\nQuery:\n{q['query']}")
    
    print("\n" + "="*80)
    print("HOW TO RUN THESE QUERIES")
    print("="*80)
    print("""
1. Start the data agent CLI:
   python data_agent/data_agent_complex.py

2. Copy and paste one complete query at a time (including FILE: prefix if needed)

3. Wait for response and check:
   - Domain classification is correct
   - Task type matches expectations
   - Files are generated (check with ls or dir)
   - Code execution was successful

4. For file-reading queries (3, 4, 5, 9):
   - Make sure test_data.csv exists in the project root
   - Use exact filename: test_data.csv

5. For file-writing queries (4, 6, 7, 9):
   - Check the generated files in the project directory
   - Verify content looks correct

Example Run:
   $ python data_agent/data_agent_complex.py
   You: FILE: test_data.csv
       Analyze this dataset for data quality issues...
   [Agent responds]
   You: exit
""")
    
    print("\n" + "="*80)
    print("QUERY SUMMARY")
    print("="*80)
    print(f"\nTotal Queries: {len(QUERIES)}")
    print(f"File-Reading Queries: {sum(1 for q in QUERIES if q['files_read'])}")
    print(f"File-Writing Queries: {sum(1 for q in QUERIES if q['files_written'])}")
    print(f"Pure IN_DOMAIN: {sum(1 for q in QUERIES if q['expected_domain'] == 'IN_DOMAIN')}")
    print(f"Routing Tests (OUT_OF_DOMAIN): {sum(1 for q in QUERIES if q['expected_domain'] == 'OUT_OF_DOMAIN')}")


if __name__ == "__main__":
    print_query_guide()
