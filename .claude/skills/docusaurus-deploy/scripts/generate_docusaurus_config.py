#!/usr/bin/env python3
"""Generate Docusaurus configuration for EmberLearn documentation."""

import argparse
from pathlib import Path


DOCUSAURUS_CONFIG = '''// @ts-check
const {{ themes: {{ prismThemes }} }} = require('prism-react-renderer');

/** @type {{import('@docusaurus/types').Config}} */
const config = {{
  title: '{title}',
  tagline: '{tagline}',
  favicon: 'img/favicon.ico',
  url: '{url}',
  baseUrl: '/',
  organizationName: '{org}',
  projectName: '{project}',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {{
    defaultLocale: 'en',
    locales: ['en'],
  }},

  presets: [
    [
      'classic',
      /** @type {{import('@docusaurus/preset-classic').Options}} */
      ({{
        docs: {{
          sidebarPath: './sidebars.js',
          editUrl: '{repo_url}/edit/main/',
        }},
        blog: false,
        theme: {{
          customCss: './src/css/custom.css',
        }},
      }}),
    ],
  ],

  themeConfig:
    /** @type {{import('@docusaurus/preset-classic').ThemeConfig}} */
    ({{
      navbar: {{
        title: '{title}',
        logo: {{
          alt: '{title} Logo',
          src: 'img/logo.svg',
        }},
        items: [
          {{
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          }},
          {{
            type: 'docSidebar',
            sidebarId: 'apiSidebar',
            position: 'left',
            label: 'API Reference',
          }},
          {{
            type: 'docSidebar',
            sidebarId: 'skillsSidebar',
            position: 'left',
            label: 'Skills',
          }},
          {{
            href: '{repo_url}',
            label: 'GitHub',
            position: 'right',
          }},
        ],
      }},
      footer: {{
        style: 'dark',
        links: [
          {{
            title: 'Docs',
            items: [
              {{ label: 'Getting Started', to: '/docs/intro' }},
              {{ label: 'Architecture', to: '/docs/architecture' }},
              {{ label: 'Skills', to: '/docs/skills' }},
            ],
          }},
          {{
            title: 'Community',
            items: [
              {{ label: 'GitHub', href: '{repo_url}' }},
            ],
          }},
        ],
        copyright: `Copyright © ${{new Date().getFullYear()}} {title}. Built with Docusaurus.`,
      }},
      prism: {{
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'yaml'],
      }},
    }}),
}};

module.exports = config;
'''


SIDEBARS_CONFIG = '''/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['getting-started/installation', 'getting-started/quickstart'],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: ['architecture/overview', 'architecture/agents', 'architecture/infrastructure'],
    },
  ],
  apiSidebar: [
    'api/overview',
    {
      type: 'category',
      label: 'Endpoints',
      items: ['api/query', 'api/execute', 'api/progress'],
    },
  ],
  skillsSidebar: [
    'skills/overview',
    {
      type: 'category',
      label: 'Available Skills',
      items: [
        'skills/agents-md-gen',
        'skills/kafka-k8s-setup',
        'skills/postgres-k8s-setup',
        'skills/fastapi-dapr-agent',
        'skills/mcp-code-execution',
        'skills/nextjs-k8s-deploy',
        'skills/docusaurus-deploy',
      ],
    },
  ],
};

module.exports = sidebars;
'''


PACKAGE_JSON = '''{
  "name": "emberlearn-docs",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "docusaurus": "docusaurus",
    "start": "docusaurus start",
    "build": "docusaurus build",
    "swizzle": "docusaurus swizzle",
    "deploy": "docusaurus deploy",
    "clear": "docusaurus clear",
    "serve": "docusaurus serve"
  },
  "dependencies": {
    "@docusaurus/core": "^3.0.0",
    "@docusaurus/preset-classic": "^3.0.0",
    "@mdx-js/react": "^3.0.0",
    "clsx": "^2.0.0",
    "prism-react-renderer": "^2.3.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@docusaurus/module-type-aliases": "^3.0.0",
    "@docusaurus/types": "^3.0.0"
  },
  "browserslist": {
    "production": [">0.5%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  },
  "engines": {
    "node": ">=18.0"
  }
}
'''


def generate_config(
    output_dir: Path,
    title: str,
    tagline: str,
    url: str,
    org: str,
    project: str,
    repo_url: str,
) -> None:
    """Generate Docusaurus configuration files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate docusaurus.config.js
    config = DOCUSAURUS_CONFIG.format(
        title=title,
        tagline=tagline,
        url=url,
        org=org,
        project=project,
        repo_url=repo_url,
    )
    (output_dir / "docusaurus.config.js").write_text(config)
    print(f"✓ Created {output_dir}/docusaurus.config.js")

    # Generate sidebars.js
    (output_dir / "sidebars.js").write_text(SIDEBARS_CONFIG)
    print(f"✓ Created {output_dir}/sidebars.js")

    # Generate package.json
    (output_dir / "package.json").write_text(PACKAGE_JSON)
    print(f"✓ Created {output_dir}/package.json")

    # Create directory structure
    (output_dir / "docs").mkdir(exist_ok=True)
    (output_dir / "src" / "css").mkdir(parents=True, exist_ok=True)
    (output_dir / "static" / "img").mkdir(parents=True, exist_ok=True)

    # Create custom.css
    custom_css = '''
:root {
  --ifm-color-primary: #2563eb;
  --ifm-color-primary-dark: #1d4ed8;
  --ifm-color-primary-darker: #1e40af;
  --ifm-color-primary-darkest: #1e3a8a;
  --ifm-color-primary-light: #3b82f6;
  --ifm-color-primary-lighter: #60a5fa;
  --ifm-color-primary-lightest: #93c5fd;
  --ifm-code-font-size: 95%;
}

[data-theme='dark'] {
  --ifm-color-primary: #60a5fa;
}
'''
    (output_dir / "src" / "css" / "custom.css").write_text(custom_css)
    print(f"✓ Created {output_dir}/src/css/custom.css")

    print(f"\n✓ Docusaurus configuration generated at {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate Docusaurus config")
    parser.add_argument("--output", "-o", type=Path, default=Path("docs-site"),
                        help="Output directory")
    parser.add_argument("--title", default="EmberLearn", help="Site title")
    parser.add_argument("--tagline", default="AI-Powered Python Tutoring Platform",
                        help="Site tagline")
    parser.add_argument("--url", default="https://emberlearn.dev", help="Site URL")
    parser.add_argument("--org", default="emberlearn", help="GitHub organization")
    parser.add_argument("--project", default="emberlearn", help="Project name")
    parser.add_argument("--repo-url", default="https://github.com/emberlearn/emberlearn",
                        help="Repository URL")
    args = parser.parse_args()

    generate_config(
        args.output,
        args.title,
        args.tagline,
        args.url,
        args.org,
        args.project,
        args.repo_url,
    )


if __name__ == "__main__":
    main()
