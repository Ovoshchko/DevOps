const createJestConfig = require('react-scripts/scripts/utils/createJestConfig')

const config = createJestConfig(
  (relativePath) => require.resolve(`react-scripts/${relativePath}`),
  __dirname,
  false,
)

module.exports = {
  ...config,
  roots: ['<rootDir>/tests'],
  testMatch: ['<rootDir>/tests/**/*.{spec,test}.{js,jsx,ts,tsx}'],
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
}
