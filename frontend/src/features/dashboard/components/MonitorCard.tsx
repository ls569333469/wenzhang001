import React from "react";
import { Circle } from "lucide-react";
import { UI_TEXT } from "@/config/constants";

interface MonitorCardProps {
    label: string;
    status: "online" | "offline" | "busy";
    latency?: string;
}

export function MonitorCard({ label, status, latency }: MonitorCardProps) {
    const isOnline = status === "online";

    return (
        <div className="p-5 bg-white border border-zinc-200 rounded-sm">
            <p className="text-[10px] font-semibold tracking-widest text-zinc-400 uppercase mb-3">
                {label}
            </p>
            <div>
                <div className="flex items-center gap-2 mb-1">
                    <Circle
                        size={8}
                        className={isOnline ? "text-emerald-500 fill-emerald-500 animate-pulse" : "text-red-400 fill-red-400"}
                    />
                    <span className={`text-lg font-serif font-medium ${isOnline ? "text-zinc-800" : "text-zinc-400"}`}>
                        {isOnline ? UI_TEXT.monitor.operational : UI_TEXT.monitor.offline}
                    </span>
                </div>
                <p className="text-xs text-zinc-400 font-mono">
                    {latency ? `${latency} ${UI_TEXT.monitor.latencyLabel}` : UI_TEXT.monitor.connectionFailed}
                </p>
            </div>
        </div>
    );
}

