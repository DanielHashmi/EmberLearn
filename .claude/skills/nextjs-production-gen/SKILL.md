---
name: nextjs-production-gen
description: Generate complete production-grade Next.js 15 application with design system, Shadcn/ui, Framer Motion, Monaco Editor, and responsive layouts
allowed-tools: Bash, Read, Write
model: claude-sonnet-4-20250514
---

# Next.js Production Generator

## When to Use

- User requests production-quality Next.js application
- Building frontend with design system integration
- Need consistent styling and animations across all components
- Require Monaco Editor integration with code-splitting
- Want automated performance optimization

## Instructions

1. **Verify Prerequisites**:
   ```bash
   python3 scripts/check_prereqs.py
   ```

2. **Generate Complete Application**:
   ```bash
   python3 scripts/generate_complete_app.py \
     --design-system ../../design-system.json \
     --output frontend/
   ```

3. **Verify Generation**:
   ```bash
   python3 scripts/verify_generation.py frontend/
   ```

4. **Install Dependencies**:
   ```bash
   cd frontend && npm install
   ```

5. **Validate Build**:
   ```bash
   cd frontend && npm run build
   ```

## Validation

- [ ] All files generated without errors
- [ ] Design tokens imported correctly
- [ ] TypeScript compilation succeeds
- [ ] Build completes successfully
- [ ] No console errors in development mode

## Output

- Complete Next.js 15 application with App Router
- 40+ Shadcn/ui components with custom theme
- Framer Motion animations with design system presets
- Monaco Editor with lazy loading
- Responsive layouts (5 breakpoints)
- Performance-optimized (code splitting, image optimization)

See [REFERENCE.md](./REFERENCE.md) for detailed configuration options.
