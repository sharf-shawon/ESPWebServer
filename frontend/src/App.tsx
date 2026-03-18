import { useState, useCallback, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { BoardSelector } from "@/components/BoardSelector";
import { CodeEditor } from "@/components/CodeEditor";
import { LivePreview } from "@/components/LivePreview";
import { FlashPanel } from "@/components/FlashPanel";
import { BuildLog } from "@/components/BuildLog";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useFlasher } from "@/hooks/useFlasher";
import type { Board } from "@/lib/boards";
import { Cpu, Zap, AlertCircle } from "lucide-react";

const DEFAULT_HTML = `<h1>Hello ESP!</h1>
<p>My ESP8266/ESP32 web server is running!</p>
<button onclick="toggleLED()">Toggle LED</button>
<script>
function toggleLED() {
  fetch('/led/toggle').then(r => r.text()).then(alert);
}
</script>`;

const DEFAULT_CSS = `body {
  font-family: Arial, sans-serif;
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  background: #f0f0f0;
}
h1 { color: #333; }
button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}
button:hover { background: #0056b3; }`;

export default function App() {
  const [board, setBoard] = useState<Board | null>(null);
  const [html, setHtml] = useState(DEFAULT_HTML);
  const [css, setCss] = useState(DEFAULT_CSS);
  const [js, setJs] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [buildError, setBuildError] = useState<string | null>(null);
  const [isBuilding, setIsBuilding] = useState(false);

  const { status: buildStatus, messages, progress: buildProgress, downloadUrl, reset: resetBuild } = useWebSocket(jobId);
  const { flashProgress, flash, reset: resetFlash, isWebSerialSupported } = useFlasher();

  const handleCodeChange = useCallback(
    (field: "html" | "css" | "js", value: string) => {
      if (field === "html") setHtml(value);
      else if (field === "css") setCss(value);
      else setJs(value);
    },
    []
  );

  const handleBuild = async () => {
    if (!board) {
      setBuildError("Please select a board first.");
      return;
    }

    const totalSize = new Blob([html, css, js]).size;
    if (totalSize > 512 * 1024) {
      setBuildError("HTML bundle exceeds 512KB limit.");
      return;
    }

    setBuildError(null);
    setIsBuilding(true);
    resetBuild();
    resetFlash();

    try {
      const response = await fetch("/api/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          board_id: board.id,
          html,
          css,
          js,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Build request failed");
      }

      const data = await response.json();
      setJobId(data.job_id);
    } catch (err) {
      setBuildError(err instanceof Error ? err.message : "Build failed");
      setIsBuilding(false);
    }
  };

  // Track build completion via effect to avoid state updates during render
  useEffect(() => {
    if (isBuilding && (buildStatus === "success" || buildStatus === "error")) {
      setIsBuilding(false);
    }
  }, [isBuilding, buildStatus]);

  const handleFlash = async () => {
    if (!downloadUrl || !board) return;
    try {
      await flash(downloadUrl, board);
    } catch {
      // error handled in hook
    }
  };

  const handleDownload = () => {
    if (!downloadUrl) return;
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = `firmware-${board?.id ?? "esp"}.bin`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary rounded-lg p-2">
              <Cpu className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">ESP Web Deployer</h1>
              <p className="text-xs text-muted-foreground">Flash websites to ESP8266/ESP32 boards</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Zap className="h-3 w-3" />
            <span>Powered by esptool-js + Web Serial</span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 space-y-6">
        {buildError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{buildError}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Editor + Board */}
          <div className="lg:col-span-2 space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Board Configuration</CardTitle>
                <CardDescription>Select your ESP board and configure flash settings</CardDescription>
              </CardHeader>
              <CardContent>
                <BoardSelector selectedBoard={board} onSelect={setBoard} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Web Content</CardTitle>
                <CardDescription>Paste or upload your HTML/CSS/JS for the ESP web server</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeEditor html={html} css={css} js={js} onChange={handleCodeChange} />
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <LivePreview html={html} css={css} js={js} />
              </CardContent>
            </Card>
          </div>

          {/* Right: Build + Flash */}
          <div className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Build Firmware</CardTitle>
                <CardDescription>Compile for your selected board</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {(isBuilding || buildStatus === "compiling" || buildStatus === "connecting") && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Building firmware...</span>
                      <span>{buildProgress}%</span>
                    </div>
                    <Progress value={buildProgress} />
                  </div>
                )}

                <Button
                  onClick={handleBuild}
                  disabled={isBuilding || buildStatus === "compiling"}
                  className="w-full"
                  size="lg"
                >
                  {isBuilding ? "Building..." : "Build Firmware"}
                </Button>

                <BuildLog messages={messages} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Flash to Board</CardTitle>
                <CardDescription>Connect ESP via USB and flash</CardDescription>
              </CardHeader>
              <CardContent>
                <FlashPanel
                  board={board}
                  firmwareUrl={downloadUrl}
                  flashProgress={flashProgress}
                  onFlash={handleFlash}
                  onDownload={handleDownload}
                  isWebSerialSupported={isWebSerialSupported}
                  buildStatus={buildStatus}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">After Flashing</CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground space-y-2">
                <p>1. Board creates WiFi AP: <strong>esp-web-server</strong></p>
                <p>2. Connect and open <strong>192.168.4.1</strong></p>
                <p>3. Enter your WiFi credentials</p>
                <p>4. Board connects and shows its IP</p>
                <p>5. Open the IP to see your website!</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
