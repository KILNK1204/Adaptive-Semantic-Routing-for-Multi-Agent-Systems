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
    file_type: str = Field(..., description="Type of file (csv, json, txt, excel, etc.).")
    size_bytes: int = Field(..., description="File size in bytes.")
    preview: str = Field(default="", description="First few lines or summary of file content.")


class StatsAgentResponse(BaseModel):

    domain: Literal["IN_DOMAIN", "OUT_OF_DOMAIN"] = Field(
        ...,
        description=(
            "Whether the query is primarily about statistical inference or "
            "model evaluation (IN_DOMAIN) or something else (OUT_OF_DOMAIN)."
        ),
    )
    agent: Literal["StatisticsAgent"] = Field(
        ...,
        description="Name of this agent (always 'StatisticsAgent').",
    )
    recommend: List[str] = Field(
        default_factory=list,
        description=(
            "Names of OTHER agents that should handle follow-up work "
            "(e.g. ['MLAgent', 'DataEngAgent']) or an empty list if none."
        ),
    )
    task_type: str = Field(
        ...,
        description=(
            "Short label describing the main statistical task, e.g. "
            "'descriptive', 'one_sample_t_test', 'two_sample_t_test', "
            "'regression', 'time_series', 'experimental_design', 'bayesian', "
            "or 'other'."
        ),
    )
    difficulty: Literal["intro", "intermediate", "advanced"] = Field(
        ...,
        description=(
            "Rough difficulty for a student who has taken an intro stats course."
        ),
    )
    answer: str = Field(
        ...,
        description="Final user-facing explanation and any calculations.",
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
            is_binary = 'b' in mode
            class FileWriter:
                def __init__(self, fname, f_mode, binary=False):
                    self.fname = fname
                    self.mode = f_mode
                    self.binary = binary
                    self.content = [] if not binary else bytearray()
                
                def write(self, data):
                    if self.binary:
                        if isinstance(data, bytes):
                            self.content.extend(data)
                        else:
                            self.content.extend(str(data).encode())
                    else:
                        self.content.append(data)
                    return len(data) if isinstance(data, (str, bytes)) else len(str(data))
                
                def __enter__(self):
                    return self
                
                def __exit__(self, *args):
                    if self.binary:
                        content = bytes(self.content)
                    else:
                        content = ''.join(self.content)
                    
                    written_files[self.fname] = content
                    saved_files.append(self.fname)
                    # Also write to actual filesystem
                    try:
                        with original_open(self.fname, self.mode) as f:
                            f.write(content)
                    except Exception as e:
                        print(f"[Error writing file {self.fname}: {e}]")
            
            return FileWriter(filename, mode, is_binary)
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
        'open': tracked_open,  # Use our tracked open
    }
    
    import matplotlib.pyplot as plt
    original_show = plt.show
    plot_counter = [0]
    
    def save_plot_instead():
        try:
            from pathlib import Path
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            
            plot_counter[0] += 1
            filename = output_dir / f"plot_{plot_counter[0]}.png"
            plt.savefig(str(filename), dpi=150, bbox_inches='tight')
            saved_files.append(str(filename))
            print(f"[Plot saved to: {filename}]")
            plt.close()  # Close only after successful save
        except Exception as e:
            print(f"[Error saving plot: {e}]")
    
    plt.show = save_plot_instead
    
    sandbox = {
        'pd': __import__('pandas'),
        'np': __import__('numpy'),
        'plt': plt,
        'stats': __import__('scipy').stats,
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
                if fname.endswith('.png'):
                    output += f"  📊 {fname} (visualization)\n"
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
        plt.show = original_show


def _parse_code_blocks(text: str) -> List[str]:
    pattern = r'```(?:python)?\s*\n(.*?)```'
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



STATS_SYSTEM_PROMPT = """
ROLE: You are StatisticsAgent - one member of a team of specialist agents:

- StatisticsAgent: hypothesis tests, confidence intervals, regression, distributions,
    sample size, experimental design.
- MLAgent: machine learning models, training, validation, feature engineering.
- DataEngAgent: data cleaning, schemas, SQL, ETL, data pipelines.
- VizAgent: data visualization choices, storytelling, dashboards, charts.
- GeneralInfoAgent: general knowledge, web-like factual queries, travel, news, etc.

YOUR JOB: Answer statistical inference questions and route non-statistical work to better agents.

RESPONSE FORMAT - PLAIN TEXT with these fields clearly labeled:
DOMAIN: IN_DOMAIN or OUT_OF_DOMAIN
TASK_TYPE: describe the task (e.g., correlation, regression, visualization, etc)
DIFFICULTY: intro, intermediate, or advanced
RECOMMEND: comma-separated list of better agents or 'none'
ANSWER: Your explanation and results (can include code and output)

RULES:
1. Always include DOMAIN:, TASK_TYPE:, DIFFICULTY:, RECOMMEND:, and ANSWER: fields
2. For DOMAIN use only: IN_DOMAIN or OUT_OF_DOMAIN
3. For DIFFICULTY use only: intro, intermediate, or advanced
4. For RECOMMEND: if IN_DOMAIN, use 'none'; if OUT_OF_DOMAIN, suggest best agent(s)
5. ANSWER field can be multiple lines and include code blocks with ```python``` markers
6. Include any code execution results in ANSWER field

DOMAIN CLASSIFICATION:
- IN_DOMAIN: t-tests, ANOVA, correlation, regression, confidence intervals, distributions, 
    histograms, box plots, scatter plots with statistical analysis, experimental design
- OUT_OF_DOMAIN: dashboard design (VizAgent), ML models (MLAgent), general knowledge 
    (GeneralInfoAgent), data engineering (DataEngAgent)

WHEN RECOMMENDING AGENTS:
- If question is about ML/model training → recommend MLAgent
- If question is about data cleaning/SQL/schemas → recommend DataEngAgent
- If question is about visualization/dashboards → recommend VizAgent
- If question is general knowledge/travel/news → recommend GeneralInfoAgent
- For IN_DOMAIN statistical questions, always use 'none'

WHEN USER PROVIDES DATA FILES:
1. Write Python code in ANSWER field with ```python code here``` blocks
2. Code will be executed automatically in a sandbox with: pandas (pd), numpy (np), scipy.stats (stats), matplotlib.pyplot (plt)
3. Use plt.show() at the end of plotting code - DO NOT use plt.savefig() explicitly
4. ALL plt.show() calls are automatically intercepted and converted to PNG file saves
5. Do NOT include explicit plt.savefig() calls - they will save blank figures
6. Include print() statements to show numerical results
7. Example correct pattern:
   ```python
   import pandas as pd
   import matplotlib.pyplot as plt
   df = pd.read_csv('data.csv')
   plt.scatter(df['col1'], df['col2'])
   plt.show()  # ← This automatically saves to plot_N.png
   ```

EXAMPLE RESPONSE:
DOMAIN: IN_DOMAIN
TASK_TYPE: correlation
DIFFICULTY: intermediate
RECOMMEND: none
ANSWER: 
I'll calculate the correlation between study hours and GPA.

```python
import pandas as pd
from scipy.stats import pearsonr
df = pd.read_csv('data.csv')
r, p = pearsonr(df['study_hours'], df['gpa'])
print(f'Pearson r={r:.2f}, p={p:.3f}')
```

The results show a strong positive correlation.

You MUST always include an ANSWER: line followed by at least one sentence. Never leave ANSWER empty, even if the question is OUT_OF_DOMAIN
"""


def _parse_stats_agent_response(raw_text: str) -> StatsAgentResponse:
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
    
    return StatsAgentResponse(
        domain=domain,
        agent="StatisticsAgent",
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
) -> Tuple[StatsAgentResponse, float]:
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

    parsed = _parse_stats_agent_response(raw_text)
    return parsed, latency


# --- Public API ---


def run_statistics_agent(query: str) -> str:
    answer, _ = run_statistics_agent_timed(query)
    return answer


def run_statistics_agent_timed(query: str) -> Tuple[str, float]:
    structured, latency = run_statistics_agent_structured_timed(query)
    return structured.answer, latency


def run_statistics_agent_structured_timed(
    query: str,
    file_paths: Optional[List[str]] = None,
) -> Tuple[StatsAgentResponse, float]:
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
        STATS_SYSTEM_PROMPT,
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
    print("Complex StatisticsAgent (LangChain + JSON-structured output).")
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
            resp, latency = run_statistics_agent_structured_timed(query, file_paths=file_paths)
            # Convert structured response to dict for parser
            resp_dict = {
                "domain": resp.domain,
                "agent": resp.agent,
                "recommend": resp.recommend,
                "task_type": resp.task_type,
                "difficulty": resp.difficulty,
                "answer": resp.answer,
            }
            parsed = parse_json_response(resp_dict, agent_name="complex")
            output = format_full_output(parsed, latency)
            print(f"\n{output}\n")
        except Exception as e:
            print(f"\n[Error calling LangChain/Ollama] {e}\n")
