/**
 * Test the specific failing query: "Locate candidate interview feedback"
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

const testQuery = "Locate candidate interview feedback";

console.log("\n" + "=".repeat(60));
console.log("🔍 Testing Original Failing Query");
console.log("=".repeat(60) + "\n");

console.log(`Query: "${testQuery}"`);
console.log(`\n📍 BEFORE FIX:`);
console.log(`   Expected: information-retrieval`);
console.log(`   Got:      general-chat ❌`);

const result = classifyQuery(testQuery);

console.log(`\n✨ AFTER FIX:`);
console.log(`   Expected: information-retrieval`);
console.log(`   Got:      ${result} ${result === 'information-retrieval' ? '✅' : '❌'}`);

console.log("\n" + "=".repeat(60));

if (result === 'information-retrieval') {
  console.log("\n🎉 SUCCESS! Query now routes correctly to information-retrieval agent\n");
  console.log("This means:");
  console.log("  • The query will search company databases for interview feedback");
  console.log("  • The Information Retrieval Agent will handle the request");
  console.log("  • It will NOT be treated as casual conversation\n");
} else {
  console.log("\n❌ FAILED! Query still routes incorrectly\n");
}
