import { useEffect, useRef, useState, useCallback } from "react";

export type BuildStatus =
  | "idle"
  | "connecting"
  | "compiling"
  | "success"
  | "error";

export interface BuildMessage {
  type: "progress" | "log" | "success" | "error";
  message: string;
  progress?: number;
  downloadUrl?: string;
  firmwareSize?: number;
}

export function useWebSocket(jobId: string | null) {
  const [status, setStatus] = useState<BuildStatus>("idle");
  const [messages, setMessages] = useState<BuildMessage[]>([]);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const reset = useCallback(() => {
    setStatus("idle");
    setMessages([]);
    setProgress(0);
    setDownloadUrl(null);
  }, []);

  useEffect(() => {
    if (!jobId) return;

    setStatus("connecting");
    const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/build/${jobId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    // Track current status via ref to avoid stale closure in onclose
    const currentStatusRef = { value: "connecting" as BuildStatus };

    ws.onopen = () => {
      currentStatusRef.value = "compiling";
      setStatus("compiling");
    };

    ws.onmessage = (event) => {
      try {
        const msg: BuildMessage = JSON.parse(event.data);
        setMessages((prev) => [...prev, msg]);
        if (msg.progress !== undefined) {
          setProgress(msg.progress);
        }
        if (msg.type === "success") {
          currentStatusRef.value = "success";
          setStatus("success");
          if (msg.downloadUrl) setDownloadUrl(msg.downloadUrl);
        } else if (msg.type === "error") {
          currentStatusRef.value = "error";
          setStatus("error");
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onerror = () => {
      currentStatusRef.value = "error";
      setStatus("error");
      setMessages((prev) => [
        ...prev,
        { type: "error", message: "WebSocket connection error" },
      ]);
    };

    ws.onclose = () => {
      if (currentStatusRef.value === "compiling") {
        setStatus("error");
      }
    };

    return () => {
      ws.close();
    };
  }, [jobId]);

  return { status, messages, progress, downloadUrl, reset };
}
