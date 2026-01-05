/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Architecture',
      items: ['architecture', 'api-reference'],
    },
    {
      type: 'category',
      label: 'Skills',
      items: ['skills-guide'],
    },
    'evaluation',
  ],
};

module.exports = sidebars;
