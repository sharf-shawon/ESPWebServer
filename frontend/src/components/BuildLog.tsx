import { useRef, useEffect } from "react";
import type { BuildMessage } from "@/hooks/useWebSocket";
import { Terminal } from "lucide-react";
import { cn } from "@/lib/utils";

interface BuildLogProps {
  messages: BuildMessage[];
}

export function BuildLog({ messages }: BuildLogProps) {
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium flex items-center gap-2">
        <Terminal className="h-4 w-4" />
        Build Log
      </label>
      <div
        ref={logRef}
        className="bg-black text-green-400 font-mono text-xs p-3 rounded-lg h-48 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <span className="text-gray-500">Waiting for build output...</span>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "leading-relaxed",
                msg.type === "error" && "text-red-400",
                msg.type === "success" && "text-green-300"
              )}
            >
              {msg.message}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
