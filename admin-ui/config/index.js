const ProxyAgent = require('proxy-agent');
// proxy lists
const serverList = {
  gcp: 'http://login.dev.igirlimg.com',
  test: 'http://47.100.247.92:9010'
};

// First Step check yard args, ex:yarn serve --env=test01 --module=module(part of code serve)
const rawArgv = process.argv.slice(2);
const args = require('minimist')(rawArgv);

const proxyTable = {};

// validate args
let errorMsg = '';
let serverTarget = 'test'; // default test serve

if (Reflect.has(args, 'env')) {
  const serverEnv = args.env;
  if (!Reflect.ownKeys(serverList).includes(serverEnv)) {
    errorMsg = '[INFO], 启动参数env不存在，请检查';
  }
  if (errorMsg) {
    console.log(errorMsg);
    process.exit(1);
  }
  serverTarget = serverEnv;
}

const isLocal = Reflect.has(args, 'local');
const isProxy = Reflect.has(args, 'proxy');

// Second Step check proxy
const proxyRules = [
  {
    target: isLocal ? (args.local === true ? 'http://localhost:8800' : args.local) : '',
    url: process.env.VUE_APP_BASE_API,
    pathRewrite: {
      [`^${process.env.VUE_APP_BASE_API}`]: ''
    }
  },
  {
    target: isLocal ? 'http://localhost:8800' : '',
    url: '/api'
  }
];
// const proxyRules = ['/ajax'];

// provide args to http-proxy-middleware
// use args.ip ,if exist
const proxyTarget = args.ip ? `http://${args.ip}:${args.port || '80'}` : serverList[serverTarget];

if (process.env.NODE_ENV !== 'production') {
  console.log(`Proxy Target => ${proxyTarget}`);
}
proxyRules.forEach(item => {
  proxyTable[item.url] = {
    target: proxyTarget,
    changeOrigin: true,
    secure: false,
    ws: false // need close
  };
  // rewrite
  if (item.pathRewrite) {
    proxyTable[item.url].pathRewrite = item.pathRewrite;
  }
  // target
  if (item.target) {
    proxyTable[item.url].target = item.target;
  }
  // proxy for socks5
  if (isProxy) {
    proxyTable[item.url].agent = new ProxyAgent('socks5://127.0.0.1:1086');
  }
});

// 导出的配置
module.exports = {
  dev: {
    host: '0.0.0.0',
    port: '8080',
    autoOpenBrowser: true,
    proxyTable,
    historyApiFallback: true,
    publicPathDev: '/',
    useEslint: true
  },
  prod: {
    productionSourceMap: false,
    publicPathProd: '/'
  }
};
