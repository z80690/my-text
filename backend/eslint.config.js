// eslint-disable-next-line import/no-unresolved
import tseslint from 'typescript-eslint'
import js from '@eslint/js'
import globals from 'globals'
import pluginImport from 'eslint-plugin-import'
import pluginJsdoc from 'eslint-plugin-jsdoc'

export default [
  {
    ignores: [
      'node_modules/',
      'dist/',
      'build/',
      '*.pyc',
      '__pycache__/',
      '.env',
      '*.md',
      'logs/',
      '*.log'
    ]
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.js', '**/*.mjs', '**/*.cjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.node,
        console: 'readonly',
        module: 'readonly',
        require: 'readonly',
        process: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        Buffer: 'readonly',
        setTimeout: 'readonly',
        setInterval: 'readonly',
        clearTimeout: 'readonly',
        clearInterval: 'readonly',
        global: 'readonly'
      }
    },
    plugins: {
      import: pluginImport,
      jsdoc: pluginJsdoc
    },
    settings: {
      'import/resolver': {
        node: {
          extensions: ['.js', '.mjs', '.cjs', 'ts', '.tsx', '.json']
        }
      }
    },
    rules: {
      ...pluginImport.configs.recommended.rules,
      ...pluginJsdoc.configs.recommended.rules,
      semi: ['error', 'never'],
      quotes: ['error', 'single'],
      indent: ['error', 2],
      'no-unused-vars': [
        'error',
        { args: 'all', argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
      ],
      'no-console': 'warn',
      'no-debugger': 'error',
      eqeqeq: ['error', 'always'],
      'no-trailing-spaces': 'error',
      'comma-dangle': ['error', 'never'],
      'arrow-parens': ['error', 'always'],
      'no-eval': 'error',
      'no-implicit-globals': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-template': 'error',
      'no-mixed-spaces-and-tabs': 'error',
      'import/no-unresolved': 'error',
      'import/named': 'error',
      'import/default': 'error',
      'import/export': 'error',
      'jsdoc/require-jsdoc': ['warn', { publicOnly: true }],
      'jsdoc/check-alignment': 'error',
      'jsdoc/check-examples': 'off',
      'jsdoc/check-param-names': 'error',
      'jsdoc/check-tag-names': 'error',
      'jsdoc/check-types': 'error',
      'jsdoc/empty-tags': 'warn',
      'jsdoc/implements-on-classes': 'error',
      'jsdoc/match-description': 'off',
      'jsdoc/no-bad-blocks': 'error',
      'jsdoc/no-defaults': 'off',
      'jsdoc/no-multi-asterisks': 'error',
      'jsdoc/require-returns': 'warn',
      'jsdoc/require-throws': 'warn',
      'jsdoc/valid-types': 'error',

      // 新增严格规则
      'no-else-return': 'error',
      'no-lonely-if': 'error',
      'no-useless-return': 'error',
      'no-duplicate-imports': 'error',
      'no-await-in-loop': 'warn',
      'prefer-destructuring': ['error', { object: true, array: false }],
      'max-len': ['warn', { code: 100, comments: 120, ignoreUrls: true }],
      'max-depth': ['warn', 4],
      'max-params': ['warn', 5],
      'no-magic-numbers': ['warn', { ignore: [-1, 0, 1, 2, 4, 5, 15] }],
      complexity: ['warn', 15],
      'one-var': ['error', 'never'],
      'operator-linebreak': ['error', 'after'],
      'no-whitespace-before-property': 'error',
      'no-multi-spaces': ['error', { ignoreEOLComments: true }],
      'func-call-spacing': ['error', 'never'],
      'key-spacing': ['error', { beforeColon: false, afterColon: true }],
      'space-infix-ops': 'error',
      'space-unary-ops': ['error', { words: true, nonwords: false }],
      'spaced-comment': ['error', 'always'],
      'switch-colon-spacing': 'error',
      'array-bracket-spacing': ['error', 'never'],
      'object-curly-spacing': ['error', 'always'],
      'computed-property-spacing': ['error', 'never'],
      'template-curly-spacing': ['error', 'never'],
      'yield-star-spacing': ['error', 'both']
    }
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: tseslint.parser,
      parserOptions: {
        project: './tsconfig.json'
      }
    },
    plugins: {
      import: pluginImport,
      jsdoc: pluginJsdoc,
      '@typescript-eslint': tseslint.plugin
    },
    settings: {
      'import/resolver': {
        node: {
          extensions: ['.js', '.mjs', '.cjs', 'ts', '.tsx', '.json']
        }
      }
    },
    rules: {
      ...pluginImport.configs.recommended.rules,
      ...pluginJsdoc.configs.recommended.rules,
      semi: ['error', 'never'],
      quotes: ['error', 'single'],
      indent: ['error', 2],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'error',
        { args: 'all', argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
      ],
      '@typescript-eslint/consistent-type-imports': 'error',
      '@typescript-eslint/no-namespace': 'error',
      '@typescript-eslint/no-empty-interface': 'warn',
      '@typescript-eslint/explicit-function-return-type': ['warn', { allowExpressions: true }],
      'no-console': 'warn',
      'no-debugger': 'error',
      eqeqeq: ['error', 'always'],
      'no-trailing-spaces': 'error',
      'comma-dangle': ['error', 'never'],
      'arrow-parens': ['error', 'always'],
      'no-eval': 'error',
      'no-implicit-globals': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      'prefer-template': 'error',
      'no-mixed-spaces-and-tabs': 'error',
      'import/no-unresolved': 'off',
      'import/named': 'error',
      'import/default': 'error',
      'import/export': 'error',
      'jsdoc/require-jsdoc': ['warn', { publicOnly: true }],
      'jsdoc/check-alignment': 'error',
      'jsdoc/check-examples': 'off',
      'jsdoc/check-param-names': 'error',
      'jsdoc/check-tag-names': 'error',
      'jsdoc/check-types': 'error',
      'jsdoc/empty-tags': 'warn',
      'jsdoc/implements-on-classes': 'error',
      'jsdoc/match-description': 'off',
      'jsdoc/no-bad-blocks': 'error',
      'jsdoc/no-defaults': 'off',
      'jsdoc/no-multi-asterisks': 'error',
      'jsdoc/require-returns': 'warn',
      'jsdoc/require-throws': 'warn',
      'jsdoc/valid-types': 'error',

      // 新增严格规则
      'no-else-return': 'error',
      'no-lonely-if': 'error',
      'no-useless-return': 'error',
      'no-duplicate-imports': 'error',
      'no-await-in-loop': 'warn',
      'prefer-destructuring': ['error', { object: true, array: false }],
      'max-len': ['warn', { code: 100, comments: 120, ignoreUrls: true }],
      'max-depth': ['warn', 4],
      'max-params': ['warn', 5],
      'no-magic-numbers': ['warn', { ignore: [-1, 0, 1, 2, 4, 5, 15] }],
      complexity: ['warn', 15],
      'one-var': ['error', 'never'],
      'operator-linebreak': ['error', 'after'],
      'no-whitespace-before-property': 'error',
      'no-multi-spaces': ['error', { ignoreEOLComments: true }],
      'func-call-spacing': ['error', 'never'],
      'key-spacing': ['error', { beforeColon: false, afterColon: true }],
      'space-infix-ops': 'error',
      'space-unary-ops': ['error', { words: true, nonwords: false }],
      'spaced-comment': ['error', 'always'],
      'switch-colon-spacing': 'error',
      'array-bracket-spacing': ['error', 'never'],
      'object-curly-spacing': ['error', 'always'],
      'computed-property-spacing': ['error', 'never'],
      'template-curly-spacing': ['error', 'never'],
      'yield-star-spacing': ['error', 'both'],

      // TypeScript 增强规则
      ...tseslint.configs.recommended.rules,
      '@typescript-eslint/no-floating-promises': 'warn',
      '@typescript-eslint/no-misused-promises': 'warn',
      '@typescript-eslint/await-thenable': 'error',
      '@typescript-eslint/no-for-in-array': 'error',
      '@typescript-eslint/no-unnecessary-type-assertion': 'warn',
      '@typescript-eslint/no-unnecessary-condition': 'warn',
      '@typescript-eslint/prefer-readonly': 'warn',
      '@typescript-eslint/array-type': ['error', { default: 'array-simple' }],
      '@typescript-eslint/consistent-indexed-object-style': 'error',
      '@typescript-eslint/no-require-imports': 'error',
      '@typescript-eslint/ban-ts-comment': ['error', { 'ts-ignore': 'allow-with-description' }],
      '@typescript-eslint/explicit-module-boundary-types': [
        'warn',
        { allowArgumentsExplicitlyTypedAsAny: false }
      ]
    }
  }
]
