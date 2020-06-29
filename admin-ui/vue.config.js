/* eslint-disable no-sequences */
const path = require('path');
const defaultSettings = require('./src/settings.ts');
const config = require('./config');

const { historyApiFallback, host, port, proxyTable, autoOpenBrowser, publicPathDev, useEslint } = config.dev;
const { publicPathProd } = config.prod;
const isDev = process.env.NODE_ENV === 'development';
// webpack module types
const types = ['vue-modules', 'vue', 'normal-modules', 'normal'];

function resolve(dir) {
  return path.join(__dirname, dir);
}

const name = defaultSettings.title || 'vue Admin Template'; // page title

module.exports = {
  publicPath: isDev ? publicPathDev : publicPathProd,
  outputDir: 'dist',
  assetsDir: 'static',
  lintOnSave: isDev,
  productionSourceMap: false,
  devServer: {
    host: host || '127.0.0.1',
    port: port || '9527',
    open: autoOpenBrowser,
    historyApiFallback,
    overlay: {
      warnings: false,
      errors: true
    },
    proxy: proxyTable
    // after: require('./mock/mock-server.js'),
  },
  configureWebpack: {
    // provide the app's title in webpack's name field, so that
    // it can be accessed in index.html to inject the correct title.
    name
  },
  pluginOptions: {
    'style-resources-loader': {
      preProcessor: 'scss',
      patterns: [
        path.resolve(__dirname, 'src/styles/_variables.scss'),
        path.resolve(__dirname, 'src/styles/_mixins.scss')
      ]
    }
  },
  chainWebpack(config) {
    // Provide the app's title in webpack's name field, so that
    // it can be accessed in index.html to inject the correct title.
    // resolve dir alias
    config.resolve.modules
      .add(resolve('src'))
      .end()
      .alias.set('@', resolve('src'))
      .set('_c', resolve('src/components'));

    // delete elsint
    if (!useEslint) config.module.rules.delete('eslint');

    config.plugins.delete('preload'); // TODO: need test
    config.plugins.delete('prefetch'); // TODO: need test

    // set svg-sprite-loader
    config.module
      .rule('svg')
      .exclude.add(resolve('src/icons'))
      .end();
    config.module
      .rule('icons')
      .test(/\.svg$/)
      .include.add(resolve('src/icons'))
      .end()
      .use('svg-sprite-loader')
      .loader('svg-sprite-loader')
      .options({
        symbolId: 'icon-[name]'
      })
      .end();

    // set preserveWhitespace
    config.module
      .rule('vue')
      .use('vue-loader')
      .loader('vue-loader')
      .tap(options => {
        options.compilerOptions.preserveWhitespace = true;
        return options;
      })
      .end();

    // https://webpack.js.org/configuration/devtool/#development
    // eslint-disable-next-line no-unused-expressions
    config.when(isDev), config => config.devtool('cheap-source-map');

    config.when(!isDev, config => {
      config
        .plugin('ScriptExtHtmlWebpackPlugin')
        .after('html')
        .use('script-ext-html-webpack-plugin', [
          {
            // `runtime` must same as runtimeChunk name. default is `runtime`
            inline: /runtime\..*\.js$/
          }
        ])
        .end();
      config.optimization.splitChunks({
        chunks: 'all',
        cacheGroups: {
          libs: {
            name: 'chunk-libs',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
            chunks: 'initial' // only package third parties that are initially dependent
          },
          elementUI: {
            name: 'chunk-elementUI', // split elementUI into a single package
            priority: 20, // the weight needs to be larger than libs and app or it will be packaged into libs or app
            test: /[\\/]node_modules[\\/]_?element-ui(.*)/ // in order to adapt to cnpm
          },
          commons: {
            name: 'chunk-commons',
            test: resolve('src/components'), // can customize your rules
            minChunks: 3, //  minimum common number
            priority: 5,
            reuseExistingChunk: true
          }
        }
      });
      config.optimization.runtimeChunk('single');
    });
  }
};
