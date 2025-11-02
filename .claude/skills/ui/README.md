# UI Skill

Expert frontend UI specialist for the ProActive People Recruitment System.

## Quick Start

This skill provides comprehensive knowledge of all frontend UI elements, components, and patterns in the project.

## Contents

### SKILL.md
Main skill documentation with:
- Complete technology stack overview
- File structure and component locations
- Quick navigation guide (line numbers for all components)
- Development commands and best practices

### References

**[references/ui-catalog.md](references/ui-catalog.md)** (880 lines)
Complete catalog of all UI elements including:
- Every component with line numbers
- All dependencies and libraries
- Complete technology stack
- Gap analysis and missing features
- Comprehensive statistics

**[references/component-patterns.md](references/component-patterns.md)** (600+ lines)
Practical code examples for:
- Component extraction patterns
- State management (Zustand, Context)
- API integration (TanStack Query, Fetch)
- Styling patterns (Tailwind)
- Form handling (React Hook Form + Zod)
- Error handling
- Performance optimization
- Accessibility patterns

**[references/improvement-roadmap.md](references/improvement-roadmap.md)** (900+ lines)
Step-by-step refactoring guide:
- 8-week implementation plan
- Component extraction strategy
- Library integration guides
- Migration paths (TypeScript, testing)
- Success metrics and checklists

### Scripts

**[scripts/extract-component.js](scripts/extract-component.js)**
Automated component extraction from dashboard.jsx.

Usage:
```bash
node .claude/skills/ui/scripts/extract-component.js <component-name> <start-line> <end-line>
```

## When to Use This Skill

Use this skill when:
- Working with any UI components or pages
- Modifying styles or layouts
- Debugging frontend issues
- Implementing new features
- Refactoring component architecture
- Questions about the UI codebase

## Key Information

### Current State
- **Single-file app**: All 756 lines in dashboard.jsx
- **No TypeScript**: Plain JavaScript/JSX
- **No component library**: Custom inline components
- **State management**: React hooks only (no Redux/Zustand)
- **No testing**: Zero test infrastructure

### Technology Stack
- React 18.2.0 + Vite 5.0.8
- Tailwind CSS 3.4.0
- Lucide React (icons)
- react-markdown + remark-gfm
- Native Fetch API

### Quick Navigation (dashboard.jsx)
- Header: lines 303-339
- Connected Sources: 344-374
- Workflows Sidebar: 379-438
- Chat Interface: 442-568
- Console Panel: 571-604
- Analytics: 610-752

## Getting Started

1. Read [SKILL.md](SKILL.md) for overview
2. Check [references/ui-catalog.md](references/ui-catalog.md) for comprehensive details
3. Use [references/component-patterns.md](references/component-patterns.md) for code examples
4. Follow [references/improvement-roadmap.md](references/improvement-roadmap.md) for refactoring

## Development

```bash
cd frontend
npm start          # Start dev server on http://localhost:3000
npm run build      # Build for production
npm run preview    # Preview production build
```

## Contact

For questions about this skill, refer to the main project documentation in CLAUDE.md.
