import { Board, BOARDS } from "@/lib/boards";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Cpu } from "lucide-react";

interface BoardSelectorProps {
  selectedBoard: Board | null;
  onSelect: (board: Board) => void;
}

export function BoardSelector({ selectedBoard, onSelect }: BoardSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium flex items-center gap-2">
        <Cpu className="h-4 w-4" />
        Board
      </label>
      <Select
        value={selectedBoard?.id ?? ""}
        onValueChange={(id) => {
          const board = BOARDS.find((b) => b.id === id);
          if (board) onSelect(board);
        }}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select a board..." />
        </SelectTrigger>
        <SelectContent>
          {BOARDS.map((board) => (
            <SelectItem key={board.id} value={board.id}>
              <div className="flex items-center gap-2">
                <span>{board.name}</span>
                <Badge variant={board.chip === "esp32" ? "default" : "secondary"} className="text-xs">
                  {board.chip.toUpperCase()}
                </Badge>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {selectedBoard && (
        <p className="text-xs text-muted-foreground">
          {selectedBoard.description} · Flash: {selectedBoard.flashSize} · SPIFFS: {selectedBoard.spiffsSize}
        </p>
      )}
    </div>
  );
}
