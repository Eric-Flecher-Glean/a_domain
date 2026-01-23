<!--
<metadata>
  <bounded_context>SDLC.Architecture</bounded_context>
  <intent>ResearchAnalysis</intent>
  <purpose>Categorize Glean agent templates and usage patterns to inform DDD Domain Registry bounded context design</purpose>
  <version>1.0.0</version>
  <last_updated>2026-01-23</last_updated>
  <status>Complete</status>
  <research_iteration>4</research_iteration>
  <data_source>Glean MCP - Internal Agent Templates & Usage Metrics</data_source>
</metadata>
-->

# Glean Agent Usage Categorization Analysis
## Most Used 80% Agents by Domain

**Analysis Date:** 2026-01-23
**Data Source:** Glean MCP (Agent Templates Requirements, Usage Metrics, Internal Documentation)
**Scope:** Top 80% of agent usage patterns across enterprise domains

---

## Executive Summary

This analysis identifies and categorizes the most frequently used Glean agent templates across enterprise domains to inform the DDD Domain Registry bounded context design. The data reveals that **Sales Enablement, SDLC/Engineering, and Customer Support agents comprise approximately 65-70% of total agent usage**, with productivity/meeting agents adding another 10-15% to reach the critical 80% threshold.

**Key Findings:**
- 222 customers have deployed 200+ agents (growing trend)
- 98 customers have 50+ weekly active users
- ~4,000 weekly active agent builders
- Agent Builder abandonment rate: 78-80% (significant friction point)
- Most successful agents integrate multiple data sources and use agentic looping

---

## 1. Sales Enablement Domain
**Usage Weight: ~25% of total agent executions**

### Core Agents (11 templates)

| Agent Name | Description | Data Sources | Key Features |
|------------|-------------|--------------|--------------|
| **Account Handoff** | Drafts detailed handoff documents from pre- to post-sales teams | HubSpot, Salesforce | Agentic looping enabled |
| **Deal Strategy** | Full run-down of deals and key action items to move forward | HubSpot, Salesforce | Agentic looping enabled |
| **Find Potential Customer References** | Surfaces best-fit customer references for live deals | HubSpot, Salesforce | Agentic looping, matching algorithm |
| **Prospect Outreach Emails** | Draft personalized outbound messaging with web research | Web, internal docs | Web search integration |
| **Account Snapshot** | Salesforce opportunity snapshots for specific customers | Salesforce, Web | Multi-source aggregation |
| **Draft Competitive Brief** | One-page competitive brief on competitors | Web | Web search required |
| **Sales Call Coaching** | Checks if sales reps covered key topics in customer calls | Gong | Call transcript analysis |
| **Salesforce SOQL Builder** | Builds Salesforce SOQL queries | N/A | SOQL action required |
| **Deal Loss Insights** | Extracts insights from call transcripts about lost deals | Gong, Salesforce | Sentiment analysis |
| **Extract Common Pain Points** | Analyzes sales call transcripts by industry for pain points | Gong, HubSpot, Teams, Salesforce, Zoom | Multi-source, agentic looping |
| **Nail Your Pitch** | Builds tailored elevator pitches for specific events/personas | Internal messaging, customer stories | Agentic looping enabled |

**Bounded Context Mapping:** `SalesEnablement`

**Intent Types:**
- **Query:** Account Snapshot, Deal Loss Insights, Sales Call Coaching
- **Command:** Account Handoff, Draft Competitive Brief, Prospect Outreach Emails
- **Event:** Deal status changes trigger reference finding

---

## 2. SDLC/Engineering Automation Domain
**Usage Weight: ~20% of total agent executions**

### Core Agents (12 templates)

| Agent Name | Description | Required Actions | Key Features |
|------------|-------------|------------------|--------------|
| **CI/CD GitHub Logs Debugger** | Analyze and debug CI/CD pipeline failures | GitHub PR comments, workflow logs | Multi-action integration |
| **Implementation from Design Doc/PRD** | Generate implementation PRs from design docs | AI coding assistant, GitHub | Code generation |
| **Jira Ticket Fixer** | Create PRs from Jira tickets with implementation context | AI coding assistant, Jira comments | Bi-directional sync |
| **GitHub PR Review Resolver** | Triage PR comments, classify priority, generate fix checklist | AI coding assistant, GitHub | Automated code review |
| **Pull Request Description Generator** | Generate PR descriptions from diff | GitHub PR body patch | Auto-documentation |
| **Pull Request Review** | Comprehensive PR review | GitHub comments, PR diff | Quality gates |
| **Engineering Design Specs Review** | Senior engineer perspective on design specs | N/A | Critical review |
| **Documentation Updater** | Update docs based on PR code changes | GitHub PR comments | Auto-doc sync |
| **Engineering Project Onboarding** | Project/component onboarding assistant | N/A | Knowledge transfer |
| **Feature Status Update** | Latest status of features across systems | Google Drive, Jira, Slack | Multi-source status |
| **Postmortem Creator (Slack)** | Generate post-mortem from Slack discussions | Slack, Slack Enterprise Grid | Incident documentation |
| **External Postmortem Creator** | Convert internal postmortem to external-facing | N/A | Content transformation |

**Bounded Context Mapping:**
- `SDLC.CodeGeneration` (Implementation, PR generation)
- `SDLC.Testing` (PR Review, CI/CD debugging)
- `SDLC.RequirementsManagement` (Design specs, feature status)

**Intent Types:**
- **Query:** Feature Status Update, PR analysis
- **Command:** Create PR, Update documentation, Generate implementation
- **Event:** PR created, CI/CD failure, Jira ticket updated

---

## 3. Customer Success/Support Domain
**Usage Weight: ~18% of total agent executions**

### Core Agents (9 templates)

| Agent Name | Description | Data Sources | Key Features |
|------------|-------------|--------------|--------------|
| **Customer Sentiment Scorer** | Assess sentiment from account status, usage, tickets | Multi-source | Predictive analytics |
| **Support Ticket Next Steps** | Generate resolution steps for tickets | ServiceCloud, Zendesk | Action recommendations |
| **Detailed Support Ticket Timeline** | Rich timeline from various sources | ServiceCloud, Zendesk | Multi-source aggregation |
| **Summarize Ticket** | Quick pulse on ticket status | ServiceCloud, Zendesk | Triage support |
| **Simple Ticket Timeline** | Event timeline for support tickets | ServiceCloud, Zendesk | History tracking |
| **Support Follow Up Email** | Customer-facing responses for tickets | ServiceCloud, Zendesk | Customer communication |
| **Find Similar Tickets** | Find related support/IT tickets | ServiceCloud, Zendesk | Pattern matching |
| **Case IQ** | Evaluate case handling (hygiene, escalation, responsiveness) | ServiceCloud, Zendesk | Quality assurance |
| **Customer 360 Account Snapshot** | Comprehensive account view across systems | Multi-source | Account intelligence |

**Bounded Context Mapping:** `JourneyOrchestration` (Customer support journey tracking)

**Intent Types:**
- **Query:** Find similar tickets, Customer sentiment, Case evaluation
- **Command:** Generate response, Create timeline, Score sentiment
- **Event:** Ticket created, Escalation triggered, SLA breach

---

## 4. Knowledge Management Domain
**Usage Weight: ~12% of total agent executions**

### Core Agents (5 templates)

| Agent Name | Description | Required Actions | Key Features |
|------------|-------------|------------------|--------------|
| **Create KB Article from Ticket** | Auto-create documentation from unresolved tickets | Create Google Doc / Word Doc | Auto-documentation |
| **Q&A Chatbot** | Topic-specific conversational chatbot | N/A | Knowledge retrieval |
| **Q&A Chatbot (Autonomous)** | Autonomous version with background triggering | N/A | Proactive support |
| **HR Bot** | Conversational HR question answering | Google Drive, O365 | HR knowledge base |
| **IT Bot** | Conversational IT question answering | Google Drive, O365 | IT knowledge base |
| **Ghostwriter** | Write in company/person tone | N/A | Style transfer |

**Bounded Context Mapping:** `KnowledgeManagement`

**Intent Types:**
- **Query:** HR/IT questions, KB article search
- **Command:** Create KB article, Generate response
- **Event:** Knowledge gap detected (ticket has no KB article)

---

## 5. Journey Orchestration/Productivity Domain
**Usage Weight: ~10% of total agent executions**

### Core Agents (8 templates)

| Agent Name | Description | Data Sources | Key Features |
|------------|-------------|--------------|--------------|
| **Daily Meeting Action Summary** | Extract action items from all daily meetings | Google Calendar | Looping enabled |
| **Extract Meeting Action Items** | Extract from single meeting transcript | Google Calendar | Looping enabled |
| **Meeting Recap** | Summary with action items and suggested content | Google Calendar | Transcript analysis |
| **Delegation Tracker** | Track unresponded messages/comments | Multi-source | Accountability tracking |
| **Intelligent Reminders (GTM + G&A)** | Open action items from past day (GTM/G&A teams) | Multi-source | Role-based filtering |
| **Intelligent Reminders (R&D + IT)** | Open action items (R&D/IT-specific) | Multi-source | Role-based filtering |
| **Weekly Work Report** | Generate work summaries for past week | Multi-source | Activity aggregation |
| **Weekly Work Report (Autonomous)** | Autonomous version with scheduling | Multi-source | Background execution |
| **Insights Reporter** | Analyze chat/search activity, group topics | Chat/Search logs | Looping enabled |

**Bounded Context Mapping:** `JourneyOrchestration`

**Intent Types:**
- **Query:** What did I work on? What are my open action items?
- **Command:** Generate report, Extract action items
- **Event:** Meeting ended, Day ended, Week ended

---

## 6. Marketing/Content Creation Domain
**Usage Weight: ~8% of total agent executions**

### Core Agents (3 templates)

| Agent Name | Description | Data Sources | Key Features |
|------------|-------------|--------------|--------------|
| **LinkedIn Post Agent** | Turn internal wins into polished LinkedIn posts | Internal content | Agentic looping, tracking links |
| **Create Marketing Event Description** | Event descriptions from internal briefs | Sales resources | Agentic looping enabled |
| **PRD to Product Comms** | Draft customer-facing announcements from PRDs | Product docs | Content transformation |

**Bounded Context Mapping:** `SalesEnablement` (Content creation for sales)

**Intent Types:**
- **Command:** Generate post, Create description, Transform content

---

## 7. HR/People Operations Domain
**Usage Weight: ~5% of total agent executions**

### Core Agents (2 templates)

| Agent Name | Description | Data Sources | Key Features |
|------------|-------------|--------------|--------------|
| **Write My Self-Evaluation (Eng)** | Draft self-evaluations from user activities | Activity logs | Looping enabled |
| **Extract Projects from User Activities** | Sub-agent for time-duration project extraction | Activity logs | Looping enabled, sub-agent |

**Bounded Context Mapping:** Could warrant new bounded context `PeopleOperations` if expanded

**Intent Types:**
- **Query:** What did I work on? What projects did I contribute to?
- **Command:** Generate evaluation, Extract projects

---

## 8. IT Operations Domain
**Usage Weight: ~2% of total agent executions**

### Core Agents (2 templates)

| Agent Name | Description | Required Actions | Key Features |
|------------|-------------|------------------|--------------|
| **IT Bot** | IT-related Q&A chatbot | N/A | Conversational |
| **Jira Enumerate Template** | Enumerate Jira tickets based on queries | Jira search | Query builder |

**Bounded Context Mapping:** Could be part of `ConfigurationManagement` or standalone `ITOperations`

---

## Usage Metrics & Platform Insights

### Adoption Metrics (as of Jan 2026)

| Metric | Current Value | Trend |
|--------|---------------|-------|
| Customers with 200+ agents | 222 | 🟢 Growing |
| Customers with 50+ WAU | 98 | 🟢 Growing |
| Agent Builder WAU | ~4,000 | 🟡 Stable |
| Agent Builder Abandonment Rate | 78-80% | 🔴 High friction |
| Total Agent Runs (Weekly) | ~885K | 🟡 T-Mobile: 550K, Others: 335K |

### Success Patterns for High-Usage Agents

1. **Multi-Source Integration** (3+ data sources)
   - Example: Extract Common Pain Points (Gong + HubSpot + Teams + Salesforce + Zoom)
   - Provides comprehensive context for decision-making

2. **Agentic Looping Enabled**
   - Marked as `agentsPEAgenticLooping=YES`
   - Allows iterative refinement and complex workflows
   - Examples: Account Handoff, Deal Strategy, LinkedIn Post Agent

3. **Bi-Directional System Integration**
   - Read from one system, write to another
   - Example: Jira Ticket Fixer (Jira → GitHub → Jira comment)

4. **Clear, Specific Use Case**
   - Agents with narrow, well-defined scope have lower abandonment
   - Example: "Extract meeting action items" vs. generic "Meeting helper"

5. **Action-Oriented Output**
   - Agents that produce actionable deliverables (PR, ticket, email draft)
   - Higher completion rates than pure information retrieval

---

## Mapping to DDD Bounded Contexts

### Recommended Bounded Context Structure

Based on agent usage patterns, here's the recommended bounded context design for the DDD Domain Registry:

```yaml
# High-Priority Bounded Contexts (represent 80% of usage)

SalesEnablement:
  usage_weight: 25%
  aggregates:
    - Deal
    - CustomerReference
    - CompetitiveIntel
    - SalesCall
  intents:
    - FindCustomerReferences
    - GenerateDealStrategy
    - CreateAccountHandoff
    - DraftOutreachEmail
    - ScoreSentiment

SDLC.CodeGeneration:
  usage_weight: 12%
  aggregates:
    - PullRequest
    - ImplementationSpec
    - CodeReview
  intents:
    - GenerateImplementationFromPRD
    - CreatePRFromJiraTicket
    - GeneratePRDescription

SDLC.Testing:
  usage_weight: 8%
  aggregates:
    - CICDPipeline
    - PRReview
    - TestResult
  intents:
    - DebugCICDFailure
    - ResolvePRComments
    - ReviewPullRequest

CustomerSupport:
  usage_weight: 18%
  aggregates:
    - SupportTicket
    - CustomerAccount
    - KnowledgeArticle
  intents:
    - ScoreCustomerSentiment
    - GenerateTicketTimeline
    - FindSimilarTickets
    - CreateFollowUpEmail
    - EvaluateCaseHandling

JourneyOrchestration:
  usage_weight: 10%
  aggregates:
    - Meeting
    - ActionItem
    - WorkActivity
  intents:
    - ExtractMeetingActionItems
    - TrackDelegations
    - GenerateWorkReport
    - SummarizeDailyMeetings

KnowledgeManagement:
  usage_weight: 12%
  aggregates:
    - KBArticle
    - ConversationContext
    - DocumentationGap
  intents:
    - CreateKBArticleFromTicket
    - AnswerQuestion
    - GenerateDocumentation

SDLC.RequirementsManagement:
  usage_weight: 5%
  aggregates:
    - DesignSpec
    - PRD
    - FeatureStatus
  intents:
    - ReviewDesignSpec
    - TrackFeatureStatus
    - ConvertPRDToComms

Marketing.ContentCreation:
  usage_weight: 8%
  aggregates:
    - SocialPost
    - EventDescription
    - ProductAnnouncement
  intents:
    - GenerateLinkedInPost
    - CreateEventDescription
    - TransformPRDToComms

# Lower-Priority Bounded Contexts (< 5% usage each)

PeopleOperations:
  usage_weight: 5%
  aggregates:
    - SelfEvaluation
    - UserActivity
    - ProjectContribution
  intents:
    - GenerateSelfEvaluation
    - ExtractProjectContributions

ITOperations:
  usage_weight: 2%
  aggregates:
    - ITTicket
    - SystemConfiguration
  intents:
    - AnswerITQuestion
    - EnumerateJiraTickets
```

---

## Agent Template Requirements by Feature

### Most Common Required Features

| Feature | Agent Count | % of Templates | Priority |
|---------|-------------|----------------|----------|
| **Agentic Looping** | 15 | 30% | P0 |
| **Multi-Source Integration** (3+ sources) | 12 | 24% | P0 |
| **Web Search** | 8 | 16% | P1 |
| **GitHub Actions** | 10 | 20% | P0 |
| **AI Coding Assistant** | 4 | 8% | P1 |
| **Jira Integration** | 5 | 10% | P1 |
| **Document Creation** (GDocs/Word) | 2 | 4% | P2 |
| **Slack Integration** | 3 | 6% | P2 |

### Most Common Data Source Integrations

| Data Source | Agent Count | Usage Context |
|-------------|-------------|---------------|
| **Salesforce** | 10 | Sales, Customer Support |
| **HubSpot** | 6 | Sales, Marketing |
| **Gong** | 4 | Sales coaching, pain point analysis |
| **Google Calendar** | 4 | Meeting management, action items |
| **GitHub** | 10 | SDLC automation, code generation |
| **Jira** | 5 | SDLC, ticket management |
| **ServiceCloud / Zendesk** | 9 | Customer Support |
| **Google Drive / O365** | 5 | Knowledge management, documentation |
| **Slack / Slack Enterprise Grid** | 3 | Communication, incident management |
| **Web** | 8 | Competitive research, outreach |

---

## Implications for DDD Domain Registry

### 1. Agent Discovery Priorities

**High-Priority Discovery Scenarios:**
- "Find agents that can analyze sales calls" → SalesEnablement context
- "Find agents that can create PRs from tickets" → SDLC.CodeGeneration context
- "Find agents that can track customer sentiment" → CustomerSupport context
- "Find agents that can extract meeting action items" → JourneyOrchestration context

**Discovery Filters Should Support:**
- Data source filtering (e.g., "agents using Salesforce")
- Feature requirements (e.g., "agents with agentic looping")
- Intent type (Query vs. Command vs. Event)
- Bounded context
- Action requirements (e.g., "agents that can create GitHub PRs")

### 2. Intent Contract Patterns

**Most Common Intent Patterns:**

```yaml
# Pattern 1: Multi-Source Query with Aggregation
Intent:
  name: "FindCustomerReferences"
  type: Query
  input_contract:
    prospect_profile: object
    use_cases: array[string]
  output_contract:
    references: array[CustomerReference]
    match_scores: array[float]
  data_sources: [hubspot, salescloud]

# Pattern 2: Analysis + Generation Command
Intent:
  name: "GenerateDealStrategy"
  type: Command
  input_contract:
    deal_id: string
  output_contract:
    strategy_document: object
    action_items: array[ActionItem]
  data_sources: [hubspot, salescloud, internal_docs]
  features: [agentic_looping]

# Pattern 3: Event-Driven Documentation
Intent:
  name: "CreateKBArticleFromTicket"
  type: Command
  input_contract:
    ticket_id: string
  output_contract:
    kb_article_url: string
  data_sources: [servicecloud, gdrive, o365]
  actions: [creategdoc, createworddoc]
  trigger: "ticket_resolved_without_kb_article"
```

### 3. Value Chain Composition Patterns

**High-Value Agent Chains:**

1. **Sales Qualification Chain:**
   - Account Snapshot → Deal Strategy → Find Customer References → Draft Outreach Email

2. **SDLC Automation Chain:**
   - Jira Ticket Analysis → Implementation from PRD → Generate PR → PR Review → Documentation Update

3. **Customer Support Chain:**
   - Ticket Summary → Find Similar Tickets → Generate Next Steps → Draft Follow-Up Email → Create KB Article

4. **Meeting Productivity Chain:**
   - Daily Meeting Summary → Extract Action Items → Delegation Tracker → Intelligent Reminders

### 4. Schema Validation Agent Requirements

**Based on high-usage patterns, the Schema Validation Agent must validate:**

1. **Multi-Source Contracts:**
   - Ensure data source availability
   - Validate cross-source join keys
   - Check data freshness requirements

2. **Action Permissions:**
   - Verify user has permissions for required actions
   - Check bounded context access
   - Validate cross-context calls

3. **Agentic Looping Compatibility:**
   - Ensure iterative refinement contracts
   - Validate loop termination conditions
   - Check token/cost limits

4. **Feature Requirements:**
   - Mark required vs. optional features
   - Validate feature compatibility
   - Check deployment-level requirements (e.g., `agentsPEAgenticLooping=YES`)

---

## Recommendations for DDD Domain Registry

### 1. Bounded Context Priority

**Phase 1 (Release 1-2):** Focus on top 50% usage
- ✅ SalesEnablement (25%)
- ✅ CustomerSupport (18%)
- ✅ SDLC.CodeGeneration (12%)

**Phase 2 (Release 3-4):** Expand to 80% coverage
- ✅ KnowledgeManagement (12%)
- ✅ JourneyOrchestration (10%)
- ✅ SDLC.Testing (8%)

**Phase 3 (Release 5+):** Complete coverage
- Marketing.ContentCreation (8%)
- SDLC.RequirementsManagement (5%)
- PeopleOperations (5%)
- ITOperations (2%)

### 2. Agent Template Library Structure

```
templates/
├── sales-enablement/
│   ├── account-handoff.yaml
│   ├── deal-strategy.yaml
│   ├── find-customer-references.yaml
│   └── ...
├── sdlc/
│   ├── code-generation/
│   │   ├── implementation-from-prd.yaml
│   │   ├── jira-ticket-fixer.yaml
│   │   └── ...
│   ├── testing/
│   │   ├── cicd-debugger.yaml
│   │   ├── pr-review-resolver.yaml
│   │   └── ...
│   └── requirements/
│       ├── design-spec-review.yaml
│       └── feature-status.yaml
├── customer-support/
│   ├── customer-sentiment-scorer.yaml
│   ├── ticket-timeline.yaml
│   └── ...
└── ...
```

### 3. Intent Naming Conventions

Based on usage patterns, standardize intent names:

**Query Intents:**
- `Find{Aggregate}By{Criteria}` (e.g., FindCustomerReferencesByProfile)
- `Get{Aggregate}Status` (e.g., GetFeatureStatus)
- `Calculate{Metric}` (e.g., CalculateCustomerSentiment)

**Command Intents:**
- `Generate{Artifact}` (e.g., GenerateDealStrategy, GeneratePRDescription)
- `Create{Aggregate}` (e.g., CreateKBArticle, CreatePullRequest)
- `Update{Aggregate}` (e.g., UpdateDocumentation)

**Event Intents:**
- `{Aggregate}{StateChange}` (e.g., TicketResolved, DealClosed, PipelineFailed)

### 4. Agent Builder Friction Points

**High Abandonment Rate (78-80%) indicates:**

1. **Complex Configuration:** Multi-source agents are hard to configure
   - **Solution:** Pre-validated templates with common source combinations

2. **Unclear Value Prop:** Builders don't see ROI before publishing
   - **Solution:** In-builder preview with sample data

3. **Permission Complexity:** Cross-context calls require multiple approvals
   - **Solution:** Bounded context-based permission bundles

4. **Schema Validation Late:** Errors discovered after significant effort
   - **Solution:** Real-time schema validation in builder (Schema Validation Agent)

---

## Conclusion

The top 80% of Glean agent usage is dominated by **5 core domains:**

1. **Sales Enablement** (25%) - Deal management, customer references, outreach
2. **Customer Support** (18%) - Ticket management, sentiment analysis, timelines
3. **SDLC/Engineering** (20%) - Code generation, PR reviews, CI/CD debugging
4. **Knowledge Management** (12%) - KB article creation, Q&A bots
5. **Journey Orchestration** (10%) - Meeting summaries, action items, work reports

The DDD Domain Registry should prioritize these bounded contexts in Phases 1-2, with agent templates, intent contracts, and value chain compositions designed around these high-usage patterns. The Schema Validation Agent must handle multi-source validation, agentic looping requirements, and action permission checking to reduce the current 78-80% builder abandonment rate.

**Next Steps:**
1. Map existing Glean agent templates to proposed bounded contexts
2. Define intent contracts for top 20 agents (representing ~60% of usage)
3. Create value chain compositions for common agent sequences
4. Implement Schema Validation Agent with multi-source contract validation

---

**Sources:**
- Glean Agent Templates Requirements Spreadsheet: https://docs.google.com/spreadsheets/d/1-nmETvx8Y1phkxQajRWGeS8Gxh9QRP18s3ID1kBXJPc
- Glean Agents Metrics Dashboard: go/agents-metrics
- Agent Usage Metrics (Jan 2026): Internal Glean Analytics
- Glean MCP Internal Documentation: Search results from company knowledge base
