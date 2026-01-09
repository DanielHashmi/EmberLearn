#!/usr/bin/env python3
"""
Generate complete production-grade Next.js 15 application with design system.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def load_design_system(path: str) -> Dict[str, Any]:
    """Load and parse design system JSON."""
    with open(path, 'r') as f:
        return json.load(f)

def generate_package_json(output_dir: Path) -> None:
    """Generate package.json with all required dependencies."""
    package_json = {
        "name": "emberlearn-frontend",
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "type-check": "tsc --noEmit"
        },
        "dependencies": {
            "next": "^15.0.0",
            "react": "^18.3.0",
            "react-dom": "^18.3.0",
            "framer-motion": "^11.0.0",
            "@radix-ui/react-slot": "^1.0.2",
            "@radix-ui/react-dialog": "^1.0.5",
            "@radix-ui/react-dropdown-menu": "^2.0.6",
            "@radix-ui/react-select": "^2.0.0",
            "@radix-ui/react-toast": "^1.1.5",
            "@radix-ui/react-tooltip": "^1.0.7",
            "class-variance-authority": "^0.7.0",
            "clsx": "^2.1.0",
            "tailwind-merge": "^2.2.0",
            "lucide-react": "^0.344.0",
            "zod": "^3.22.4",
            "@monaco-editor/react": "^4.6.0"
        },
        "devDependencies": {
            "@types/node": "^20.11.0",
            "@types/react": "^18.2.48",
            "@types/react-dom": "^18.2.18",
            "typescript": "^5.3.3",
            "tailwindcss": "^3.4.1",
            "postcss": "^8.4.33",
            "autoprefixer": "^10.4.17",
            "eslint": "^8.56.0",
            "eslint-config-next": "^15.0.0"
        }
    }

    output_path = output_dir / "package.json"
    with open(output_path, 'w') as f:
        json.dump(package_json, f, indent=2)
    print(f"✓ Generated: {output_path}")

def generate_tailwind_config(output_dir: Path, design_system: Dict) -> None:
    """Generate tailwind.config.ts from design system."""
    colors = design_system['colors']

    config = f"""import type {{ Config }} from "tailwindcss";

const config: Config = {{
  darkMode: ["class"],
  content: [
    "./pages/**/*.{{ts,tsx}}",
    "./components/**/*.{{ts,tsx}}",
    "./app/**/*.{{ts,tsx}}",
    "./src/**/*.{{ts,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: {json.dumps(colors['brand']['primary'], indent=10)},
        secondary: {json.dumps(colors['brand']['secondary'], indent=10)},
        accent: {json.dumps(colors['brand']['accent'], indent=10)},
        neutral: {json.dumps(colors['neutral'], indent=10)},
        success: {{
          DEFAULT: "{colors['semantic']['success']['light']}",
          dark: "{colors['semantic']['success']['dark']}",
        }},
        warning: {{
          DEFAULT: "{colors['semantic']['warning']['light']}",
          dark: "{colors['semantic']['warning']['dark']}",
        }},
        error: {{
          DEFAULT: "{colors['semantic']['error']['light']}",
          dark: "{colors['semantic']['error']['dark']}",
        }},
      }},
      fontFamily: {{
        sans: {json.dumps(design_system['typography']['fontFamily']['sans'].split(', '))},
        mono: {json.dumps(design_system['typography']['fontFamily']['mono'].split(', '))},
      }},
      fontSize: {json.dumps(design_system['typography']['fontSize'], indent=8)},
      spacing: {json.dumps(design_system['spacing']['scale'], indent=8)},
      borderRadius: {json.dumps(design_system['borderRadius'], indent=8)},
      boxShadow: {json.dumps(design_system['shadows'], indent=8)},
    }},
  }},
  plugins: [],
}};

export default config;
"""

    output_path = output_dir / "tailwind.config.ts"
    with open(output_path, 'w') as f:
        f.write(config)
    print(f"✓ Generated: {output_path}")

def generate_globals_css(output_dir: Path) -> None:
    """Generate global CSS with Tailwind directives."""
    css = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.9%;
  }

  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
  }

  * {
    @apply border-neutral-200;
  }

  body {
    @apply bg-white text-neutral-900 dark:bg-neutral-950 dark:text-neutral-50;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
"""

    app_dir = output_dir / "app"
    app_dir.mkdir(parents=True, exist_ok=True)

    output_path = app_dir / "globals.css"
    with open(output_path, 'w') as f:
        f.write(css)
    print(f"✓ Generated: {output_path}")

def generate_root_layout(output_dir: Path) -> None:
    """Generate root layout with theme provider."""
    layout = """import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "EmberLearn - AI-Powered Python Tutoring",
  description: "Learn Python programming through conversational AI agents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.variable}>{children}</body>
    </html>
  );
}
"""

    app_dir = output_dir / "app"
    output_path = app_dir / "layout.tsx"
    with open(output_path, 'w') as f:
        f.write(layout)
    print(f"✓ Generated: {output_path}")

def generate_landing_page(output_dir: Path) -> None:
    """Generate landing page with hero section."""
    page = """'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <motion.section
        className="py-20 px-4 md:py-32 md:px-8 bg-gradient-to-br from-primary-50 to-secondary-50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 300, damping: 28 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-neutral-900">
              Learn Python with
              <span className="text-primary-600"> AI Tutors</span>
            </h1>

            <p className="text-xl md:text-2xl mb-8 text-neutral-600 max-w-3xl mx-auto">
              Master Python programming through personalized AI-powered tutoring,
              interactive coding exercises, and real-time feedback.
            </p>

            <motion.div
              className="flex gap-4 justify-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Link
                href="/register"
                className="px-8 py-4 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors shadow-lg hover:shadow-xl"
              >
                Get Started Free
              </Link>

              <Link
                href="/chat"
                className="px-8 py-4 bg-white text-neutral-900 rounded-xl font-semibold hover:bg-neutral-100 transition-colors shadow-lg"
              >
                Try Demo
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      {/* Features Section */}
      <section className="py-20 px-4 md:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12 text-neutral-900">
            Why Choose EmberLearn?
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2 text-neutral-900">
                  {feature.title}
                </h3>
                <p className="text-neutral-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

const features = [
  {
    icon: "🤖",
    title: "AI-Powered Tutoring",
    description: "Get personalized explanations and guidance from specialized AI agents trained in Python programming."
  },
  {
    icon: "💻",
    title: "Interactive Coding",
    description: "Write and run Python code directly in your browser with our integrated code editor."
  },
  {
    icon: "📊",
    title: "Track Progress",
    description: "Monitor your learning journey with detailed progress tracking and mastery scores."
  },
]
"""

    app_dir = output_dir / "app"
    output_path = app_dir / "page.tsx"
    with open(output_path, 'w') as f:
        f.write(page)
    print(f"✓ Generated: {output_path}")

def generate_design_tokens_lib(output_dir: Path, design_system: Dict) -> None:
    """Generate design tokens TypeScript file."""
    tokens = f"""/**
 * Design tokens generated from design-system.json
 * DO NOT EDIT MANUALLY - Regenerate using nextjs-production-gen Skill
 */

export const designTokens = {{
  colors: {json.dumps(design_system['colors'], indent=4)},
  typography: {json.dumps(design_system['typography'], indent=4)},
  spacing: {json.dumps(design_system['spacing'], indent=4)},
  borderRadius: {json.dumps(design_system['borderRadius'], indent=4)},
  shadows: {json.dumps(design_system['shadows'], indent=4)},
}} as const;

export type DesignTokens = typeof designTokens;
"""

    lib_dir = output_dir / "lib"
    lib_dir.mkdir(parents=True, exist_ok=True)

    output_path = lib_dir / "design-tokens.ts"
    with open(output_path, 'w') as f:
        f.write(tokens)
    print(f"✓ Generated: {output_path}")

def generate_animation_presets(output_dir: Path, design_system: Dict) -> None:
    """Generate Framer Motion animation presets."""
    presets = f"""/**
 * Framer Motion animation presets from design system
 * DO NOT EDIT MANUALLY - Regenerate using nextjs-production-gen Skill
 */

export const animations = {json.dumps(design_system['animations']['presets'], indent=2)};

export const springs = {json.dumps(design_system['animations']['springs'], indent=2)};

export const durations = {json.dumps(design_system['animations']['durations'], indent=2)};

export const easings = {json.dumps(design_system['animations']['easings'], indent=2)};
"""

    lib_dir = output_dir / "lib"
    output_path = lib_dir / "animation-presets.ts"
    with open(output_path, 'w') as f:
        f.write(presets)
    print(f"✓ Generated: {output_path}")

def generate_utils(output_dir: Path) -> None:
    """Generate utility functions."""
    utils = """import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
"""

    lib_dir = output_dir / "lib"
    output_path = lib_dir / "utils.ts"
    with open(output_path, 'w') as f:
        f.write(utils)
    print(f"✓ Generated: {output_path}")

def generate_tsconfig(output_dir: Path) -> None:
    """Generate TypeScript configuration."""
    tsconfig = {
        "compilerOptions": {
            "target": "ES2017",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {
                "@/*": ["./*"]
            }
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"]
    }

    output_path = output_dir / "tsconfig.json"
    with open(output_path, 'w') as f:
        json.dump(tsconfig, f, indent=2)
    print(f"✓ Generated: {output_path}")

def generate_postcss_config(output_dir: Path) -> None:
    """Generate PostCSS configuration."""
    config = """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

    output_path = output_dir / "postcss.config.js"
    with open(output_path, 'w') as f:
        f.write(config)
    print(f"✓ Generated: {output_path}")

def generate_next_config(output_dir: Path) -> None:
    """Generate Next.js configuration."""
    config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizePackageImports: ['lucide-react', 'framer-motion'],
  },
}

module.exports = nextConfig
"""

    output_path = output_dir / "next.config.js"
    with open(output_path, 'w') as f:
        f.write(config)
    print(f"✓ Generated: {output_path}")

def main():
    """Main generation function."""
    if len(sys.argv) < 3:
        print("Usage: python3 generate_complete_app.py --design-system <path> --output <dir>")
        sys.exit(1)

    # Parse arguments
    design_system_path = None
    output_dir = None

    for i, arg in enumerate(sys.argv):
        if arg == "--design-system" and i + 1 < len(sys.argv):
            design_system_path = sys.argv[i + 1]
        elif arg == "--output" and i + 1 < len(sys.argv):
            output_dir = Path(sys.argv[i + 1])

    if not design_system_path or not output_dir:
        print("Error: Missing required arguments")
        sys.exit(1)

    print(f"Loading design system from: {design_system_path}")
    design_system = load_design_system(design_system_path)

    print(f"\nGenerating Next.js application in: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate all files
    print("\nGenerating configuration files...")
    generate_package_json(output_dir)
    generate_tsconfig(output_dir)
    generate_tailwind_config(output_dir, design_system)
    generate_postcss_config(output_dir)
    generate_next_config(output_dir)

    print("\nGenerating application structure...")
    generate_globals_css(output_dir)
    generate_root_layout(output_dir)
    generate_landing_page(output_dir)

    print("\nGenerating library files...")
    generate_design_tokens_lib(output_dir, design_system)
    generate_animation_presets(output_dir, design_system)
    generate_utils(output_dir)

    print("\n" + "="*60)
    print("✓ Generation complete!")
    print(f"\nNext steps:")
    print(f"  cd {output_dir}")
    print(f"  npm install")
    print(f"  npm run dev")
    print("="*60)

if __name__ == "__main__":
    main()
