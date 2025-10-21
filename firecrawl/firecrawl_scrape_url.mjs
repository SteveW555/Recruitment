import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

if (process.argv.length < 3) {
  console.error("Usage: node firecrawl_scrape_url.mjs <url>");
  process.exit(1);
}

const url = process.argv[2];

async function main() {
  const client = new Client(
    { name: "codex-agent", version: "1.0.0" },
    { capabilities: {} }
  );
  const transport = new StreamableHTTPClientTransport(
    new URL("http://localhost:3000/mcp")
  );
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
  console.log(JSON.stringify(result, null, 2));
  await client.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
