# Next.js Production Generator - Reference Documentation

## Overview

Generates **complete production-grade Next.js 15 applications** with design system integration, Shadcn/ui components, Framer Motion animations, and Monaco Editor.

## Token Efficiency

- **Without Skill**: ~15,000 tokens (load Next.js docs, React docs, Tailwind docs, Framer Motion docs)
- **With Skill**: ~150 tokens (SKILL.md + result)
- **Reduction**: 99%

## Architecture

### Input Files

1. **design-system.json** (Required):
   - Color palette (primary, secondary, accent, semantic, neutral)
   - Typography system (fonts, sizes, weights, line heights)
   - Spacing scale (4px/8px grid)
   - Animation presets (durations, easings, springs)
   - Component variants (button, input, card styles)

2. **pages-structure.yaml** (Optional):
   - Page definitions and routes
   - Section layouts
   - Component composition

### Output Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with theme provider
│   ├── page.tsx                # Landing page with hero section
│   ├── globals.css             # Tailwind + design tokens
│   ├── (auth)/
│   │   ├── login/page.tsx     # Login page
│   │   └── register/page.tsx  # Register page
│   ├── dashboard/page.tsx     # Dashboard with charts
│   ├── chat/page.tsx          # AI chat interface
│   └── practice/page.tsx      # Code editor with Monaco
├── components/
│   ├── ui/                    # Shadcn/ui components (40+)
│   ├── animations/            # Framer Motion wrappers
│   └── features/              # Feature-specific components
├── lib/
│   ├── design-tokens.ts       # Generated from design-system.json
│   ├── animation-presets.ts   # Framer Motion configurations
│   └── utils.ts               # Utility functions (cn, etc.)
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript strict mode
├── tailwind.config.ts         # Generated from design system
├── postcss.config.js          # PostCSS configuration
└── next.config.js             # Next.js optimization
```

## Generated Features

### Design System Integration

- **Colors**: All colors from design-system.json imported to Tailwind config
- **Typography**: Font families, sizes, weights applied consistently
- **Spacing**: 4px/8px grid system enforced
- **Animations**: Framer Motion presets (fadeIn, slideUp, scaleIn, stagger)
- **Components**: Button, Input, Card variants with design tokens

### Performance Optimization

- **Code Splitting**: Automatic route-based splitting
- **Dynamic Imports**: Monaco Editor, Chart libraries lazy-loaded
- **Image Optimization**: Next.js Image component with WebP/AVIF
- **Font Loading**: Variable fonts with font-display: swap
- **Bundle Size**: Optimized imports for lucide-react, framer-motion

### TypeScript Configuration

- **Strict Mode**: Enabled for type safety
- **Path Aliases**: `@/*` for clean imports
- **No Any Types**: Enforced through strict mode
- **Type Checking**: Pre-commit hook ready

### Accessibility

- **Semantic HTML**: Proper heading hierarchy, landmarks
- **ARIA Labels**: All interactive elements labeled
- **Keyboard Navigation**: Tab order, focus indicators
- **Color Contrast**: 4.5:1 minimum (from design system)

## Usage Examples

### Basic Generation

```bash
python3 scripts/generate_complete_app.py \
  --design-system ../../design-system.json \
  --output frontend/
```

### With Custom Pages

```bash
# Create pages-structure.yaml
cat > pages-structure.yaml << EOF
pages:
  - name: landing
    route: /
    sections: [hero, features, testimonials, pricing]
  - name: dashboard
    route: /dashboard
    sections: [stats, progress, activity]
EOF

# Generate with custom structure
python3 scripts/generate_complete_app.py \
  --design-system ../../design-system.json \
  --pages pages-structure.yaml \
  --output frontend/
```

### Development Workflow

```bash
# 1. Generate application
python3 scripts/generate_complete_app.py \
  --design-system design-system.json \
  --output frontend/

# 2. Install dependencies
cd frontend && npm install

# 3. Start development server
npm run dev

# 4. Build for production
npm run build

# 5. Run type checking
npm run type-check
```

## Design System Requirements

### Minimum Required Sections

```json
{
  "colors": {
    "brand": { "primary": {...}, "secondary": {...}, "accent": {...} },
    "semantic": { "success": {...}, "warning": {...}, "error": {...} },
    "neutral": { "50": "...", "100": "...", ..., "950": "..." }
  },
  "typography": {
    "fontFamily": { "sans": "...", "mono": "..." },
    "fontSize": { "xs": "...", "sm": "...", ..., "9xl": "..." }
  },
  "spacing": {
    "scale": { "0": "0px", "1": "4px", ..., "64": "256px" }
  },
  "animations": {
    "durations": { "fast": 150, "normal": 300, "slow": 500 },
    "easings": { "easeIn": "...", "easeOut": "...", "spring": "..." },
    "presets": { "fadeIn": {...}, "slideUp": {...}, "scaleIn": {...} }
  }
}
```

## Customization

### Adding New Pages

1. Create page component in `app/` directory
2. Use design tokens from `lib/design-tokens.ts`
3. Apply animations from `lib/animation-presets.ts`
4. Follow existing patterns for consistency

### Adding New Components

1. Create component in `components/` directory
2. Import design tokens: `import { designTokens } from '@/lib/design-tokens'`
3. Use Framer Motion: `import { motion } from 'framer-motion'`
4. Apply animations: `import { animations } from '@/lib/animation-presets'`

### Modifying Design System

1. Update `design-system.json`
2. Regenerate application: `python3 scripts/generate_complete_app.py ...`
3. All components automatically use new tokens

## Performance Targets

- **Lighthouse Performance**: ≥95
- **First Contentful Paint**: <1.2s
- **Time to Interactive**: <3s
- **Largest Contentful Paint**: <2.5s
- **Cumulative Layout Shift**: <0.1
- **Bundle Size**: JS <250KB, CSS <50KB (gzipped)

## Troubleshooting

### Build Errors

**Issue**: TypeScript compilation errors
**Solution**: Run `npm run type-check` to see detailed errors. Ensure all imports are correct.

**Issue**: Tailwind classes not working
**Solution**: Verify `tailwind.config.ts` includes all content paths. Run `npm run dev` to regenerate.

### Runtime Errors

**Issue**: Hydration mismatch
**Solution**: Ensure client-only components use `'use client'` directive. Check for SSR-incompatible code.

**Issue**: Monaco Editor not loading
**Solution**: Verify dynamic import with `ssr: false`. Check browser console for errors.

### Performance Issues

**Issue**: Large bundle size
**Solution**: Run `npm run build` and check `.next/analyze`. Ensure dynamic imports for heavy components.

**Issue**: Slow page loads
**Solution**: Check image optimization. Ensure WebP/AVIF formats. Use `priority` prop for above-fold images.

## Integration with Other Skills

### With `fastapi-dapr-agent`

```bash
# Generate backend
python3 .claude/skills/fastapi-dapr-agent/scripts/generate_complete_agent.py triage backend/triage_agent

# Generate frontend
python3 .claude/skills/nextjs-production-gen/scripts/generate_complete_app.py \
  --design-system design-system.json \
  --output frontend/

# Frontend automatically configured to call backend at http://localhost:8000
```

### With `performance-optimizer`

```bash
# Generate application
python3 scripts/generate_complete_app.py ...

# Optimize
python3 .claude/skills/performance-optimizer/scripts/optimize.py \
  --app-path frontend/ \
  --target lighthouse-95
```

### With `accessibility-validator`

```bash
# Generate application
python3 scripts/generate_complete_app.py ...

# Validate
python3 .claude/skills/accessibility-validator/scripts/validate.py \
  --url http://localhost:3000 \
  --standard wcag22-aa
```

## Best Practices

1. **Design System First**: Create comprehensive design-system.json before generation
2. **Consistent Tokens**: Never hardcode colors, spacing, or animation values
3. **Type Safety**: Enable TypeScript strict mode, avoid `any` types
4. **Performance**: Use dynamic imports for heavy components (Monaco, Charts)
5. **Accessibility**: Test with keyboard navigation, screen readers
6. **Responsive**: Test on mobile (375px), tablet (768px), desktop (1440px)

## Limitations

- **Subjective Design**: Cannot make aesthetic decisions (color palette selection, visual hierarchy)
- **Content Creation**: Does not generate marketing copy, images, or videos
- **Custom Logic**: Complex business logic requires manual implementation
- **Third-Party APIs**: Integration with external services requires manual configuration

## Version History

- **v1.0.0** (2026-01-06): Initial release with design system integration
  - Next.js 15 with App Router
  - Shadcn/ui components
  - Framer Motion animations
  - Monaco Editor integration
  - TypeScript strict mode
  - Performance optimization
