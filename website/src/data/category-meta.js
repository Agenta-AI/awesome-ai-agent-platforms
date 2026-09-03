export const META = {
  "ai-coworkers": {
    category: "AI coworkers and teammates",
    title: "Best open-source AI coworkers and AI teammate platforms",
    h1: "Open-source AI coworkers and teammates",
    lead: "AI coworkers are persistent agents you delegate real work to. They sign in to your tools, keep context between sessions, run tasks on schedules, and return finished work. This page lists the open-source and source-available platforms in that category, with the license and hosting model for each.",
    look: [
      "Whether the agent can sign in to and act inside your existing tools",
      "Persistent memory and context that carries across sessions",
      "Scheduled and background runs, not just live chat",
      "Team sharing, so more than one person can use and manage an agent",
      "Self-hosting, so data and credentials stay in your infrastructure",
      "Freedom to choose the underlying model or use your existing subscription",
    ],
    faqs: [
      {
        q: "What is the difference between an AI coworker and a chatbot?",
        a: "A chatbot answers questions in a conversation. An AI coworker is delegated a task, uses tools to complete it across multiple steps, keeps context over time, and returns finished work. The coworker is managed like a team member rather than queried like a search box.",
      },
      {
        q: "Can I run an AI coworker on my own infrastructure?",
        a: "Yes. Most platforms in this category can be self-hosted, which keeps your data and tool credentials on your own machines or servers. Each entry states its exact hosting model.",
      },
    ],
  },
  "agent-builders": {
    category: "Agent builders and frameworks",
    title: "Best open-source AI agent builders and frameworks",
    h1: "Open-source agent builders and frameworks",
    lead: "Agent builders and frameworks are the tools developers use to create, connect, run, and inspect agents. Some are code libraries, others are visual platforms. This page lists the open-source and source-available options, with the license and hosting model for each.",
    look: [
      "Code library versus visual builder, matched to who will maintain the agents",
      "Model portability, so you are not locked to one provider",
      "State and memory handling for long-running agents",
      "Deployment path from prototype to production",
      "Observability and tracing for debugging agent behavior",
      "License terms, since some builders separate enterprise features",
    ],
    faqs: [
      {
        q: "What is the difference between an agent framework and an agent platform?",
        a: "A framework is a code library you embed in your own application and control in code. A platform is a runnable product with its own interface, often including a visual builder, deployment, and monitoring. Frameworks give more control; platforms start faster.",
      },
      {
        q: "Do I need to write code to build an agent?",
        a: "Not always. Several tools in this category offer visual builders that need little or no code, while others are code-first libraries. The right choice depends on who will build and maintain the agents.",
      },
    ],
  },
  "workflow-automation": {
    category: "Workflow automation platforms",
    title: "Best open-source and self-hostable workflow automation platforms",
    h1: "Open-source and self-hostable workflow automation platforms",
    lead: "Workflow automation platforms run repeatable processes from triggers, schedules, and integrations, and many now include AI steps or embedded agents. This page lists the open-source and source-available options, with the license and hosting model for each. Read license terms carefully here, because several use fair-code or source-available licenses rather than standard open source.",
    look: [
      "Breadth of prebuilt integrations with the services you use",
      "AI steps and the ability to embed agents inside a workflow",
      "Code steps for logic the visual nodes cannot express",
      "Self-hosting support and how much is gated behind an enterprise license",
      "Triggers and scheduling for event-driven and recurring runs",
      "The exact license, since fair-code terms restrict some commercial uses",
    ],
    faqs: [
      {
        q: "How do workflow automation platforms differ from AI agents?",
        a: "Automation platforms execute flows you define in advance, which makes them predictable. Agents decide their own steps toward a goal. Many teams combine both: a workflow handles the reliable parts and calls an agent for the open-ended step.",
      },
      {
        q: "Are these platforms fully open source?",
        a: "Some are, and some are source-available or fair-code, which publishes the code but restricts certain uses. Each entry states its exact license so you can judge fit before adopting it.",
      },
    ],
  },
  "browser-agents": {
    category: "Browser agents",
    title: "Open-source browser agents for web automation",
    h1: "Open-source browser agents",
    lead: "Browser agents operate a web browser the way a person does, navigating pages, filling forms, and completing tasks on websites that have no API. This page lists the open-source browser agents in this directory, with the license and hosting model for each.",
    look: [
      "Reliability on dynamic, JavaScript-heavy sites",
      "Self-hosting versus a managed cloud option",
      "Whether it is a developer library or a ready-to-use product",
      "How it handles logins, sessions, and anti-bot measures",
      "The exact license, including any managed-only components",
    ],
    faqs: [
      {
        q: "When do I need a browser agent instead of an API integration?",
        a: "Use a browser agent when the site or task has no usable API, or when the workflow spans several pages a person would normally click through. When a clean API exists, calling it directly is usually more reliable.",
      },
    ],
  },
  "coding-agents": {
    category: "Coding agents",
    title: "Best open-source coding agents",
    h1: "Open-source coding agents",
    lead: "Coding agents read a codebase, edit files, run commands and tests, and iterate until a software task is done. This page lists the open-source coding agents in this directory, with the license and hosting model for each.",
    look: [
      "Where it runs: terminal, IDE extension, or a self-hosted platform",
      "Which model providers it supports, including local models",
      "Sandboxing and how it isolates command execution",
      "Multi-file edits and how it navigates a large codebase",
      "Cost control, since coding tasks can use many tokens",
    ],
    faqs: [
      {
        q: "Do coding agents work with any language model?",
        a: "Most support several providers, and some are tuned for low-cost or local models. Each platform page lists the documented model support.",
      },
    ],
  },
};
