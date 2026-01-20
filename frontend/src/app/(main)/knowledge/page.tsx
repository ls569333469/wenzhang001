import { FileText, Upload, FolderOpen, MoreHorizontal } from "lucide-react";

/**
 * Knowledge Base Page v8.0: Digital Luxury Aesthetic
 * 
 * Design: Elegant gallery grid, documents as exhibits
 * No heavy borders, generous spacing, typographic hierarchy
 */

const knowledgeItems = [
  { id: 1, name: "Optimism Superchain 深度解析", tokens: 2847, date: "01.18" },
  { id: 2, name: "Arbitrum Orbit 生态报告", tokens: 1523, date: "01.17" },
  { id: 3, name: "Layer2 桥接协议对比", tokens: 3201, date: "01.15" },
  { id: 4, name: "DeFi 收益聚合器分析", tokens: 1876, date: "01.14" },
  { id: 5, name: "ZK-Rollup 技术白皮书", tokens: 4521, date: "01.12" },
  { id: 6, name: "MEV 保护机制研究", tokens: 2103, date: "01.10" },
];

export default function KnowledgePage() {
  return (
    <div className="h-full flex flex-col bg-paper overflow-hidden">
      {/* Header - Minimal */}
      <div className="px-8 pt-8 pb-6 shrink-0">
        <div className="flex items-end justify-between">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <FolderOpen className="w-5 h-5 text-ink-muted/50" />
              <h1 className="text-2xl font-serif font-medium text-ink-primary tracking-tight">
                知识库
              </h1>
            </div>
            <p className="text-sm text-ink-muted/60 ml-8">
              {knowledgeItems.length} 篇文档 · 已索引
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-zinc-900 text-white rounded-md hover:bg-zinc-800 transition-all text-sm font-medium shadow-lg shadow-zinc-900/10">
            <Upload className="w-4 h-4 opacity-70" />
            上传
          </button>
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="flex-1 overflow-y-auto px-8 pb-8">
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-6">
          {knowledgeItems.map((item) => (
            <article
              key={item.id}
              className="group cursor-pointer"
            >
              {/* Thumbnail */}
              <div className="aspect-[4/3] bg-white rounded-lg mb-4 flex items-center justify-center border border-hairline/30 group-hover:border-hairline transition-colors group-hover:shadow-lg group-hover:shadow-zinc-900/5">
                <FileText className="w-8 h-8 text-ink-muted/20 group-hover:text-ink-muted/40 transition-colors" />
              </div>
              {/* Meta */}
              <div className="flex items-start justify-between">
                <div className="min-w-0 pr-4">
                  <h3 className="text-sm font-medium text-ink-primary truncate group-hover:text-black transition-colors">
                    {item.name}
                  </h3>
                  <p className="text-xs text-ink-muted/50 mt-1">
                    {item.tokens.toLocaleString()} tokens · {item.date}
                  </p>
                </div>
                <button className="shrink-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreHorizontal className="w-4 h-4 text-ink-muted" />
                </button>
              </div>
            </article>
          ))}
        </div>

        {/* Drop Zone - Subtle */}
        <div className="mt-12 py-12 border border-dashed border-hairline/50 rounded-lg text-center">
          <Upload className="w-6 h-6 text-ink-muted/30 mx-auto mb-3" />
          <p className="text-sm text-ink-muted/50">
            拖拽文件至此处上传
          </p>
        </div>
      </div>
    </div>
  );
}
