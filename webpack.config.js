// webpack.config.js
const path = require('path');

module.exports = {
  entry: './totalfootball/static/js/App.js',
  output: {
    path: path.resolve(__dirname, './totalfootball/static/js'),
    filename: 'App.bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,  // Rule for CSS files
        use: ['style-loader', 'css-loader'],  // Loads CSS into JS and injects it into the DOM
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};
