import { useEffect, useRef } from "react";
import DOMPurify from "dompurify";
import { Monitor } from "lucide-react";

interface LivePreviewProps {
  html: string;
  css: string;
  js: string;
}

export function LivePreview({ html, css, js }: LivePreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    // This is a developer tool where users intentionally write their own HTML/JS.
    // Script tags are allowed so the live preview matches what the ESP board will serve.
    // The iframe sandbox attribute (allow-scripts) limits the execution context.
    const sanitizedHtml = DOMPurify.sanitize(html, {
      ADD_TAGS: ["style", "script"],
      ADD_ATTR: ["onload", "onclick"],
      FORCE_BODY: false,
    });

    const content = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>${css}</style>
</head>
<body>
${sanitizedHtml}
<script>${js}<\/script>
</body>
</html>`;

    const doc = iframe.contentDocument || iframe.contentWindow?.document;
    if (doc) {
      doc.open();
      doc.write(content);
      doc.close();
    }
  }, [html, css, js]);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium flex items-center gap-2">
        <Monitor className="h-4 w-4" />
        Live Preview
      </label>
      <div className="border rounded-lg overflow-hidden bg-white" style={{ height: "400px" }}>
        <iframe
          ref={iframeRef}
          title="Live Preview"
          className="w-full h-full"
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
    </div>
  );
}
