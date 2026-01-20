import { PaperCard } from "@/components/ui/paper-card";
import { Settings } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="h-full flex flex-col items-center justify-center bg-paper p-8">
      <PaperCard className="max-w-md text-center">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-zinc-100 flex items-center justify-center">
          <Settings className="w-8 h-8 text-ink-muted" />
        </div>
        <h1 className="text-xl font-serif font-medium text-ink-primary mb-2">
          系统设置
        </h1>
        <p className="text-sm text-ink-muted">
          此功能正在开发中，敬请期待 Phase 4...
        </p>
      </PaperCard>
    </div>
  );
}
