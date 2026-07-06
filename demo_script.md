# TasteBoard Agent - Kaggle Demo Script

*(Estimated Time: 2-3 minutes)*

---

### [0:00] Introduction
**"Hi, I'm presenting TasteBoard, a data-backed market research agent built for the 'Agents for Business' track."**

**"Founders often have great product ideas but struggle to objectively validate them. They spend hours manually searching for competitors, reading reviews, and trying to figure out if there's an actual market gap. TasteBoard automates this entire process using a multi-agent architecture."**

---

### [0:30] The Demo
*(Open the Streamlit App)*

**"Here is the TasteBoard Streamlit UI. A founder just types their raw product idea into the box."**
*(Show the input box containing the demo idea: "I want to build an AI tool that helps creators repurpose long YouTube videos...")*

**"When I click 'Run Analysis', a team of 8 specialized agents goes to work."**
*(Click 'Run Analysis'. While it loads, explain the architecture.)*

---

### [0:45] The Architecture & MCP
**"Under the hood, we are using a Coordinator pattern. Instead of one massive prompt, the Coordinator orchestrates 8 distinct sub-agents sequentially."**

**"Crucially, these agents interact with the outside world through a dedicated Model Context Protocol (MCP) server. The Coordinator acts as a strict security layer—it injects a specific `call_tool` capability into each sub-agent. For example, the Market Search Agent is only authorized to call the web search tool, while the Review Mining Agent is only authorized to cluster complaints."**

**"This guarantees isolated tool scoping and prevents hallucination, ensuring that every piece of data is traced back to real evidence."**

---

### [1:30] The Results
*(The loading spinner finishes, and the UI displays the charts and report.)*

**"The pipeline just finished. First, you'll see the Visualization Agent has generated live charts based on real competitor data."**
*(Scroll past the charts: Ratings, Review Volumes, Top Complaints, and the Opportunity Radar.)*

**"And here is the final 12-section Founder Feasibility Report assembled by the Report Agent. It has taken the vague idea and mapped out:"**
- **"The core target users and keywords."**
- **"Real competitor benchmarks with live pricing and rating data."**
- **"A gap analysis of user complaints mined from real reviews."**
- **"And a final, data-backed Opportunity Score."**

---

### [2:15] Conclusion
**"In summary, TasteBoard demonstrates a robust, production-ready multi-agent workflow. It uses strict tool-scoping via MCP, delegates complex tasks to specialized agents, and ultimately delivers immense business value by turning a vague idea into actionable market intelligence."**

**"Thank you!"**
