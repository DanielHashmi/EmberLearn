// @ts-check

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'EmberLearn',
  tagline: 'AI-Powered Python Tutoring Platform',
  favicon: 'img/favicon.ico',

  url: 'https://emberlearn.dev',
  baseUrl: '/',

  organizationName: 'emberlearn',
  projectName: 'emberlearn',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/emberlearn/emberlearn/tree/main/docs/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'EmberLearn',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            href: 'https://github.com/emberlearn/emberlearn',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Getting Started', to: '/docs/intro' },
              { label: 'Architecture', to: '/docs/architecture' },
              { label: 'Skills Guide', to: '/docs/skills-guide' },
            ],
          },
          {
            title: 'More',
            items: [
              { label: 'API Reference', to: '/docs/api-reference' },
              { label: 'Evaluation', to: '/docs/evaluation' },
              { label: 'GitHub', href: 'https://github.com/emberlearn/emberlearn' },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} EmberLearn. Built for Hackathon III.`,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
        additionalLanguages: ['python', 'bash', 'yaml'],
      },
    }),
};

module.exports = config;
