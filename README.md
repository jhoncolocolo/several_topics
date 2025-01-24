
```javascript
generateSeed.js
javascript
Copiar
Editar
import crypto from 'crypto';

export const generateSeed = () => {
  const byteSize = 120;
  const randomBytes = crypto.randomBytes(byteSize);
  return randomBytes.toString('base64');
};
Logger.js
Incluye la clase Logger que ya proporcionaste. No es necesario modificarla.

handler.js
Integra la clase Logger y añade las bitácoras:

javascript
Copiar
Editar
import crypto from 'crypto';
import { generateSeed } from './generateSeed.js';
import { Logger } from './Logger.js';

const logger = new Logger('info');

export const handler = async (event) => {
  let transactionId = event?.transactionId || null;

  // Log para la solicitud
  const requestMessage = JSON.stringify({ transactionId });
  logger.request(requestMessage, 'info');

  // Generación de la semilla
  if (!transactionId) {
    transactionId = crypto.randomUUID();
  }
  const seed = generateSeed();

  // Log para la respuesta
  const responseMessage = JSON.stringify({
    seed: '**CONFIDENTIAL**',
    transactionId,
  });
  logger.response(responseMessage, 'info');

  return {
    seed,
    transactionId,
  };
};
Pruebas unitarias
tests/Logger.test.js
Pruebas para la clase Logger:

javascript
Copiar
Editar
import { Logger } from '../src/Logger.js';

describe('Logger', () => {
  let logger;
  let consoleSpy;

  beforeEach(() => {
    logger = new Logger('info');
    consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  it('should log a request message', () => {
    logger.request('Request log message', 'info', '{"data":"value"}');
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Request log message'));
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('"additional_data":"{\\"data\\":\\"value\\"}"'));
  });

  it('should log a response message', () => {
    logger.response('Response log message', 'info', '{"status":"ok"}');
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('Response log message'));
    expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('"additional_data":"{\\"status\\":\\"ok\\"}"'));
  });

  it('should not log a debug message if the level is info', () => {
    logger.debug('Debug log message');
    expect(consoleSpy).not.toHaveBeenCalled();
  });
});
tests/handler.test.js
Pruebas para el manejador, incluyendo la validación de las bitácoras:

javascript
Copiar
Editar
import crypto from 'crypto';
import { handler } from '../src/handler.js';
import { generateSeed } from '../src/generateSeed.js';
import { Logger } from '../src/Logger.js';

jest.mock('../src/generateSeed.js', () => ({
  generateSeed: jest.fn(() => 'mockedSeed'),
}));

jest.mock('../src/Logger.js', () => {
  const mockLogger = {
    request: jest.fn(),
    response: jest.fn(),
  };
  return { Logger: jest.fn(() => mockLogger) };
});

describe('handler', () => {
  let loggerMock;

  beforeEach(() => {
    loggerMock = new Logger();
  });

  it('should log request and response correctly when transactionId is provided', async () => {
    const event = { transactionId: 'existing-id' };
    const result = await handler(event);

    expect(loggerMock.request).toHaveBeenCalledWith(
      '{"transactionId":"existing-id"}',
      'info'
    );

    expect(loggerMock.response).toHaveBeenCalledWith(
      '{"seed":"**CONFIDENTIAL**","transactionId":"existing-id"}',
      'info'
    );

    expect(result).toEqual({
      seed: 'mockedSeed',
      transactionId: 'existing-id',
    });
  });

  it('should log request and response correctly when transactionId is not provided', async () => {
    jest.spyOn(crypto, 'randomUUID').mockReturnValue('generated-id');
    const event = {};
    const result = await handler(event);

    expect(loggerMock.request).toHaveBeenCalledWith(
      '{"transactionId":null}',
      'info'
    );

    expect(loggerMock.response).toHaveBeenCalledWith(
      '{"seed":"**CONFIDENTIAL**","transactionId":"generated-id"}',
      'info'
    );

    expect(result).toEqual({
      seed: 'mockedSeed',
      transactionId: 'generated-id',
    });

    crypto.randomUUID.mockRestore();
  });
});
```
