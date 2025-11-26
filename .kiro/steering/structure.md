---
inclusion: always
---

# Project Structure

## Directory Organization

```
.
├── .kiro/                    # Kiro configuration and steering
│   ├── settings/            # Kiro settings and configurations
│   ├── specs/               # Feature specifications
│   └── steering/            # AI assistant steering rules
├── {Name}_2025_Salesforce_Activities_Report.md  # Individual activity reports
└── .DS_Store               # macOS system file (ignore)
```

## File Organization

### Report Files (Root Directory)
- Individual Salesforce activity reports are stored at the root level
- Each report represents a single employee's activities for a reporting period
- Reports are named using the pattern: `{FirstName}_{LastName}_{Year}_Salesforce_Activities_Report.md`

### Configuration (.kiro/)
- Contains Kiro-specific configuration and steering documents
- Steering rules guide AI assistant behavior when working with reports
- Settings and specs support development workflows

## Report Content Structure

Each report markdown file follows this internal structure:

1. **Title Section** - Employee name and report type
2. **Executive Summary** - Employee metadata (role, department, location, period)
3. **Activity Overview** - High-level metrics and focus areas
4. **Main Content Sections** - Organized by activity type or theme:
   - Leadership & Management Highlights
   - Innovation & Technology Leadership
   - Thought Leadership & Public Speaking
   - Strategic Account Management
   - Partner & Technology Engagements
   - Customer Relationship Management
5. **Analysis Sections** - Activity distribution, strategic impact, KPIs
6. **Recommendations** - Actionable insights and next steps
7. **Metadata Footer** - Report generation details
8. **Detailed Timeline** - Chronological activity breakdown by quarter

## Conventions

### Report Sections
- Use descriptive H2 headings for major sections
- Group related activities under thematic H3 subsections
- Number individual activities within sections for easy reference
- Include metadata (dates, participants, status) for each activity

### Activity Documentation
- Each activity should include: date, type, participants, focus, outcomes, and status
- Link activities to Salesforce opportunities when applicable
- Specify format (Virtual/In-Person) for each engagement
- Include CSAT scores for workshops and customer-facing events

### Data Presentation
- Use bullet points for lists and summaries
- Use numbered lists for sequential activities or recommendations
- Include percentage calculations for distribution analysis
- Provide both absolute numbers and percentages for metrics

### Cross-References
- Link activities to specific accounts and opportunities
- Reference Salesforce opportunity IDs and names
- Track opportunity status (Completed, In Progress, Closed Lost)
- Include revenue impact when available

## Scalability

The flat structure at the root level works for small teams. For larger deployments, consider organizing reports by:
- Year subdirectories
- Department or team subdirectories
- Geographic region subdirectories
