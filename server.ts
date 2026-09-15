import express from "express";
import path from "path";
import { spawn } from "child_process";
import { createServer as createViteServer } from "vite";

const app = express();
const PORT = 3000;

app.use(express.json());

function executePythonBridge(requestPayload: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", ["app/api_bridge.py"], {
      cwd: process.cwd(),
      env: { ...process.env, PYTHONPATH: "." }
    });

    let stdoutData = "";
    let stderrData = "";

    proc.stdout.on("data", (data) => {
      stdoutData += data.toString();
    });

    proc.stderr.on("data", (data) => {
      stderrData += data.toString();
    });

    proc.on("close", (code) => {
      if (code !== 0 && !stdoutData.trim()) {
        return reject(new Error(`Python bridge failed: ${stderrData}`));
      }
      try {
        const parsed = JSON.parse(stdoutData.trim() || "{}");
        resolve(parsed);
      } catch (err) {
        reject(new Error(`Failed to parse Python response: ${stdoutData} (Error: ${stderrData})`));
      }
    });

    proc.stdin.write(JSON.stringify(requestPayload));
    proc.stdin.end();
  });
}

// 1. Health API
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", app: "MY AI", privacy: "LOCAL_STRICT" });
});

// 2. Chat API
app.post("/api/chat", async (req, res) => {
  try {
    const text = req.body.text || "";
    const result = await executePythonBridge({ action: "chat", text });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 3. System & Dashboard API
app.get("/api/dashboard", async (req, res) => {
  try {
    const result = await executePythonBridge({ action: "get_dashboard" });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 4. Tasks API
app.post("/api/tasks/create", async (req, res) => {
  try {
    const result = await executePythonBridge({
      action: "create_task",
      title: req.body.title,
      priority: req.body.priority || "MEDIUM"
    });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/tasks/complete", async (req, res) => {
  try {
    const result = await executePythonBridge({
      action: "complete_task",
      task_id: req.body.task_id
    });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 5. Benchmarks API
app.post("/api/benchmarks", async (req, res) => {
  try {
    const result = await executePythonBridge({ action: "run_benchmarks" });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// 6. Autonomous Heartbeat API
app.post("/api/heartbeat", async (req, res) => {
  try {
    const result = await executePythonBridge({ action: "tick_companion" });
    res.json(result);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

async function startServer() {
  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`MY AI Server running at http://0.0.0.0:${PORT}`);
  });
}

startServer();
