import json
import time
import os
import traceback
import re
from typing import List, Literal, Tuple, Optional, Dict, Any
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field


MODEL_NAME = "llama3.1"


class ExecutionResult(BaseModel):
    code: str = Field(..., description="The Python code that was executed.")
    success: bool = Field(..., description="Whether code executed without errors.")
    output: str = Field(default="", description="stdout/print output from the code execution.")
    error: str = Field(default="", description="Error message if execution failed.")


class FileMetadata(BaseModel):
    file_path: str = Field(..., description="Path to the file.")
    file_type: str = Field(..., description="Type of file (csv, json, txt, excel, sql, etc.).")
    size_bytes: int = Field(..., description="File size in bytes.")
    preview: str = Field(default="", description="First few lines or summary of file content.")


class DataEngAgentResponse(BaseModel):

    domain: Literal["IN_DOMAIN", "OUT_OF_DOMAIN"] = Field(
        ...,
        description=(
            "Whether the query is primarily about data engineering tasks "
            "(IN_DOMAIN) or something else (OUT_OF_DOMAIN)."
        ),
    )
    agent: Literal["DataEngAgent"] = Field(
        ...,
        description="Name of this agent (always 'DataEngAgent').",
    )
    recommend: List[str] = Field(
        default_factory=list,
        description=(
            "Names of OTHER agents that should handle follow-up work "
            "(e.g. ['StatisticsAgent', 'MLAgent']) or an empty list if none."
        ),
    )
    task_type: str = Field(
        ...,
        description=(
            "Short label describing the main data engineering task, e.g. "
            "'sql_query', 'schema_design', 'etl_pipeline', 'data_cleaning', "
            "'performance_tuning', 'storage_architecture', or 'other'."
        ),
    )
    difficulty: Literal["intro", "intermediate", "advanced"] = Field(
        ...,
        description=(
            "Rough difficulty for a student who has database and SQL knowledge."
        ),
    )
    answer: str = Field(
        ...,
        description="Final user-facing explanation and any SQL/design artifacts.",
    )
    files_analyzed: List[FileMetadata] = Field(
        default_factory=list,
        description="Metadata for all files processed.",
    )
    code_executions: List[ExecutionResult] = Field(
        default_factory=list,
        description="Results from executed code snippets.",
    )


_base_llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0.2,
    top_p=0.9,
    top_k=40,
)


def _read_file_content(file_path: str, max_preview_lines: int = 20) -> Tuple[str, str, str]:
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_type = path.suffix.lower().lstrip('.')
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        preview_lines = lines[:max_preview_lines]
        if len(lines) > max_preview_lines:
            preview_lines.append(f"... ({len(lines) - max_preview_lines} more lines)")
        preview = '\n'.join(preview_lines)
        
        return content, preview, file_type
        
    except UnicodeDecodeError:
        raise Exception(f"Cannot read file as text: {file_path}. Is it a binary file?")
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")


def _execute_code(code: str, available_data: Optional[Dict[str, Any]] = None) -> ExecutionResult:
    import sys
    from io import StringIO
    import builtins
    
    saved_files = []
    written_files = {}
    
    original_open = builtins.open
    
    def tracked_open(filename, mode='r', *args, **kwargs):
        if 'w' in mode:
            class FileWriter:
                def __init__(self, fname, f_mode):
                    from pathlib import Path
                    self.fname = fname
                    self.mode = f_mode
                    self.content = []
                    # Ensure output folder exists
                    self.output_dir = Path("output")
                    self.output_dir.mkdir(exist_ok=True)
                
                def write(self, text):
                    self.content.append(text)
                    return len(text)
                
                def __enter__(self):
                    return self
                
                def __exit__(self, *args):
                    from pathlib import Path
                    content = ''.join(self.content)
                    written_files[self.fname] = content
                    saved_files.append(self.fname)
                    try:
                        output_path = self.output_dir / self.fname
                        with original_open(str(output_path), self.mode, encoding='utf-8') as f:
                            f.write(content)
                    except Exception as e:
                        print(f"[Error writing file {self.fname}: {e}]")
            
            return FileWriter(filename, mode)
        else:
            return original_open(filename, mode, *args, **kwargs)
    
    safe_builtins = {
        'print': print,
        'len': len,
        'range': range,
        'sum': sum,
        'min': min,
        'max': max,
        'sorted': sorted,
        'enumerate': enumerate,
        'zip': zip,
        'dict': dict,
        'list': list,
        'tuple': tuple,
        'str': str,
        'int': int,
        'float': float,
        'bool': bool,
        'abs': abs,
        'round': round,
        'pow': pow,
        'isinstance': isinstance,
        'type': type,
        '__import__': __import__,
        'open': tracked_open,
    }
    
    import sqlite3 as sqlite3_orig
    import types
    
    def create_wrapped_sqlite3():
        wrapped = types.ModuleType('sqlite3_wrapped')
        
        # Copy all attributes from original sqlite3
        for attr in dir(sqlite3_orig):
            if not attr.startswith('_'):
                setattr(wrapped, attr, getattr(sqlite3_orig, attr))
        
        original_connect = sqlite3_orig.connect
        def wrapped_connect(database, *args, **kwargs):
            from pathlib import Path
            if database != ':memory:':
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / database
                saved_files.append(str(output_path))
                return original_connect(str(output_path), *args, **kwargs)
            return original_connect(database, *args, **kwargs)
        
        wrapped.connect = wrapped_connect
        return wrapped
    
    sqlite3_wrapper = create_wrapped_sqlite3()
    
    builtin_import = __import__
    def safe_import(name, *args, **kwargs):
        if name == 'sqlite3':
            return sqlite3_wrapper
        return builtin_import(name, *args, **kwargs)
    
    safe_builtins['__import__'] = safe_import
    
    sandbox = {
        'warnings': __import__('warnings'),
        '__builtins__': safe_builtins,
    }
    
    if available_data:
        sandbox.update(available_data)
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    try:
        exec(code, sandbox)
        output = sys.stdout.getvalue()
        
        if saved_files:
            output += f"\n\n[Generated Files]\n"
            for fname in saved_files:
                if fname.endswith('.sql'):
                    output += f"  📋 {fname} (SQL schema/queries)\n"
                elif fname.endswith('.txt'):
                    output += f"  📄 {fname} (documentation)\n"
                elif fname.endswith('.csv'):
                    output += f"  📊 {fname} (data)\n"
                else:
                    output += f"  📄 {fname}\n"
        
        return ExecutionResult(
            code=code,
            success=True,
            output=output,
            error=""
        )
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        return ExecutionResult(
            code=code,
            success=False,
            output="",
            error=error_msg
        )
    finally:
        sys.stdout = old_stdout


def _parse_code_blocks(text: str) -> List[str]:
    pattern = r'```(?:python|sql)?\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [block.strip() for block in matches if block.strip()]


def _prepare_data_for_execution(file_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    data_vars = {}
    
    if not file_paths:
        return data_vars
    
    for i, file_path in enumerate(file_paths):
        try:
            path = Path(file_path)
            file_type = path.suffix.lower()
            
            if file_type == '.csv':
                df = __import__('pandas').read_csv(file_path)
                var_name = f'df_{i}' if i > 0 else 'df'
                data_vars[var_name] = df
                
            elif file_type in ['.xlsx', '.xls']:
                df = __import__('pandas').read_excel(file_path)
                var_name = f'df_{i}' if i > 0 else 'df'
                data_vars[var_name] = df
                
            elif file_type == '.json':
                import json as json_module
                with open(file_path, 'r') as f:
                    data = json_module.load(f)
                df = __import__('pandas').DataFrame(data)
                var_name = f'df_{i}' if i > 0 else 'df'
                data_vars[var_name] = df
                
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {str(e)}")
    
    return data_vars


DATAENG_SYSTEM_PROMPT = """
ROLE: You are DataEngAgent - one member of a team of specialist agents:

- StatisticsAgent: hypothesis tests, confidence intervals, regression (as stats),
    sample size, experimental design.
- MLAgent: machine learning models, training, validation, feature engineering.
- DataEngAgent: data cleaning, schemas, SQL, ETL, data pipelines, storage.
- VizAgent: data visualization choices, storytelling, dashboards, charts.
- GeneralInfoAgent: general knowledge, web-like factual queries, travel, news, etc.

YOUR JOB: Answer data engineering questions and route non-data-eng work to better agents.

RESPONSE FORMAT - PLAIN TEXT with these fields clearly labeled:
DOMAIN: IN_DOMAIN or OUT_OF_DOMAIN
TASK_TYPE: describe the data engineering task (e.g., sql_query, schema_design, etl_pipeline, data_cleaning, performance_tuning, storage_architecture, etc)
DIFFICULTY: intro, intermediate, or advanced
RECOMMEND: comma-separated list of better agents or 'none'
ANSWER: Your explanation and results (can include code and output)

RULES:
1. Always include DOMAIN:, TASK_TYPE:, DIFFICULTY:, RECOMMEND:, and ANSWER: fields
2. For DOMAIN use only: IN_DOMAIN or OUT_OF_DOMAIN
3. For DIFFICULTY use only: intro, intermediate, or advanced
4. For RECOMMEND: if IN_DOMAIN, use 'none'; if OUT_OF_DOMAIN, suggest best agent(s)
5. ANSWER field can be multiple lines and include code blocks with ```python``` or ```sql``` markers
6. Include any code execution results in ANSWER field

DOMAIN CLASSIFICATION:
- IN_DOMAIN: data cleaning and preprocessing (missing values, outliers, type conversions),
    table and schema design (primary keys, foreign keys, normalization),
    SQL queries (SELECT, JOIN, GROUP BY, HAVING, subqueries),
    indexing and query performance tuning,
    ETL / ELT pipelines (ingest, transform, load),
    data warehouse / data lake / lakehouse architecture,
    batch vs streaming pipelines, scheduling/orchestration (Airflow-style),
    file formats and partitioning strategies (CSV, JSON, Parquet, etc)
- OUT_OF_DOMAIN: pure statistical inference/hypothesis tests (StatisticsAgent),
    ML models and training (MLAgent), dashboard/visualization design (VizAgent),
    general knowledge (GeneralInfoAgent)

WHEN RECOMMENDING AGENTS:
- If question is about hypothesis tests, confidence intervals → recommend StatisticsAgent
- If question is about ML models, training, features → recommend MLAgent
- If question is about dashboard/chart design → recommend VizAgent
- If question is general knowledge/travel/news → recommend GeneralInfoAgent
- For IN_DOMAIN data engineering questions, always use 'none'

WHEN USER PROVIDES DATA FILES:
1. Write Python code in ANSWER field with ```python code here``` blocks
2. Code will be executed automatically in a sandbox with: pandas (pd), numpy (np), sqlite3, csv, json
3. Include print() statements to show results
4. Use sqlite3 for demonstrating SQL queries:
   ```python
   import sqlite3
   conn = sqlite3.connect(':memory:')
   cursor = conn.cursor()
   cursor.execute('CREATE TABLE ...')
   cursor.execute('INSERT INTO ...')
   cursor.execute('SELECT ...')
   results = cursor.fetchall()
   for row in results:
       print(row)
   conn.close()
   ```
5. For data cleaning, use pandas operations (dropna, fillna, astype, etc)
6. For schema design, show CREATE TABLE statements with proper constraints
7. Example patterns:
   ```python
   import pandas as pd
   df = pd.read_csv('data.csv')
   print("Missing values:")
   print(df.isnull().sum())
   df_clean = df.dropna()
   print(f"Cleaned: {len(df_clean)} rows")
   ```

EXAMPLE RESPONSE:
DOMAIN: IN_DOMAIN
TASK_TYPE: data_cleaning
DIFFICULTY: intermediate
RECOMMEND: none
ANSWER:
I'll help clean the dataset by handling missing values and removing duplicates.

```python
import pandas as pd
df = pd.read_csv('data.csv')
print(f"Original shape: {df.shape}")
print(f"Missing values: {df.isnull().sum().sum()}")

df_clean = df.dropna()
df_clean = df_clean.drop_duplicates()
print(f"Cleaned shape: {df_clean.shape}")
print(f"Removed {len(df) - len(df_clean)} rows")
```

The data is now clean and ready for analysis.

You MUST always include an ANSWER: line followed by at least one sentence. Never leave ANSWER empty, even if the question is OUT_OF_DOMAIN
"""


def _parse_dataeng_agent_response(raw_text: str) -> DataEngAgentResponse:
    lines = raw_text.strip().split('\n')
    
    domain = "IN_DOMAIN"
    task_type = "other"
    difficulty = "intro"
    recommend = []
    answer_lines = []
    
    parsing_answer = False
    
    for line in lines:
        line_lower = line.lower()
        
        if line_lower.startswith('domain:'):
            domain_val = line[7:].strip().upper()
            if domain_val in ["IN_DOMAIN", "OUT_OF_DOMAIN"]:
                domain = domain_val
        
        elif line_lower.startswith('task_type:'):
            task_type = line[10:].strip()
        
        elif line_lower.startswith('difficulty:'):
            diff_val = line[11:].strip().lower()
            if diff_val in ["intro", "intermediate", "advanced"]:
                difficulty = diff_val
        
        elif line_lower.startswith('recommend:'):
            recommend_str = line[10:].strip()
            if recommend_str.lower() != 'none':
                recommend = [a.strip() for a in recommend_str.split(',')]
        
        elif line_lower.startswith('answer:'):
            answer_lines.append(line[7:].strip())
            parsing_answer = True
        
        elif parsing_answer:
            answer_lines.append(line)
    
    answer = '\n'.join(answer_lines)
    
    if domain not in ["IN_DOMAIN", "OUT_OF_DOMAIN"]:
        domain = "IN_DOMAIN"
    if difficulty not in ["intro", "intermediate", "advanced"]:
        difficulty = "intro"
    
    return DataEngAgentResponse(
        domain=domain,
        agent="DataEngAgent",
        recommend=recommend,
        task_type=task_type,
        difficulty=difficulty,
        answer=answer,
        files_analyzed=[],
        code_executions=[]
    )


def _call_langchain_structured(
    system_prompt: str,
    user_query: str,
    file_contents: Optional[str] = None
) -> Tuple[DataEngAgentResponse, float]:
    if file_contents:
        full_query = f"{user_query}\n\n[File Data Provided]\n{file_contents}"
    else:
        full_query = user_query
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=full_query),
    ]

    start = time.time()
    result = _base_llm.invoke(messages)
    end = time.time()

    latency = end - start

    if hasattr(result, "content"):
        raw_text = result.content
    else:
        raw_text = str(result)

    parsed = _parse_dataeng_agent_response(raw_text)
    return parsed, latency


# --- Public API ---


def run_data_eng_agent(query: str) -> str:
    answer, _ = run_data_eng_agent_timed(query)
    return answer


def run_data_eng_agent_timed(query: str) -> Tuple[str, float]:
    structured, latency = run_data_eng_agent_structured_timed(query)
    return structured.answer, latency


def run_data_eng_agent_structured_timed(
    query: str,
    file_paths: Optional[List[str]] = None,
) -> Tuple[DataEngAgentResponse, float]:
    file_contents = None
    files_analyzed = []
    
    if file_paths:
        file_content_parts = []
        for file_path in file_paths:
            try:
                content, preview, file_type = _read_file_content(file_path)
                
                file_size = os.path.getsize(file_path)
                files_analyzed.append({
                    'file_path': file_path,
                    'file_type': file_type,
                    'size_bytes': file_size,
                    'preview': preview,
                })
                
                file_content_parts.append(f"FILE: {file_path}\nTYPE: {file_type}\nCONTENT:\n{content}")
                
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {str(e)}")
        
        if file_content_parts:
            file_contents = "\n\n".join(file_content_parts)
    
    response, latency = _call_langchain_structured(
        DATAENG_SYSTEM_PROMPT,
        query,
        file_contents=file_contents
    )
    
    response.files_analyzed = [FileMetadata(**f) for f in files_analyzed]
    
    if response.code_executions is None:
        response.code_executions = []
    
    code_blocks = _parse_code_blocks(response.answer)
    if code_blocks:
        data_vars = _prepare_data_for_execution(file_paths)
        
        for code_block in code_blocks:
            execution = _execute_code(code_block, available_data=data_vars)
            response.code_executions.append(execution)
            
            if execution.success and execution.output:
                response.answer += f"\n\nExecution Output:\n{execution.output}"
    
    return response, latency


if __name__ == "__main__":
    print("Complex DataEngAgent (LangChain + structured output).")
    print("Syntax:")
    print("  - Your query")
    print("  - FILE: path/to/file.csv Your query (reads file and analyzes)")
    print("  - FILE: file1.csv FILE: file2.csv Your query (multiple files)")
    print("  - exit/quit to leave\n")

    import sys
    import re
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from agent_response_parser import parse_json_response, format_full_output

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        # Parse FILE: prefixes
        file_pattern = r'FILE:\s*([\S]+)'
        file_matches = re.findall(file_pattern, user_input)
        file_paths = file_matches if file_matches else None
        
        # Remove FILE: prefixes to get the query
        query = re.sub(file_pattern, '', user_input).strip()
        if not query:
            print("[Error] No query provided. Use: FILE: path/to/file.csv Your query\n")
            continue

        try:
            resp, latency = run_data_eng_agent_structured_timed(query, file_paths=file_paths)
            # Convert structured response to dict for parser
            resp_dict = {
                "domain": resp.domain,
                "agent": resp.agent,
                "recommend": resp.recommend,
                "task_type": resp.task_type,
                "difficulty": resp.difficulty,
                "answer": resp.answer,
            }
            parsed = parse_json_response(resp_dict, agent_name="DataEng-complex")
            output = format_full_output(parsed, latency)
            print(f"\n{output}\n")
        except Exception as e:
            print(f"\n[Error calling LangChain/Ollama] {e}\n")
