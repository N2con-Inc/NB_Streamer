# GitHub Issues & Project Board Setup Guide

**Project**: NB_Streamer Product Backlog Management  
**Purpose**: Configure GitHub Issues and Project Board for tracking Epics and User Stories

## GitHub Project Board Configuration

### Project Setup
1. **Create GitHub Project**: "NB_Streamer MVP Development"
2. **Project Type**: Board view with custom fields
3. **Visibility**: Private (or Public based on preference)

### Board Columns
| Column | Purpose | WIP Limit |
|--------|---------|-----------|
| **📋 Backlog** | All unstarted issues | No limit |
| **🔄 Ready** | Issues ready to start (dependencies met) | No limit |
| **⚡ In Progress** | Currently being worked on | 3 |
| **👀 Review** | Code review and testing | 5 |
| **✅ Done** | Completed and merged | No limit |

### Custom Fields
- **Epic**: Link to parent Epic issue
- **Story Points**: Number field (1-9)
- **Complexity**: Select (Small, Medium, Large) 
- **Functional Area**: Select (Streaming Core, Auth, UI/API, Packaging, CI/CD)
- **MVP Priority**: Select (Critical, High, Medium, Low)

## Labels Configuration

### Priority Labels
```
🔴 priority/critical - Critical MVP functionality
🟡 priority/high - High MVP priority  
🟢 priority/medium - Medium priority
⚪ priority/low - Low priority (future)
```

### Type Labels
```
📋 type/epic - Epic-level work
📝 type/story - User story
🐛 type/bug - Bug fixes
📚 type/documentation - Documentation
🧪 type/testing - Testing work
```

### Size Labels
```
🔸 size/S - Small (1-3 points)
🔹 size/M - Medium (4-6 points) 
🔷 size/L - Large (7-9 points)
```

### Functional Area Labels
```
⚡ area/streaming-core - Core event processing
🔐 area/auth - Authentication system
🌐 area/ui-api - Web service and API
📦 area/packaging - Docker and deployment
🔄 area/ci-cd - Testing and CI/CD
```

### Status Labels
```
🚀 status/ready - Ready to start
⏸️ status/blocked - Blocked by dependency
🔥 status/urgent - Needs immediate attention
```

## Issue Templates

### Epic Issue Template
```markdown
---
name: Epic
about: Epic-level work item
title: "[EPIC] "
labels: type/epic
assignees: ''
---

## Epic Description
Brief description of the epic and its business value.

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## User Stories
Link to related user stories:
- [ ] #issue_number - Story title
- [ ] #issue_number - Story title

## Definition of Done
- [ ] All user stories completed
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Code reviewed and merged

## Notes
Any additional context or considerations.
```

### User Story Issue Template
```markdown
---
name: User Story
about: User story work item
title: "[STORY] "
labels: type/story
assignees: ''
---

## User Story
As a **[user type]**, I want [goal] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Notes
Implementation details, API contracts, etc.

## Definition of Done
- [ ] Code implemented and tested
- [ ] Unit tests written and passing
- [ ] Integration tests passing (if applicable)
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Merged to main branch

## Dependencies
- Depends on: #issue_number
- Blocks: #issue_number

## Testing Notes
Specific testing requirements or scenarios.
```

## Bulk Issue Creation Script

Here's a Python script to create all Epic and Story issues programmatically:

```python
#!/usr/bin/env python3
"""
GitHub Issues Creation Script for NB_Streamer Backlog
Requires: pip install PyGithub
Usage: python create_issues.py
"""

from github import Github
import os

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Set your token
REPO_NAME = "your-username/NB_Streamer"  # Update with your repo
PROJECT_ID = 1  # Update with your project ID

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Epic definitions
epics = [
    {
        "title": "[EPIC] Event Streaming Core",
        "body": """## Epic Description
Implement the core event processing pipeline from Netbird JSON input to Graylog UDP/TCP output

## Success Criteria
- Receive Netbird JSON events with 100% fidelity
- Process 100+ events/second with <100ms latency per event
- Support UDP (primary) and TCP (fallback) protocols
- Graceful error handling for malformed events

## Story Point Estimate
21 points across 6 user stories
""",
        "labels": ["type/epic", "priority/critical", "area/streaming-core", "size/L"]
    },
    # Add other epics here...
]

# User Story definitions
stories = [
    {
        "title": "[STORY] Receive JSON events from Netbird",
        "body": """## User Story
As a **system administrator**, I want the service to receive JSON events from Netbird so that I can monitor VPN activities in Graylog

## Acceptance Criteria
- [ ] Accept HTTP POST requests with JSON payload
- [ ] Validate JSON structure against Netbird schema
- [ ] Return appropriate HTTP status codes

## Technical Notes
- Use FastAPI with Pydantic models
- Implement proper error handling
- Log all incoming requests

## Definition of Done
- [ ] Code implemented and tested
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
""",
        "labels": ["type/story", "priority/critical", "area/streaming-core", "size/M"],
        "epic": "Event Streaming Core"
    },
    # Add other stories here...
]

def create_issues():
    """Create Epic and Story issues in GitHub"""
    
    # Create Epics first
    epic_map = {}
    for epic in epics:
        issue = repo.create_issue(
            title=epic["title"],
            body=epic["body"],
            labels=epic["labels"]
        )
        epic_name = epic["title"].replace("[EPIC] ", "")
        epic_map[epic_name] = issue.number
        print(f"Created Epic: {issue.number} - {epic['title']}")
    
    # Create Stories and link to Epics
    for story in stories:
        body = story["body"]
        if "epic" in story:
            epic_number = epic_map.get(story["epic"])
            if epic_number:
                body += f"\n\n## Related Epic\n- Part of #{epic_number}"
        
        issue = repo.create_issue(
            title=story["title"],
            body=body,
            labels=story["labels"]
        )
        print(f"Created Story: {issue.number} - {story['title']}")

if __name__ == "__main__":
    create_issues()
```

## Milestone Configuration

### MVP Release 1.0.0
- **Due Date**: Based on 7-11 day development timeline
- **Description**: "Initial release with core event streaming functionality"
- **Issues**: All Critical and High priority items

### Post-MVP Features
- **Due Date**: TBD
- **Description**: "Documentation and enhancement features"
- **Issues**: Medium and Low priority items

## Project Automation

### GitHub Actions Workflow
Create `.github/workflows/project-board.yml`:

```yaml
name: Project Board Automation

on:
  issues:
    types: [opened, edited, closed, reopened]
  pull_request:
    types: [opened, closed, reopened]

jobs:
  update-board:
    runs-on: ubuntu-latest
    steps:
      - name: Move new issues to Ready
        if: github.event.action == 'opened'
        uses: alex-page/github-project-automation-plus@v0.8.1
        with:
          project: NB_Streamer MVP Development
          column: Ready
          repo-token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Move closed issues to Done
        if: github.event.action == 'closed'
        uses: alex-page/github-project-automation-plus@v0.8.1
        with:
          project: NB_Streamer MVP Development
          column: Done
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

## Usage Instructions

1. **Setup Repository**:
   ```bash
   # Navigate to your NB_Streamer repository
   cd NB_Streamer
   
   # Create GitHub Project Board manually via GitHub UI
   # Configure labels using GitHub UI or CLI
   ```

2. **Create Issues**:
   ```bash
   # Option 1: Manual creation using templates
   # Use the issue templates provided above
   
   # Option 2: Bulk creation with script
   export GITHUB_TOKEN="your_token_here"
   python create_issues.py
   ```

3. **Configure Project Board**:
   - Link issues to project board
   - Set up custom fields
   - Configure automation rules

4. **Daily Workflow**:
   - Move issues between columns as work progresses
   - Update story points and complexity estimates
   - Link pull requests to issues
   - Review and prioritize backlog regularly

## Best Practices

### Issue Management
- **Small Commits**: Link commits to specific issues using `Fixes #123`
- **Branch Naming**: Use `feature/123-issue-description` format
- **Pull Requests**: Reference issues in PR descriptions

### Backlog Refinement
- **Weekly Reviews**: Reassess priorities and estimates
- **Dependency Tracking**: Keep dependency links updated
- **Story Splitting**: Break down large stories (>8 points)

### Reporting
- **Burndown Charts**: Track progress against milestones
- **Velocity Tracking**: Monitor story points completed per iteration
- **Blocker Resolution**: Daily review of blocked items

This setup provides a comprehensive project management structure aligned with the product backlog, ensuring all requirements are tracked and progress is visible throughout the development process.
