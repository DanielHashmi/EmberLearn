# Docusaurus Deploy - Reference

## Overview

This skill deploys Docusaurus 3.0+ documentation sites, with automatic generation from codebase sources including Skills, API specs, and code documentation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Documentation Pipeline                    │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Codebase   │───▶│  Generate   │───▶│   Build     │     │
│  │   Scan      │    │    Docs     │    │  Docusaurus │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                                      │            │
│         ▼                                      ▼            │
│  ┌─────────────┐                      ┌─────────────┐      │
│  │ - Skills    │                      │   Deploy    │      │
│  │ - API specs │                      │  - Local    │      │
│  │ - Docstrings│                      │  - GitHub   │      │
│  │ - Markdown  │                      │  - K8s      │      │
│  └─────────────┘                      └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Generated Structure

```
docs-site/
├── docusaurus.config.js    # Site configuration
├── sidebars.js             # Navigation structure
├── package.json            # Dependencies
├── docs/
│   ├── intro.md            # Landing page
│   ├── getting-started/
│   │   ├── installation.md
│   │   └── quickstart.md
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── agents.md
│   │   └── infrastructure.md
│   ├── api/
│   │   ├── overview.md
│   │   └── endpoints/
│   └── skills/
│       ├── overview.md
│       └── <skill-name>.md
├── src/
│   └── css/
│       └── custom.css
├── static/
│   └── img/
└── build/                  # Generated output
```

## Configuration

### docusaurus.config.js

Key settings:
- `title`: Site title (EmberLearn)
- `tagline`: Site description
- `url`: Production URL
- `baseUrl`: Base path (usually `/`)
- `organizationName`: GitHub org
- `projectName`: Repository name

### Sidebar Configuration

```javascript
// sidebars.js
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['getting-started/installation'],
    },
  ],
  skillsSidebar: [
    'skills/overview',
    // Auto-generated skill pages
  ],
};
```

## Deployment Targets

### Local Development

```bash
./scripts/build_and_deploy.sh docs-site . local
# Opens http://localhost:3000
```

### GitHub Pages

```bash
./scripts/build_and_deploy.sh docs-site . github-pages
# Deploys to https://<org>.github.io/<repo>
```

### Kubernetes

```bash
./scripts/build_and_deploy.sh docs-site . kubernetes
# Builds Docker image and loads into Minikube
```

## Auto-Generation Features

### From Skills

Each skill in `.claude/skills/` generates a documentation page:
- Extracts description from YAML frontmatter
- Links to source files
- Documents usage instructions

### From Python Docstrings

```python
def calculate_mastery(scores: list[float]) -> float:
    """Calculate mastery score from component scores.

    Args:
        scores: List of [exercise, quiz, quality, streak] scores

    Returns:
        Weighted mastery score (0.0 to 1.0)
    """
```

### From TypeScript JSDoc

```typescript
/**
 * Execute Python code in sandbox environment.
 * @param code - Python source code to execute
 * @returns Execution result with output and timing
 */
export async function executeCode(code: string): Promise<ExecutionResult>
```

### From OpenAPI Specs

API documentation generated from `contracts/*.yaml` files.

## Customization

### Theme Colors

Edit `src/css/custom.css`:

```css
:root {
  --ifm-color-primary: #2563eb;  /* Blue */
  --ifm-color-primary-dark: #1d4ed8;
  /* ... */
}
```

### Adding Pages

1. Create markdown file in `docs/`
2. Add frontmatter with `sidebar_position`
3. Update `sidebars.js` if needed

```markdown
---
sidebar_position: 3
---

# My New Page

Content here...
```

### Custom Components

Create React components in `src/components/`:

```jsx
// src/components/MasteryBadge.jsx
export default function MasteryBadge({ level }) {
  const colors = {
    red: 'bg-red-100',
    yellow: 'bg-yellow-100',
    green: 'bg-green-100',
    blue: 'bg-blue-100',
  };
  return <span className={colors[level]}>{level}</span>;
}
```

## Troubleshooting

### Build Failures

```bash
# Clear cache
npm run clear

# Reinstall dependencies
rm -rf node_modules && npm install

# Check for broken links
npm run build -- --strict
```

### Missing Pages

1. Verify file exists in `docs/`
2. Check frontmatter syntax
3. Verify sidebar configuration

### Deployment Issues

```bash
# Check build output
ls -la docs-site/build/

# Test locally first
npm run serve

# Check Docker build
docker build -t test-docs .
docker run -p 8080:80 test-docs
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
    paths: ['docs/**', '.claude/skills/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
        working-directory: docs-site
      - run: npm run build
        working-directory: docs-site
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs-site/build
```

## Best Practices

1. **Keep docs close to code**: Update docs when code changes
2. **Use auto-generation**: Let scripts extract from docstrings
3. **Version documentation**: Tag releases with docs
4. **Test locally**: Always preview before deploying
5. **Monitor broken links**: Use `--strict` build flag
