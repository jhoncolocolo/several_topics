
```javascript
1. logger/Logger.ts
Clase para la bitácora estructurada.

typescript
Copiar
Editar
export class Logger {
  private readonly levels: string[];
  private readonly currentLevel: number;

  constructor(level: string = 'info') {
    this.levels = ['error', 'warn', 'info', 'debug'];
    const levelIndex = this.levels.indexOf(level);
    if (levelIndex === -1) {
      throw new Error(`Invalid log level: ${level}`);
    }
    this.currentLevel = levelIndex;
  }

  private log(
    level: string,
    message: string,
    type: 'REQUEST' | 'RESPONSE',
    additionalData: string = ''
  ): void {
    const levelIndex = this.levels.indexOf(level);
    if (levelIndex <= this.currentLevel) {
      const timestamp = new Date().toISOString();
      const logMessage = `["${timestamp}"] -[${type}] - [${level.toUpperCase()}] - ${JSON.stringify({
        message,
        ...(additionalData && { additional_data: additionalData }),
      })}`;
      console.log(logMessage);
    }
  }

  public request(message: string, level: string, additionalData: string = ''): void {
    this.log(level, message, 'REQUEST', additionalData);
  }

  public response(message: string, level: string, additionalData: string = ''): void {
    this.log(level, message, 'RESPONSE', additionalData);
  }
}
2. services/generateSeed.ts
Servicio para generar una semilla aleatoria.

typescript
Copiar
Editar
import crypto from 'crypto';

export const generateSeed = (): string => {
  const byteSize = 120;
  const randomBytes = crypto.randomBytes(byteSize);
  return randomBytes.toString('base64');
};
3. handler.ts
Archivo principal que implementa el handler.

typescript
Copiar
Editar
import crypto from 'crypto';
import { generateSeed } from './services/generateSeed';
import { Logger } from './logger/Logger';

const logger = new Logger();

export const handler = async (event: { transactionId?: string }) => {
  let transactionId = event.transactionId || null;

  logger.request(JSON.stringify({ transactionId }), 'info');

  if (!transactionId) {
    transactionId = crypto.randomUUID();
  }

  const seed = generateSeed();

  logger.response(
    JSON.stringify({
      seed: '**CONFIDENTIAL**',
      transactionId,
    }),
    'info'
  );

  return { seed, transactionId };
};
4. tests/handler.test.ts
Pruebas unitarias para handler.ts.

typescript
Copiar
Editar
import { handler } from '../handler';

describe('Handler Tests', () => {
  it('should log request and response correctly when transactionId is provided', async () => {
    const event = { transactionId: '12345' };
    const response = await handler(event);

    expect(response).toHaveProperty('seed');
    expect(response.transactionId).toBe('12345');
  });

  it('should generate a new transactionId if none is provided', async () => {
    const event = {};
    const response = await handler(event);

    expect(response).toHaveProperty('seed');
    expect(response.transactionId).toBeDefined();
  });
});
5. tests/Logger.test.ts
Pruebas unitarias para Logger.ts.

typescript
Copiar
Editar
import { Logger } from '../logger/Logger';

describe('Logger Tests', () => {
  const mockConsole = jest.spyOn(console, 'log').mockImplementation();

  afterEach(() => {
    mockConsole.mockClear();
  });

  it('should log request messages', () => {
    const logger = new Logger('info');
    logger.request('Test request', 'info', 'additional data');

    expect(mockConsole).toHaveBeenCalledTimes(1);
    expect(mockConsole.mock.calls[0][0]).toContain('Test request');
  });

  it('should not log messages below the log level', () => {
    const logger = new Logger('warn');
    logger.request('This should not log', 'info');

    expect(mockConsole).not.toHaveBeenCalled();
  });

  it('should throw error for invalid log levels', () => {
    expect(() => new Logger('invalid')).toThrow('Invalid log level: invalid');
  });
});
6. package.json
Configuración del proyecto.

json
Copiar
Editar
{
  "name": "lambda-ts-logger",
  "version": "1.0.0",
  "description": "AWS Lambda example with structured logging and TypeScript",
  "main": "handler.ts",
  "scripts": {
    "test": "jest",
    "build": "tsc"
  },
  "dependencies": {
    "crypto": "^1.0.1"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "ts-jest": "^29.0.0",
    "typescript": "^4.0.0"
  }
}
7. tsconfig.json
Configuración de TypeScript.

json
Copiar
Editar
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "outDir": "dist"
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
8. jest.config.js
Configuración de Jest para TypeScript.

javascript
Copiar
Editar
export default {
  preset: 'ts-jest',
  testEnvironment: 'node',
  verbose: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
};
9. .gitignore
Archivos a ignorar por Git.

Copiar
Editar
node_modules/
dist/
coverage/
10. README.md
Archivo de documentación.

markdown
Copiar
Editar
# Lambda TypeScript Logger

Este proyecto es un ejemplo de AWS Lambda implementado con TypeScript y pruebas unitarias en Jest.

## Estructura del Proyecto
- `logger/`: Contiene la clase `Logger` para bitácoras estructuradas.
- `services/`: Contiene el servicio `generateSeed`.
- `tests/`: Pruebas unitarias.
- `handler.ts`: Código principal del Lambda.

## Instalación
1. Instala las dependencias:
   ```bash
   npm install
Compila el proyecto:

bash
Copiar
Editar
npm run build
Ejecuta las pruebas:

bash
Copiar
Editar
npm test
yaml
Copiar
Editar

---

¡Con esta estructura tienes un proyecto bien organizado y listo para usar en TypeScript! 🚀
```
