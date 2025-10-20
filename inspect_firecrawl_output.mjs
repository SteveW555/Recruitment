import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

async function main() {
  const url = process.argv[2] ?? "https://docs.firecrawl.dev/mcp-server";
  const client = new Client(
    { name: "codex-agent", version: "1.0.0" },
    { capabilities: {} }
  );
  const transport = new StreamableHTTPClientTransport(new URL("http://localhost:3000/mcp"));
  await client.connect(transport);
  const result = await client.callTool({
    name: "firecrawl_scrape",
    arguments: {
      url,
      formats: ["markdown", "summary"],
      onlyMainContent: true,
      maxAge: 172800000
    }
  });
  await client.close();
  const textBlock = result?.content?.[0]?.text;
  if (!textBlock) {
    console.error("No text content returned");
    process.exit(1);
  }
  let parsed;
  try {
    parsed = JSON.parse(textBlock);
  } catch (err) {
    console.error("Failed to parse returned text", err);
    process.exit(1);
  }
  console.log(JSON.stringify({ keys: Object.keys(parsed), summaryPreview: parsed.summary?.slice(0, 500) }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
