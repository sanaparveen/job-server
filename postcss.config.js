/* eslint-disable import/no-extraneous-dependencies */
const path = require("path");

module.exports = ({ env }) => ({
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    cssnano:
      env === "production"
        ? {
            preset: [
              "default",
              {
                colormin: false,
                discardComments: { removeAll: true },
              },
            ],
          }
        : false,
    "postcss-url":
      env !== "production"
        ? {
            url: "inline",
            basePath: path.resolve("assets/src/styles"),
          }
        : false,
  },
});
