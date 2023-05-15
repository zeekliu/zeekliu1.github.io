var { mathjax } = require('mathjax-full/js/mathjax');
var { TeX } = require('mathjax-full/js/input/tex');
var { SVG } = require('mathjax-full/js/output/svg');
var { LiteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor');
var { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html');
var { AllPackages } = require('mathjax-full/js/input/tex/AllPackages');

// MathJax bootstrap
const adaptor = new LiteAdaptor();
RegisterHTMLHandler(adaptor);

const html = mathjax.document('', {
  InputJax: new TeX({ packages: AllPackages }),
  OutputJax: new SVG({ fontCache: 'none' }),
});

function tex2svg(equation, isInline, color, alternateColor) {
  const svg = adaptor
    .innerHTML(html.convert(equation, { display: !isInline }))
    .replace(
      /(?<=<svg.+?>)/,
      `
<style>
  * {
    fill: ${color || "black"};
  }
  @media (prefers-color-scheme: dark) {
    * {
      fill: ${alternateColor || color || "black"};
    }
  }
</style>`
    );
  if (svg.includes('merror')) {
    return svg.replace(/<rect.+?><\/rect>/, '');
  }
  return svg;
}

module.exports = tex2svg;
