'use strict';
const path = require('path');
const root = path.join(__dirname, '../');

const VueLoaderPlugin = require('vue-loader/lib/plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const HtmlWebpackPlugin = require('html-webpack-plugin');
const siteConfig = require(path.join(root, 'src/config/config.json'));

const devServerRouteConfig = require('./dev-server-route-config');
const cssLoaderConfig = require('./css-loader-config');
const postcssLoaderConfig = require('./postcss-loader-config');
const sassLoaderConfig = require('./sass-loader-config');

module.exports = [
  {
    devtool: 'source-map',
    context: path.resolve(__dirname, '../'),
    entry: {
      index: path.join(root, 'src/index.js'),
    },
    output: {
      path: path.join(root, 'public/assets/dist'),
      filename: '[name].js',
      publicPath: '/assets/dist',
    },
    module: {
      rules: [
        {
          test: /\.vue$/,
          use: [
            {
              loader: 'vue-loader',
              options: {
                loaders: {
                  scss: [
                    'vue-style-loader',
                    cssLoaderConfig,
                    postcssLoaderConfig,
                    sassLoaderConfig,
                  ],
                }
              }
            }
          ]
        },
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: [
            {
              loader: 'babel-loader',
              options: {
                presets: ['@babel/preset-env']
              }
            },
          ]
        },
        //{
        //  test: /\.(sa|sc|c)ss$/,
        //  use: [
        //    'style-loader',
        //    cssLoaderConfig,
        //    postcssLoaderConfig,
        //    sassLoaderConfig,
        //  ],
        //},
        {
          test: /\.(sa|sc|c)ss$/,
          use: [
            MiniCssExtractPlugin.loader,
            //'style-loader',
            cssLoaderConfig,
            postcssLoaderConfig,
            sassLoaderConfig,
          ]
        }
      ]
    },
    resolve: {
      modules: [
        path.join(root, 'src'),
        'node_modules'
      ],
      extensions: ['*', '.js', '.vue', '.json'],
      alias: {
        '@': path.join(root, 'src'),
        'vue$': 'vue/dist/vue.esm.js',
        'vue-router$': 'vue-router/dist/vue-router.esm.js',
      }
    },
    plugins: [
      new VueLoaderPlugin(),
      new HtmlWebpackPlugin({
        template: path.join(root, 'src/index.html'),
        filename: '../../index.html',
        title: siteConfig.siteName,
        hash: true,
      }),
      new MiniCssExtractPlugin({
        filename: '[name].css',
      }),
    ],
    optimization: {
      splitChunks: {
        name: 'vendor',
        chunks: 'initial'
      },
    },
    //for webpack-dev-server
    devServer: {
      open: true,// Open at brower automatically
      //openPage: 'index.html',// Open this page automatically
      contentBase: path.join(root, 'public'),// RootDir for build files
      watchContentBase: true, // Watch changed forfiles under  contentBase dir
      host: 'localhost',
      port: 8080,
      before: devServerRouteConfig,
      clientLogLevel: 'debug',
    },
  },
];
