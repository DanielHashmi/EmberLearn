#!/bin/bash
# Scaffold a new Next.js project with Monaco Editor integration

set -e

PROJECT_NAME="${1:-frontend}"
OUTPUT_DIR="${2:-.}"

echo "Scaffolding Next.js project: $PROJECT_NAME"

# Create project directory
mkdir -p "$OUTPUT_DIR/$PROJECT_NAME"
cd "$OUTPUT_DIR/$PROJECT_NAME"

# Create package.json if it doesn't exist
if [ ! -f "package.json" ]; then
    cat > package.json << 'EOF'
{
  "name": "emberlearn-frontend",
  "version": "1.0.0",
  "private": true,
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
    "@monaco-editor/react": "^4.6.0",
    "zustand": "^4.5.0",
    "swr": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^15.0.0"
  }
}
EOF
    echo "✓ Created package.json"
fi

# Create app directory structure
mkdir -p app/components app/api app/hooks app/lib app/styles public

# Create layout.tsx
cat > app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import './styles/globals.css'

export const metadata: Metadata = {
  title: 'EmberLearn - AI-Powered Python Tutoring',
  description: 'Learn Python with AI-powered tutoring and real-time code execution',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  )
}
EOF
echo "✓ Created app/layout.tsx"

# Create page.tsx
cat > app/page.tsx << 'EOF'
import CodeEditor from './components/CodeEditor'
import ChatPanel from './components/ChatPanel'
import ProgressDashboard from './components/ProgressDashboard'

export default function Home() {
  return (
    <main className="flex min-h-screen">
      {/* Left sidebar - Progress */}
      <aside className="w-64 bg-white border-r border-gray-200 p-4">
        <ProgressDashboard />
      </aside>

      {/* Main content - Code Editor */}
      <section className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-200 p-4">
          <h1 className="text-xl font-semibold text-gray-800">EmberLearn</h1>
          <p className="text-sm text-gray-500">AI-Powered Python Tutoring</p>
        </header>
        <div className="flex-1 p-4">
          <CodeEditor />
        </div>
      </section>

      {/* Right sidebar - AI Chat */}
      <aside className="w-96 bg-white border-l border-gray-200">
        <ChatPanel />
      </aside>
    </main>
  )
}
EOF
echo "✓ Created app/page.tsx"

# Create globals.css
cat > app/styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Mastery level colors */
.mastery-red { @apply bg-red-100 text-red-800 border-red-200; }
.mastery-yellow { @apply bg-yellow-100 text-yellow-800 border-yellow-200; }
.mastery-green { @apply bg-green-100 text-green-800 border-green-200; }
.mastery-blue { @apply bg-blue-100 text-blue-800 border-blue-200; }

/* Monaco editor container */
.monaco-container {
  @apply rounded-lg border border-gray-200 overflow-hidden;
  height: calc(100vh - 200px);
}
EOF
echo "✓ Created app/styles/globals.css"

echo ""
echo "✓ Next.js project scaffolded at $OUTPUT_DIR/$PROJECT_NAME"
echo ""
echo "Next steps:"
echo "  1. Run: cd $OUTPUT_DIR/$PROJECT_NAME && npm install"
echo "  2. Create Monaco Editor component"
echo "  3. Configure API routes"
