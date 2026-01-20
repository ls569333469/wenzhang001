import { AdaptiveSidebar as AppSidebar } from "@/components/layout/AppSidebar";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background text-foreground font-sans overflow-hidden">
      <AppSidebar />
      <main className="flex-1 h-full overflow-hidden">
        {children}
      </main>
    </div>
  );
}
