import { readFile, writeFile } from "fs/promises";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const SOURCE_PATH = "sources.md";
const OUTPUT_PATH = "firecrawl_results.json";

async function extractUrls() {
  const text = await readFile(SOURCE_PATH, "utf-8");
  const regex = /(https?:\/\/[^\s)]+)(?=\)|\s|$)/g;
  const urls = new Set();
  for (const match of text.matchAll(regex)) {
    let url = match[1];
    // Remove trailing punctuation
    url = url.replace(/[.,:)]+$/g, "");
    urls.add(url);
  }
  return Array.from(urls);
}

async function fetchWithFirecrawl(client, url, attempt = 1) {
  try {
    const response = await client.callTool({
      name: "firecrawl_scrape",
      arguments: {
        url,
        formats: ["markdown", "summary"],
        onlyMainContent: true,
        maxAge: 172800000
      }
    });
    const textBlock = response?.content?.[0]?.text;
    if (!textBlock) {
      throw new Error("No text returned");
    }
    let parsed;
    try {
      parsed = JSON.parse(textBlock);
    } catch (err) {
      throw new Error(`JSON parse error: ${err.message}`);
    }
    return parsed;
  } catch (error) {
    if (attempt < 2) {
      await new Promise((resolve) => setTimeout(resolve, 5000));
      return fetchWithFirecrawl(client, url, attempt + 1);
    }
    return { error: error?.message ?? String(error) };
  }
}

async function main() {
  const urls = await extractUrls();
  const results = {};
  const client = new Client(
    { name: "codex-agent", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );
  const transport = new StreamableHTTPClientTransport(new URL("http://localhost:3000/mcp"));
  await client.connect(transport);

  let index = 0;
  for (const url of urls) {
    index += 1;
    console.log(`[${index}/${urls.length}] Fetching ${url}`);
    const data = await fetchWithFirecrawl(client, url);
    results[url] = data;
  }

  await client.close();
  await writeFile(OUTPUT_PATH, JSON.stringify(results, null, 2));
  console.log(`Saved results to ${OUTPUT_PATH}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
