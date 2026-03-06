import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.mjs';
mermaid.initialize({
  startOnLoad: true,
  theme: 'base',
  themeVariables: {
    primaryColor: '#e8f4f8',
    primaryTextColor: '#1a1a2e',
    primaryBorderColor: '#4a90a4',
    lineColor: '#5c6b7a',
    secondaryColor: '#f0f4f0',
    tertiaryColor: '#fff'
  },
  flowchart: { useMaxWidth: true, htmlLabels: true },
  sequence: { useMaxWidth: true }
});
