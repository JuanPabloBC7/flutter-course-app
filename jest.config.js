/** Configuración de Jest con ts-jest para TypeScript. */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  // Buscar archivos *.test.ts dentro de tests/
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  // Carga valores de entorno seguros antes de importar los módulos
  setupFiles: ['<rootDir>/tests/helpers/jest.setup.ts'],
  // Tiempo extra para pruebas de integración que tocan la base de datos
  testTimeout: 20000,
  clearMocks: true,
};
