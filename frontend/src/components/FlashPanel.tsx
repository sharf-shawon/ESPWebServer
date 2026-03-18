import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import type { Board } from "@/lib/boards";
import type { FlashProgress } from "@/hooks/useFlasher";
import { Zap, AlertCircle, CheckCircle2, Download, Usb } from "lucide-react";

interface FlashPanelProps {
  board: Board | null;
  firmwareUrl: string | null;
  firmwareSize?: number;
  flashProgress: FlashProgress;
  onFlash: () => void;
  onDownload: () => void;
  isWebSerialSupported: boolean;
  buildStatus: string;
}

export function FlashPanel({
  board,
  firmwareUrl,
  firmwareSize,
  flashProgress,
  onFlash,
  onDownload,
  isWebSerialSupported,
  buildStatus,
}: FlashPanelProps) {
  const isFlashing = ["connecting", "erasing", "writing", "verifying"].includes(
    flashProgress.status
  );
  const canFlash = !!firmwareUrl && !!board && buildStatus === "success" && !isFlashing;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium flex items-center gap-2">
          <Zap className="h-4 w-4" />
          Flash to Device
        </h3>
        {firmwareSize && (
          <Badge variant="secondary">{(firmwareSize / 1024).toFixed(1)} KB</Badge>
        )}
      </div>

      {!isWebSerialSupported && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Web Serial Not Supported</AlertTitle>
          <AlertDescription>
            Web Serial API requires Chrome or Edge 89+. Use HTTPS or localhost.
          </AlertDescription>
        </Alert>
      )}

      {flashProgress.status === "error" && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Flash Error</AlertTitle>
          <AlertDescription>{flashProgress.message}</AlertDescription>
        </Alert>
      )}

      {flashProgress.status === "success" && (
        <Alert className="border-green-500 text-green-700 bg-green-50">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertTitle>Flash Successful!</AlertTitle>
          <AlertDescription>
            Board is restarting. Connect to WiFi AP &quot;esp-web-server&quot; to configure.
          </AlertDescription>
        </Alert>
      )}

      {isFlashing && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{flashProgress.message}</span>
            <span>{flashProgress.progress}%</span>
          </div>
          <Progress value={flashProgress.progress} />
        </div>
      )}

      <div className="flex gap-2">
        <Button
          onClick={onFlash}
          disabled={!canFlash || !isWebSerialSupported}
          className="flex-1"
        >
          <Usb className="h-4 w-4 mr-2" />
          {isFlashing ? "Flashing..." : "Flash via USB"}
        </Button>
        <Button
          variant="outline"
          onClick={onDownload}
          disabled={!firmwareUrl}
        >
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
      </div>

      <p className="text-xs text-muted-foreground">
        Hold BOOT button during &quot;Connecting&quot; phase if auto-reset fails.
      </p>
    </div>
  );
}
