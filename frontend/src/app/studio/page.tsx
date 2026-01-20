import { StudioLayout } from "@/features/studio/layout/StudioLayout";
import { ConfigIsland } from "@/features/studio/components/layout/ConfigIsland";
import { AgentIsland } from "@/features/studio/components/layout/AgentIsland";
import { WritingCanvas } from "@/features/studio/components/WritingCanvas";

/**
 * Studio Page - 组装页
 * 
 * 核心: 使用 StudioLayout 布局，传入左右 Island
 */
export default function StudioPage() {
    return (
        <StudioLayout
            leftPanel={<ConfigIsland />}
            rightPanel={<AgentIsland />}
        >
            {/* Layer 1: Central Canvas Content (Client Component) */}
            <WritingCanvas />
        </StudioLayout>
    );
}

