---
inclusion: always
---

# Technology Stack

## Document Format

- **Primary Format:** Markdown (.md)
- **Report Structure:** Structured markdown with consistent heading hierarchy
- **Data Source:** Salesforce CRM API integration

## Tech Stack

- Markdown for report generation and documentation
- Salesforce CRM as the data source
- Data analysis and reporting tools (specific implementation not visible in current codebase)

## Common Patterns

### Report File Naming Convention
```
{FirstName}_{LastName}_{Year}_Salesforce_Activities_Report.md
```

### Report Structure Template
1. Executive Summary (H2)
2. Activity Overview (H2)
3. Key Performance Highlights (H2)
4. Customer Portfolio Analysis (H2)
5. Activity Distribution Analysis (H2)
6. Strategic Impact Areas (H2)
7. Key Performance Indicators (H2)
8. Recommendations (H2)
9. Detailed Activity Timeline (H2)

### Markdown Formatting Standards
- Use H1 (#) for report title only
- Use H2 (##) for major sections
- Use H3 (###) for subsections
- Use bold (**text**) for emphasis on key metrics, names, and dates
- Use bullet points for lists and activity summaries
- Use numbered lists for sequential activities or recommendations
- Include horizontal rules (---) to separate major report sections

## Data Fields

### Employee Information
- Name and alias
- Role and department
- Location
- Reporting period

### Activity Metrics
- Total activities tracked
- Activities analyzed
- Geographic focus
- Activity types and distribution
- CSAT scores (when applicable)

### Activity Categories
- Workshops (Immersion Days, Other Workshops, Hackathons)
- Architecture Reviews
- Management Meetings (Office Hours, EBC Support)
- Thought Leadership (Public Speaking, Conferences)
- Partner Engagements

### Opportunity Tracking
- Opportunity name and ID
- Account association
- Status (Completed, In Progress, Closed Lost)
- Revenue impact (when applicable)

## Quality Standards

- Maintain consistent date formatting: "Month DD, YYYY" or "MMM-DD-YYYY"
- Include CSAT scores with precision to one decimal place (e.g., 4.7/5.0)
- Provide percentage calculations for activity distribution
- Include both completed and in-progress activities with clear status indicators
- Cross-reference activities with Salesforce opportunities when applicable
