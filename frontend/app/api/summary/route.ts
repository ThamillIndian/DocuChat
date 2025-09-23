export async function POST() {
  // In a future step, use uploaded docs / chat history to compute this summary.
  return Response.json({
    summary: [
      "• This is a placeholder summary for your uploaded documents.",
      "• Wire this endpoint to your summarization logic to generate real results.",
      "• The Summary panel now has a single button to trigger this request.",
    ].join("\n"),
  })
}
