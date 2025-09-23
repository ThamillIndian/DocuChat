import ChatPanel from "../components/chat-panel"
import SummaryPanel from "../components/summary-panel"

export default function Page() {
  return (
    <main className="p-4 md:p-6 h-dvh overflow-hidden">
      <div className="flex flex-col gap-4 md:grid md:grid-cols-[1fr_360px] md:h-full">
        {/* Chat Panel */}
        <section aria-labelledby="chat-heading" className="md:col-span-1 md:h-full overflow-auto min-h-0">
          <h2 id="chat-heading" className="sr-only">
            Chat
          </h2>
          <ChatPanel />
        </section>

        {/* Summary Panel (now includes Upload) */}
        <section aria-labelledby="summary-heading" className="md:col-span-1 md:h-full overflow-auto min-h-0">
          <h2 id="summary-heading" className="sr-only">
            Summary
          </h2>
          <SummaryPanel />
        </section>
      </div>
    </main>
  )
}
