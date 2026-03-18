import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { FileCode, UploadCloud } from "lucide-react";
import { useRef } from "react";

interface CodeEditorProps {
  html: string;
  css: string;
  js: string;
  onChange: (field: "html" | "css" | "js", value: string) => void;
}

export function CodeEditor({ html, css, js, onChange }: CodeEditorProps) {
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const content = ev.target?.result as string;
      if (file.name.endsWith(".html")) onChange("html", content);
      else if (file.name.endsWith(".css")) onChange("css", content);
      else if (file.name.endsWith(".js")) onChange("js", content);
    };
    reader.readAsText(file);
    e.target.value = "";
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium flex items-center gap-2">
          <FileCode className="h-4 w-4" />
          Web Content
        </label>
        <Button
          variant="outline"
          size="sm"
          onClick={() => fileRef.current?.click()}
        >
          <UploadCloud className="h-4 w-4 mr-1" />
          Upload File
        </Button>
        <input
          ref={fileRef}
          type="file"
          accept=".html,.css,.js"
          className="hidden"
          onChange={handleFileUpload}
        />
      </div>
      <Tabs defaultValue="html">
        <TabsList>
          <TabsTrigger value="html">HTML</TabsTrigger>
          <TabsTrigger value="css">CSS</TabsTrigger>
          <TabsTrigger value="js">JavaScript</TabsTrigger>
        </TabsList>
        <TabsContent value="html">
          <Textarea
            value={html}
            onChange={(e) => onChange("html", e.target.value)}
            placeholder="<!DOCTYPE html>..."
            className="font-mono text-sm min-h-[300px] resize-y"
            spellCheck={false}
          />
        </TabsContent>
        <TabsContent value="css">
          <Textarea
            value={css}
            onChange={(e) => onChange("css", e.target.value)}
            placeholder="/* Your CSS here */"
            className="font-mono text-sm min-h-[300px] resize-y"
            spellCheck={false}
          />
        </TabsContent>
        <TabsContent value="js">
          <Textarea
            value={js}
            onChange={(e) => onChange("js", e.target.value)}
            placeholder="// Your JavaScript here"
            className="font-mono text-sm min-h-[300px] resize-y"
            spellCheck={false}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
