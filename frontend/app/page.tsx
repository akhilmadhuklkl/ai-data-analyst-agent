"use client";

import { useState } from "react";
import { ArrowUpRight, BarChart3, Database, FileSpreadsheet, Sparkles, Upload, WandSparkles } from "lucide-react";

type Result = { explanation?: string; analysis?: { columns: string[]; rows: Record<string, unknown>[] }; sql?: string; columns?: string[]; rows?: Record<string, unknown>[] };
type ColumnInfo = { name: string; type: string };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8001";
const EXAMPLES = {
  csv: ["Show revenue by region", "Which product has the highest revenue?", "Summarize the dataset"],
  sqlite: ["Show all sales records", "Compare revenue by region", "Find the top-performing product"],
};

function VisualSummary({ columns, rows }: { columns: string[]; rows: Record<string, unknown>[] }) {
  const numericColumn = columns.find((column) => rows.some((row) => typeof row[column] === "number"));
  if (!numericColumn || rows.length === 0) return null;
  const values = rows.map((row) => Number(row[numericColumn]) || 0);
  const max = Math.max(...values, 1);
  const labelColumn = columns.find((column) => column !== numericColumn) ?? numericColumn;

  return <div className="visual-summary">
    <div className="visual-heading"><span>VISUAL SUMMARY</span><small>{numericColumn.toUpperCase()}</small></div>
    <div className="bars">{rows.slice(0, 8).map((row, index) => <div className="bar-row" key={`${String(row[labelColumn])}-${index}`}>
      <span className="bar-label">{String(row[labelColumn] ?? `Row ${index + 1}`)}</span>
      <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.max((values[index] / max) * 100, 3)}%` }} /></div>
      <span className="bar-value">{String(row[numericColumn] ?? "—")}</span>
    </div>)}</div>
  </div>;
}

export default function Home() {
  const [source, setSource] = useState<"csv" | "sqlite">("csv");
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("Show revenue by region");
  const [useAI, setUseAI] = useState(true);
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [schema, setSchema] = useState<Record<string, ColumnInfo[]>>({});
  const [inspectingTables, setInspectingTables] = useState(false);

  async function loadSample() {
    setError(""); setStage("Fetching the portfolio dataset...");
    try {
      const response = await fetch(`${API_URL}/sample-data`);
      if (!response.ok) throw new Error("Could not load sample data");
      const blob = await response.blob();
      setFile(new File([blob], "sample_sales.csv", { type: "text/csv" }));
      setSource("csv"); setTables([]); setSelectedTable(""); setSchema({});
      setQuestion("Show revenue by region"); setStage("Sample data ready to analyze.");
    } catch (err) { setStage(""); setError("Sample data could not be loaded. Check that the API is running on port 8001."); }
  }

  async function loadSampleDatabase() {
    setError(""); setStage("Fetching the sample database...");
    try {
      const response = await fetch(`${API_URL}/sample-database`);
      if (!response.ok) throw new Error("Could not load sample database");
      const blob = await response.blob();
      setSource("sqlite");
      await handleFile(new File([blob], "sample_sales.sqlite", { type: "application/x-sqlite3" }), "sqlite");
    } catch (err) { setStage(""); setError("Sample database could not be loaded. Check that the API is running on port 8001."); }
  }

  async function handleFile(fileToInspect: File | null, sourceToInspect = source) {
    setFile(fileToInspect); setResult(null); setTables([]); setSelectedTable(""); setSchema({}); setError("");
    if (!fileToInspect || sourceToInspect !== "sqlite") return;
    setInspectingTables(true); setStage("Inspecting SQLite tables...");
    try {
      const form = new FormData(); form.append("file", fileToInspect);
      const response = await fetch(`${API_URL}/inspect/sqlite`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "SQLite inspection failed");
      setTables(payload.tables ?? []); setSchema(payload.schema ?? {}); setStage(`${payload.tables?.length ?? 0} table(s) found. Ready to analyze.`);
    } catch (err) { setStage(""); setError(`This SQLite file could not be inspected: ${err instanceof Error ? err.message : "check the file"}`); }
    finally { setInspectingTables(false); }
  }

  async function analyze() {
    if (!file || !question.trim()) return;
    setLoading(true); setError(""); setStage("Reading your dataset...");
    const form = new FormData(); form.append("file", file); form.append("question", question);
    if (source === "csv") form.append("use_local_ai", String(useAI));
    if (source === "sqlite" && selectedTable) form.append("table_name", selectedTable);
    try {
      setStage(source === "sqlite" ? "Inspecting the database schema..." : useAI ? "Asking the local analyst for a plan..." : "Planning the analysis...");
      const response = await fetch(`${API_URL}/analyze/${source}`, { method: "POST", body: form });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Analysis failed");
      setStage("Checking results and preparing the visual summary...");
      setResult(payload);
    } catch (err) { setError(err instanceof Error && err.message ? `Analysis could not be completed: ${err.message}` : "Analysis could not be completed. Check the file and API connection."); }
    finally { setLoading(false); setStage(""); }
  }

  function downloadFile(content: string, filename: string, type: string) {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(new Blob([content], { type }));
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  function exportTable() {
    const csv = [columns.join(","), ...rows.map((row) => columns.map((column) => JSON.stringify(row[column] ?? "")).join(","))].join("\n");
    downloadFile(csv, "nexus-analysis-results.csv", "text/csv");
  }

  function exportReport() {
    downloadFile(JSON.stringify({ question, source, explanation: result?.explanation, sql: result?.sql, metrics: { rows: rows.length, fields: columns.length, measures: numericColumns.length }, columns, rows }, null, 2), "nexus-analysis-report.json", "application/json");
  }

  const columns = result?.analysis?.columns ?? result?.columns ?? [];
  const rows = result?.analysis?.rows ?? result?.rows ?? [];
  const numericColumns = columns.filter((column) => rows.some((row) => typeof row[column] === "number"));

  return <main className="shell">
    <nav className="nav"><div className="brand"><span className="brand-mark"><Sparkles size={17} /></span> NEXUS <em>ANALYST</em></div><span className="status"><i /> LOCAL WORKSPACE</span></nav>
    <section className="hero"><div className="eyebrow">INTELLIGENCE FOR YOUR DATA <ArrowUpRight size={14} /></div><h1>Ask better questions.<br /><span>Find clearer answers.</span></h1><p>Upload a dataset, connect your thinking, and let your local analyst uncover the signal.</p></section>
    <section className="workspace">
      <aside className="control-panel">
        <div className="panel-label">01 / SOURCE</div>
        <div className="source-tabs"><button className={source === "csv" ? "active" : ""} onClick={() => { setSource("csv"); setTables([]); setSelectedTable(""); }}><FileSpreadsheet size={16} /> CSV FILE</button><button className={source === "sqlite" ? "active" : ""} onClick={() => setSource("sqlite")}><Database size={16} /> SQLITE</button></div>
        <label className="dropzone"><Upload size={21} /><strong>{file ? file.name : "Drop your data here"}</strong><small>{file ? `${(file.size / 1024).toFixed(1)} KB ready` : "CSV, DB, SQLITE · MAX 50 MB"}</small><input type="file" accept={source === "csv" ? ".csv" : ".db,.sqlite,.sqlite3"} onChange={(e) => handleFile(e.target.files?.[0] ?? null)} /></label><button className="sample-button" onClick={source === "sqlite" ? loadSampleDatabase : loadSample}><WandSparkles size={14} /> LOAD SAMPLE {source === "sqlite" ? "DATABASE" : "DATA"}</button>
        {source === "sqlite" && inspectingTables && <div className="inspection-card"><span className="inspection-spinner" /><div><strong>Reading database structure</strong><small>Finding tables and columns...</small></div></div>}
        {source === "sqlite" && !inspectingTables && tables.length === 0 && file && <div className="inspection-empty">No tables detected in this database.</div>}
        {source === "sqlite" && tables.length > 0 && <div className="table-list"><span>ANALYZE TABLE</span><select value={selectedTable} onChange={(e) => setSelectedTable(e.target.value)}><option value="">ALL TABLES</option>{tables.map((table) => <option key={table} value={table}>{table}</option>)}</select>{selectedTable && <div className="schema-card"><div className="schema-title">{selectedTable} · {schema[selectedTable]?.length ?? 0} COLUMNS</div>{schema[selectedTable]?.map((column) => <div className="schema-row" key={column.name}><code>{column.name}</code><span>{column.type}</span></div>)}</div>}</div>}
        <div className="panel-label question-label">02 / ASK</div><textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="What would you like to understand?" />
        <div className="example-questions"><span>TRY AN EXAMPLE</span>{EXAMPLES[source].map((example) => <button key={example} onClick={() => setQuestion(example)}>{example}</button>)}</div>
        {source === "csv" && <label className="toggle"><input type="checkbox" checked={useAI} onChange={(e) => setUseAI(e.target.checked)} /><span /> USE LOCAL AI INTERPRETER</label>}
        <button className="analyze" disabled={!file || loading} onClick={analyze}>{loading ? <><span className="button-loader" /> ANALYZING...</> : "ANALYZE DATA"}<ArrowUpRight size={17} /></button>
        {stage && <div className={`stage ${loading ? "active" : "ready"}`}><span />{stage}</div>}
        {error && <div className="error">{error}</div>}
      </aside>
      <section className="results"><div className="panel-label">03 / INSIGHT</div>{!result && <div className="empty"><div className="empty-icon"><BarChart3 size={28} /></div><h2>Your analysis will appear here.</h2><p>Start with the sample question, or ask something specific about your own data.</p></div>}{result && <><div className="result-head"><div><h2>Analysis complete</h2><p>{result.explanation ?? "Your database query returned these results."}</p></div><span className="pill">{rows.length} ROWS</span></div><div className="metric-grid"><div><strong>{rows.length}</strong><span>RESULT ROWS</span></div><div><strong>{columns.length}</strong><span>DATA FIELDS</span></div><div><strong>{numericColumns.length}</strong><span>MEASURES</span></div></div><VisualSummary columns={columns} rows={rows} />{result.sql && <details><summary>VIEW GENERATED SQL</summary><pre>{result.sql}</pre></details>}<div className="table-wrap"><table><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{String(row[column] ?? "—")}</td>)}</tr>)}</tbody></table></div><div className="export-actions"><span>EXPORT RESULTS</span><button onClick={exportTable}>DOWNLOAD CSV</button><button onClick={exportReport}>DOWNLOAD REPORT</button></div></>}</section>
    </section>
    <footer>BUILT FOR CURIOUS MINDS <span>·</span> LOCAL-FIRST ANALYTICS</footer>
  </main>;
}
