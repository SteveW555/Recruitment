# Feature Specification: Chat Routing AI

**Feature Branch**: `002-chat-routing-ai`
**Created**: 2025-10-22
**Status**: Draft
**Input**: User description: "Chat Routing AI. Chat entered into the prompt by the user will fall into one of six categories: 1. Simple information retrieval from multiple sources, basically a time-saving task. 2. Problem solving, real-world complex problems that would be quite challenging to solve manually given the amount of lookups and cross-referencing and research that would need to be done, again in natural language. 3. Report generation - presentation reports across a range of topics. These would be a way to present and visualize otherwise verbose data into easy to understand breakdowns, dashboards, visual, summaries etc., the kind of thing that would make attractive pdfs or slideshows to demonstrate and explain the data and topics to interested parties. 4. Automation - a request for creating an automation pipeline (like n8n or zapier, make might create) to solve repetitive tasks that the person in that role(s) has to do often. 5. Industry Knowledge - domain specific questions and possibly research related to the UK Recruitment industry and all its tangential workflows. A combination of search, pre-trained knowledge and using sources_validated_summaries.md to help locate online information. 6. Open ended non-industry chat from Hello to questions on unrelated topics. The plan for this next phase is to clearly define these roles and create an AI-based routing system that will correctly route a query to the appropriate AI agent, being a combination of the model, tools and resources."

## Clarifications

### Session 2025-10-22

- Q: When a query spans multiple categories (multi-intent), what resolution strategy should the router use? → A: Route to primary intent but show user a note: "This also relates to [secondary category]. Would you like me to route there instead?"
- Q: How long should session context be retained before expiring? → A: Session expires after 30 minutes of inactivity
- Q: What is the retention period for routing decision logs? → A: Retain for 90 days with anonymization after 30 days (remove user IDs, keep routing patterns)
- Q: What retry strategy should be used when a routed agent fails or times out? → A: Retry once with 2-second timeout, then fallback to general chat agent with explanation
- Q: What is the maximum query length the system should accept? → A: Accept up to 1000 words, truncate with warning for longer queries

## User Scenarios & Testing

### User Story 1 - Route Information Retrieval Query (Priority: P1)

A recruitment consultant asks "What are the top 5 job boards for sales positions in Bristol?" and receives information aggregated from multiple knowledge sources without having to search manually across multiple platforms.

**Why this priority**: This represents the most common use case (simple information retrieval) and delivers immediate time-saving value. It's the foundation for all routing logic.

**Independent Test**: Can be fully tested by submitting various information-seeking queries and verifying they are routed to the correct information retrieval agent, which returns relevant aggregated results.

**Acceptance Scenarios**:

1. **Given** a user submits a query asking for factual information from multiple sources, **When** the router analyzes the query, **Then** it correctly identifies it as Category 1 (Information Retrieval) and routes it to the information retrieval agent
2. **Given** the information retrieval agent receives a routed query, **When** it processes the query, **Then** it returns aggregated information from multiple relevant sources
3. **Given** a query like "What are the average salaries for software engineers in London?", **When** the system processes it, **Then** it routes to information retrieval and returns consolidated data from salary databases and job boards

---

### User Story 2 - Route Complex Problem Solving Query (Priority: P2)

A manager asks "How can we reduce candidate dropout rate by 20% within 3 months given our current pipeline issues?" and is directed to a problem-solving agent that performs multi-step analysis, cross-references industry data, and proposes actionable solutions.

**Why this priority**: This addresses high-value, complex business problems that significantly impact business outcomes. These queries require sophisticated reasoning and research capabilities.

**Independent Test**: Can be tested by submitting multi-faceted problem statements and verifying the router correctly identifies them as requiring problem-solving capabilities, with the agent returning structured analysis and recommendations.

**Acceptance Scenarios**:

1. **Given** a user submits a complex business problem requiring multiple analysis steps, **When** the router evaluates the query, **Then** it correctly identifies it as Category 2 (Problem Solving) and routes it to the problem-solving agent
2. **Given** the problem-solving agent receives a complex query, **When** it processes the request, **Then** it performs research across multiple sources, identifies root causes, and proposes evidence-based solutions
3. **Given** a query like "Why is our placement rate 15% lower than industry average and what should we do?", **When** processed, **Then** the system routes to problem-solving and returns analysis with cross-referenced industry benchmarks and recommendations

---

### User Story 3 - Route Report Generation Request (Priority: P3)

A business development manager requests "Create a quarterly performance report for our accountancy division showing placements, revenue, and candidate pipeline trends" and receives a structured, visualized report suitable for stakeholder presentation.

**Why this priority**: Report generation provides high-value output for decision-making and client presentations, though less frequently needed than information retrieval or problem solving.

**Independent Test**: Can be tested by requesting various report types and verifying correct routing to the report generation agent, which returns formatted, presentation-ready output.

**Acceptance Scenarios**:

1. **Given** a user requests a report, presentation, or data visualization, **When** the router analyzes the request, **Then** it correctly identifies it as Category 3 (Report Generation) and routes it to the report generation agent
2. **Given** the report generation agent receives a routing, **When** it processes the request, **Then** it creates a structured report with appropriate visualizations, summaries, and insights
3. **Given** a query like "Create a dashboard showing our top 10 clients by revenue this quarter", **When** processed, **Then** the system routes to report generation and produces presentation-ready output

---

### User Story 4 - Route Automation Pipeline Request (Priority: P2)

A recruiter describes "Every time a new candidate registers, I need to send them a welcome email, create a profile in our ATS, and schedule a screening call within 48 hours" and is directed to an automation agent that designs a workflow to handle this repetitive process.

**Why this priority**: Automation requests directly reduce operational overhead and improve efficiency. This is a high-impact use case that justifies P2 priority alongside problem solving.

**Independent Test**: Can be tested by describing various repetitive tasks and verifying the router identifies them as automation opportunities, with the agent returning structured workflow designs.

**Acceptance Scenarios**:

1. **Given** a user describes a repetitive task or workflow, **When** the router evaluates the query, **Then** it correctly identifies it as Category 4 (Automation) and routes it to the automation agent
2. **Given** the automation agent receives a workflow description, **When** it processes the request, **Then** it designs an automation pipeline with clear triggers, actions, and conditions
3. **Given** a query like "I need to automatically notify hiring managers when candidates apply for their jobs", **When** processed, **Then** the system routes to automation and returns a workflow specification

---

### User Story 5 - Route Industry-Specific Knowledge Query (Priority: P1)

A new recruiter asks "What is the typical notice period for permanent placements in the UK financial services sector?" and receives domain-specific information combining validated sources, industry standards, and recruitment best practices.

**Why this priority**: Domain knowledge queries are critical for day-to-day recruitment operations and represent a high-frequency use case. This must work reliably from day one.

**Independent Test**: Can be tested by asking UK recruitment-specific questions and verifying correct routing to the industry knowledge agent, which consults validated sources and domain expertise.

**Acceptance Scenarios**:

1. **Given** a user asks a question specific to UK recruitment industry practices, regulations, or standards, **When** the router analyzes the query, **Then** it correctly identifies it as Category 5 (Industry Knowledge) and routes it to the industry knowledge agent
2. **Given** the industry knowledge agent receives a domain query, **When** it processes the request, **Then** it consults validated sources, pre-trained knowledge, and sources_validated_summaries.md to provide authoritative answers
3. **Given** a query like "What are the GDPR requirements for storing candidate CVs?", **When** processed, **Then** the system routes to industry knowledge and returns compliant, UK-specific guidance

---

### User Story 6 - Route General Conversation (Priority: P3)

A user sends a casual greeting like "Hello" or asks an off-topic question like "What's the weather like today?" and receives a friendly, appropriate response without triggering specialized business agents.

**Why this priority**: While important for user experience and natural interaction, general chat is the lowest priority for business value. It should work but doesn't require the same sophistication as business-focused categories.

**Independent Test**: Can be tested by sending various non-business queries and casual messages, verifying they route to a general chat agent that provides appropriate responses without invoking specialized business logic.

**Acceptance Scenarios**:

1. **Given** a user sends a greeting or casual message, **When** the router evaluates the message, **Then** it correctly identifies it as Category 6 (General Chat) and routes it to the general conversation agent
2. **Given** a user asks a question unrelated to recruitment or business operations, **When** the router processes it, **Then** it routes to general chat rather than specialized agents
3. **Given** messages like "Hi there", "How are you?", or "Tell me a joke", **When** processed, **Then** the system routes to general chat and provides appropriate conversational responses

---

### Edge Cases

- When a query could fit multiple categories (e.g., "Create a report analyzing why our placement rate dropped and recommend solutions"), the system routes to the primary (highest-confidence) category and shows: "This also relates to [secondary category]. Would you like me to route there instead?"
- How does the system handle ambiguous queries that don't clearly fit any category?
- What happens when a user explicitly requests routing to a specific agent type?
- If a routed agent fails or times out, the system retries once with a 2-second timeout, then falls back to the general chat agent with an explanation: "I'm having trouble connecting to the specialized agent. Let me help you with this instead."
- What happens with very short queries (1-3 words) that lack context?
- Queries exceeding 1000 words are truncated to the first 1000 words with a warning message shown to the user: "Your query was truncated to 1000 words for processing."
- How does the system handle queries that combine recruitment-specific knowledge with general information needs?
- What happens when a query is in a language other than English?
- How does the system maintain conversation context when subsequent messages depend on previous routing decisions?

## Requirements

### Functional Requirements

- **FR-001**: System MUST analyze incoming user queries (up to 1000 words, with truncation warning for longer queries) and classify them into exactly one of six predefined categories (Information Retrieval, Problem Solving, Report Generation, Automation, Industry Knowledge, or General Chat)
- **FR-002**: System MUST route each classified query to the appropriate specialized agent handler based on its category
- **FR-003**: System MUST provide confidence scores for routing decisions to enable quality monitoring
- **FR-004**: System MUST handle multi-intent queries by routing to the primary (highest-confidence) intent and displaying a notification to the user: "This also relates to [secondary category name]. Would you like me to route there instead?"
- **FR-005**: System MUST maintain conversation context across multiple user messages within a session, with session expiring after 30 minutes of inactivity
- **FR-006**: System MUST log all routing decisions with category classifications and confidence scores for analysis, retaining logs for 90 days with user identifiers anonymized after 30 days
- **FR-007**: System MUST provide fallback behavior when classification confidence is below 0.7 (70%) by asking the user for clarification, presenting the top 2 most likely category suggestions
- **FR-008**: System MUST support explicit category override when users specify which agent type they want (e.g., "Route this to the automation agent")
- **FR-009**: System MUST handle agent failures by retrying once with a 2-second timeout, then falling back to the general chat agent with an explanation message to the user
- **FR-010**: System MUST enable each agent category to access appropriate tools and resources (e.g., Industry Knowledge agent must access sources_validated_summaries.md)
- **FR-011**: System MUST support modular agent definitions allowing easy addition of new categories in the future
- **FR-012**: System MUST distinguish between UK recruitment industry-specific queries and general information queries

### Key Entities

- **Query**: User input message requiring classification and routing, containing text content (maximum 1000 words), metadata (timestamp, user ID, session ID), and optional context from previous messages
- **Category**: One of six classification types (Information Retrieval, Problem Solving, Report Generation, Automation, Industry Knowledge, General Chat), each with associated routing rules and agent configurations
- **Agent Handler**: Specialized processing component for each category, configured with specific tools, resources, and capabilities appropriate for its category type
- **Routing Decision**: Classification result containing assigned category, confidence score, reasoning, and target agent handler
- **Session Context**: Conversation state tracking previous messages, routing decisions, and user preferences within a session (expires after 30 minutes of inactivity)
- **Agent Configuration**: Definition of agent capabilities including available tools, knowledge sources, and processing strategies for each category

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users receive responses to 95% of queries within 3 seconds of submission (end-to-end from query to routed agent response)
- **SC-002**: Routing accuracy reaches 90% or higher when evaluated against manually labeled test queries across all six categories
- **SC-003**: Users can successfully complete information retrieval tasks 40% faster compared to manual multi-source searches
- **SC-004**: Problem-solving queries receive comprehensive analysis that users rate as "useful" or "very useful" in 80% of cases
- **SC-005**: Generated reports meet stakeholder presentation standards in 85% of cases without requiring manual reformatting
- **SC-006**: Automation workflows designed by the system are successfully implemented without modification in 70% of cases
- **SC-007**: Industry knowledge responses cite appropriate validated sources in 95% of cases
- **SC-008**: System maintains conversation context accuracy across 95% of multi-turn conversations
- **SC-009**: Routing decision confidence scores correlate with actual routing accuracy (higher confidence = higher accuracy) with R² > 0.7

## Assumptions

- Users will provide queries in English (primary language)
- The system will integrate with existing ProActive People authentication and user management
- Specialized agents for each category already exist or will be developed in parallel
- The sources_validated_summaries.md file is maintained and up-to-date for industry knowledge queries
- Users will have appropriate permissions and access rights for their role-specific queries
- The system will operate within existing infrastructure performance constraints
- Query classification will use modern natural language understanding capabilities
- Routing decisions will be made synchronously before agent processing begins
- The modular file structure (utils/ai_router) will support future expansion with additional categories
- Confidence threshold for routing decisions is set to 0.7 (70%), below which the system will ask users for clarification
- Fallback behavior for low-confidence classifications will present the top 2 most likely category suggestions to the user
- Each agent handler will be responsible for its own response generation and error handling once routing is complete
