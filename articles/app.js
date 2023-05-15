var express = require('express');
var helmet = require('helmet');
var bodyParser = require('body-parser');
var tex2svg = require('./adaptor');

var app = express();

app.use(helmet());
app.use(bodyParser.urlencoded({ extended: false }));

app.get("/math", async function (req, res, next) {
  const mode = (Object.keys(req.query).includes("from") || Object.keys(req.query).includes("block")) 
    ? "block"
    : Object.keys(req.query).includes("inline")
    ? "inline"
    : null;
  if (!mode) {
    return next();
  }
  const isInline = mode === "inline";
  const equation = isInline
    ? (req.query.inline)
    : (req.query.from || req.query.block);
  if (!equation || equation.match(/\.ico$/)) {
    return next();
  }

  const color = req.query.color;
  const alternateColor = req.query.alternateColor;
  if (
    (color && /[^a-zA-Z0-9#]/.test(color)) ||
    (alternateColor && /[^a-zA-Z0-9#]/.test(alternateColor))
  ) {
    return next();
  }

  const normalizedEquation = equation.replace(/\.(svg|png)$/, "");

  try {
    const svgString = tex2svg(
      normalizedEquation,
      isInline,
      color,
      alternateColor
    );
    // ont month
    res.setHeader("Cache-Control", "public, max-age=2592000");
    res.contentType("image/svg+xml");
    res.write(`<?xml version="1.0" standalone="no" ?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
`);

    res.end(svgString);
  } catch (err) {
    res.status(500);
    res.write(
      '<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="15" font-size="15">'
    );
    res.write(err);
    res.end("</text></svg>");
  }
});

module.exports = app;
