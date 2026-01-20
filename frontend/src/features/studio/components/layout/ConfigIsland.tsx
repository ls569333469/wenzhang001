import { IslandContainer } from "./IslandContainer";
import { ConfigPanel } from "../ConfigPanel";

/**
 * ConfigIsland - 左侧配置岛
 * 
 * 职责: 
 * 1. 承载 ConfigPanel
 * 2. 处理响应式折叠 (Mobile Drawer vs Desktop Island)
 */
export function ConfigIsland() {
    return (
        <IslandContainer position="left">
            <ConfigPanel />
        </IslandContainer>
    );
}
