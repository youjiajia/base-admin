module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es6: true
  },
  parserOptions: {
    parser: '@typescript-eslint/parser',
    sourceType: 'module'
  },
  plugins: ['vue', 'sort-imports-es6-autofix'],
  settings: {
    'import/resolver': {
      webpack: {
        config: 'node_modules/@vue/cli-service/webpack.config.js'
      }
    }
  },
  rules: {
    eqeqeq: 'off',
    'vue/max-attributes-per-line': [
      2,
      {
        singleline: 10,
        multiline: {
          max: 1,
          allowFirstLine: true
        }
      }
    ],
    'vue/singleline-html-element-content-newline': 'off',
    'vue/multiline-html-element-content-newline': 'off',
    'vue/html-closing-bracket-newline': 'off',
    'vue/require-component-is': 'off',
    'vue/require-default-prop': 'off',
    'vue/html-self-closing': 'off',
    'vue/name-property-casing': ['error', 'PascalCase'],
    'vue/no-v-html': 'off',
    'vue/array-bracket-spacing': 'error',
    'vue/arrow-spacing': 'error',
    'vue/block-spacing': 'error',
    'vue/brace-style': 'error',
    'vue/camelcase': 'error',
    'vue/comma-dangle': 'error',
    'vue/component-name-in-template-casing': 'error',
    'vue/eqeqeq': 'error',
    'vue/key-spacing': 'error',
    'vue/match-component-file-name': 'error',
    'vue/object-curly-spacing': 'error',
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    // 函数括号中间的空格, 匿名函数不需要,命名函数不需要,异步箭头函数需要
    'space-before-function-paren': [
      2,
      {
        anonymous: 'never',
        named: 'never',
        asyncArrow: 'always'
      }
    ],
    // 开启 import 排序检查,和自动修复
    'sort-imports-es6-autofix/sort-imports-es6': [
      2,
      {
        ignoreCase: false,
        ignoreMemberSort: false,
        memberSyntaxSortOrder: ['none', 'all', 'multiple', 'single']
      }
    ],
    // 关闭 import/order 这个和 sort-imports-es6 会冲突,
    'import/order': 0,
    // 去除注释的最大长度限制
    'max-len': [
      'error',
      {
        ignoreComments: true,
        ignoreStrings: true,
        code: 200
      }
    ],
    // 箭头函数体只有一个参数时，可以省略圆括号。其它任何情况，参数都应被圆括号括起来。该规则强制箭头函数中圆括号的使用的一致性。
    'arrow-parens': [
      0,
      'as-needed',
      {
        requireForBlockBody: true
      }
    ],
    'no-param-reassign': 0,
    // 封号结尾
    semi: 0
  },
  extends: ['eslint:recommended', 'plugin:vue/recommended', '@vue/standard', '@vue/typescript']
};
