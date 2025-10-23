/**
 * Test Classification Fix for Information Retrieval Queries
 *
 * Tests that queries with "locate" and other retrieval verbs
 * are correctly classified as information-retrieval instead of general-chat
 */

const classifyQuery = (query) => {
  const lowerQuery = query.toLowerCase();

  // General chat patterns
  if (/^(hi|hello|hey|good morning|good afternoon|good evening|how are you|whats up|sup|greetings)[\s\?]*$/i.test(lowerQuery)) {
    return 'general-chat';
  }

  // Information retrieval patterns
  if (/^(find|search|show|list|locate|retrieve|get|display|fetch|view|check|access|who|where|what|how many|give me|tell me|look up|pull up).*(candidate|job|placement|open|available|contact|email|phone|feedback|interview|notes|profile|record|data|information)/i.test(query) ||
    /^(find|search|locate|retrieve|get).*(with|having|that have).*(skill|experience|years|salary|location)/i.test(query)) {
    return 'information-retrieval';
  }

  // Problem solving patterns
  if (/^(why|analyze|identify|find|what.*issue|what.*problem|what.*challenge|what.*bottleneck|suggest|recommend|solve).*(is|are|we|our|the)/i.test(query)) {
    return 'problem-solving';
  }

  // Automation patterns
  if (/^(automate|workflow|set up|create|design|build).*(workflow|automation|process|pipeline|trigger|action)/i.test(query)) {
    return 'automation';
  }

  // Report generation patterns
  if (/^(generate|create|make|produce|compile|report|summary|dashboard|analytics|metrics|performance)/i.test(query)) {
    return 'report-generation';
  }

  // Industry knowledge patterns
  if (/^(what|tell me|explain|clarify).*(gdpr|ir35|right-to-work|employment law|compliance|regulation|standard|best practice|guideline|legal|law|requirement)/i.test(query) ||
    /^(gdpr|ir35|right-to-work|employment law|compliance|regulation)/i.test(query)) {
    return 'industry-knowledge';
  }

  // Default to general chat
  return 'general-chat';
};

// Test cases
const testCases = [
  // Original failing case
  { query: "Locate candidate interview feedback", expected: "information-retrieval" },

  // New verbs that should now work
  { query: "Retrieve candidate records", expected: "information-retrieval" },
  { query: "Get candidate details", expected: "information-retrieval" },
  { query: "Display job postings", expected: "information-retrieval" },
  { query: "Fetch placement data", expected: "information-retrieval" },
  { query: "Look up client information", expected: "information-retrieval" },
  { query: "Pull up candidate profile", expected: "information-retrieval" },
  { query: "Access interview notes", expected: "information-retrieval" },
  { query: "View candidate feedback", expected: "information-retrieval" },
  { query: "Check candidate records", expected: "information-retrieval" },

  // New entity keywords
  { query: "Find candidate feedback", expected: "information-retrieval" },
  { query: "Show interview notes", expected: "information-retrieval" },
  { query: "List candidate profiles", expected: "information-retrieval" },
  { query: "Search job records", expected: "information-retrieval" },
  { query: "Get placement information", expected: "information-retrieval" },

  // Existing cases that should still work
  { query: "Find candidates with Python", expected: "information-retrieval" },
  { query: "Search for jobs in London", expected: "information-retrieval" },
  { query: "Show me active placements", expected: "information-retrieval" },
  { query: "List all candidates", expected: "information-retrieval" },

  // Skills-based queries
  { query: "Locate candidates with 5+ years experience", expected: "information-retrieval" },
  { query: "Get candidates having JavaScript skills", expected: "information-retrieval" },
  { query: "Retrieve candidates that have sales experience", expected: "information-retrieval" },

  // Should NOT match (general-chat)
  { query: "Hello", expected: "general-chat" },
  { query: "How are you?", expected: "general-chat" },
  { query: "Tell me a joke", expected: "general-chat" },

  // Should match other agents
  { query: "Why is our placement rate dropping?", expected: "problem-solving" },
  { query: "Generate a quarterly report", expected: "report-generation" },
  { query: "Automate the onboarding workflow", expected: "automation" },
  { query: "What are GDPR requirements?", expected: "industry-knowledge" },
];

// Run tests
console.log("🧪 Testing Classification Fix\n");
console.log("=" .repeat(80));

let passed = 0;
let failed = 0;

testCases.forEach(({ query, expected }) => {
  const result = classifyQuery(query);
  const status = result === expected ? "✅ PASS" : "❌ FAIL";

  if (result === expected) {
    passed++;
  } else {
    failed++;
    console.log(`\n${status}`);
    console.log(`  Query:    "${query}"`);
    console.log(`  Expected: ${expected}`);
    console.log(`  Got:      ${result}`);
  }
});

console.log("\n" + "=".repeat(80));
console.log(`\n📊 Test Results: ${passed} passed, ${failed} failed out of ${testCases.length} total\n`);

if (failed === 0) {
  console.log("🎉 All tests passed! Classification fix is working correctly.\n");
  process.exit(0);
} else {
  console.log("⚠️  Some tests failed. Please review the classification patterns.\n");
  process.exit(1);
}
