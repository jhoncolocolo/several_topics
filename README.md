
```javascript
Aquí tienes una versión del Logger en TypeScript que incluye el tiempo de creación de cada mensaje (moment_of_call) y un mensaje personalizado (custom_message) como parte del log:

typescript
Copiar
Editar
export class Logger {
  private levels: string[];
  private currentLevel: number;

  constructor(level: string = 'info') {
    this.levels = ['error', 'warn', 'info', 'debug'];
    const levelIndex = this.levels.indexOf(level);
    if (levelIndex === -1) {
      throw new Error(`Invalid log level: ${level}`);
    }
    this.currentLevel = levelIndex;
  }

  private log(level: string, message: string, customMessage: string = ''): void {
    const levelIndex = this.levels.indexOf(level);
    if (levelIndex <= this.currentLevel) {
      const momentOfCall = new Date().toISOString();
      const logObject = {
        time: momentOfCall,
        message: message,
        custom_message: customMessage,
      };
      console.log(`[${level.toUpperCase()}]`, JSON.stringify(logObject));
    }
  }

  public error(message: string, customMessage: string = ''): void {
    this.log('error', message, customMessage);
  }

  public warn(message: string, customMessage: string = ''): void {
    this.log('warn', message, customMessage);
  }

  public info(message: string, customMessage: string = ''): void {
    this.log('info', message, customMessage);
  }

  public debug(message: string, customMessage: string = ''): void {
    this.log('debug', message, customMessage);
  }
}

// Usage
const logger = new Logger('info');

logger.error('This is an error message', 'Additional context for the error'); 
logger.warn('This is a warning', 'Custom warning info');        
logger.info('Info message', 'More details about the info message');             
logger.debug('Debug message', 'Debugging context'); 
Cambios realizados:
Nuevo parámetro customMessage:

Se agregó como argumento opcional en el método log y en los métodos públicos (error, warn, info, debug).
Este mensaje permite incluir detalles adicionales al mensaje principal.
Objeto de log estructurado:

Cada mensaje de log se imprime como un objeto JSON con tres propiedades:
time: Contiene el tiempo en que se genera el mensaje (moment_of_call).
message: El mensaje principal del log.
custom_message: Mensaje adicional, opcional.
Formato de salida:

Se utiliza JSON.stringify para estructurar el objeto de log y mantener un formato legible y consistente en la consola.
Ejemplo de salida:
Si ejecutas el código, la salida se verá como:
```
plaintext
Copiar
Editar
[ERROR] {"time":"2025-01-23T10:00:00.000Z","message":"This is an error message","custom_message":"Additional context for the error"}
[WARN] {"time":"2025-01-23T10:00:01.000Z","message":"This is a warning","custom_message":"Custom warning info"}
[INFO] {"time":"2025-01-23T10:00:02.000Z","message":"Info message","custom_message":"More details about the info message"}
[DEBUG] {"time":"2025-01-23T10:00:03.000Z","message":"Debug message","custom_message":"Debugging context"}
