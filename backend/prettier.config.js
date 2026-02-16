// prettier.config.js
// Prettier Configuration - Enhanced Strict Settings
export default {
  semi: false,
  singleQuote: true,
  tabWidth: 2,
  trailingComma: 'all',
  printWidth: 100,
  bracketSpacing: true,
  arrowParens: 'always',
  endOfLine: 'lf',
  proseWrap: 'never',
  overrides: [
    {
      files: '*.py',
      options: {
        tabWidth: 4,
        singleQuote: false,
        trailingComma: 'none',
        printWidth: 88
      }
    },
    {
      files: '*.md',
      options: {
        tabWidth: 2,
        singleQuote: false,
        proseWrap: 'never',
        printWidth: 100
      }
    },
    {
      files: '*.json',
      options: {
        tabWidth: 2,
        singleQuote: false,
        trailingComma: 'none'
      }
    },
    {
      files: ['*.yaml', '*.yml'],
      options: {
        tabWidth: 2,
        singleQuote: false,
        trailingComma: 'none'
      }
    },
    {
      files: '*.html',
      options: {
        tabWidth: 2,
        singleQuote: true,
        bracketSpacing: true
      }
    },
    {
      files: '*.css',
      options: {
        tabWidth: 2,
        singleQuote: true
      }
    }
  ]
}
