var path = require('path');

module.exports = {
  entry: './src/index.js',
  output:{
    path: path.join(__dirname, '/static/js'), // <- change last argument
    filename: 'bundle.js',
    publicPath: '/static/js'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        // exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.css$/i,
        use: ['style-loader', 'css-loader'],
      }
    ]
  },
  externals: {
    'react': 'React'
  }
};
