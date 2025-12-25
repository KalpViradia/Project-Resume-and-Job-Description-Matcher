import { Shell } from "@/components/Shell";
import { Chatbot } from "@/components/Chatbot";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <>
            <Shell>
                {children}
            </Shell>
            <Chatbot />
        </>
    );
}
