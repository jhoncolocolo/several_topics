
```javascript
Aquí tienes una versión del Logger en TypeScript que incluye el tiempo de creación de cada mensaje (moment_of_call) y un mensaje personalizado (custom_message) como parte del log:

typescript
Copiar
Editar
/**
 * A Logger class for structured logging with support for log levels,
 * request/response context, and additional data. Provides formatted log outputs
 * that include timestamps and contextual information.
 */
export class Logger {
  private readonly levels: string[];
  private currentLevel: number;

  /**
   * Initializes a new Logger instance with a specified log level.
   * @param level The log level (error, warn, info, debug). Default is 'info'.
   * @throws Error if an invalid log level is provided.
   */
  constructor(level: string = 'info') {
    this.levels = ['error', 'warn', 'info', 'debug'];
    const levelIndex = this.levels.indexOf(level);
    if (levelIndex === -1) {
      throw new Error(`Invalid log level: ${level}`);
    }
    this.currentLevel = levelIndex;
  }

  /**
   * Logs a message with a specific log level, context type, and additional data.
   * @param level The log level (error, warn, info, debug).
   * @param message The main log message.
   * @param type The log context type (REQUEST or RESPONSE).
   * @param additionalData Optional additional data for context.
   */
  private log(
    level: string,
    message: string,
    type: 'REQUEST' | 'RESPONSE',
    additionalData: string = ''
  ): void {
    const levelIndex = this.levels.indexOf(level);
    if (levelIndex <= this.currentLevel) {
      const momentOfCall = new Date().toISOString();
      const logMessage = `["${momentOfCall}"] -[${type}] - [${level.toUpperCase()}] - ${JSON.stringify({
        message,
        ...(additionalData && { additional_data: additionalData }),
      })}`;
      console.log(logMessage);
    }
  }

  /**
   * Logs a message for a request context.
   * @param message The main log message.
   * @param level The log level (error, warn, info, debug).
   * @param additionalData Optional additional data for context.
   */
  public request(message: string, level: string, additionalData: string = ''): void {
    this.log(level, message, 'REQUEST', additionalData);
  }

  /**
   * Logs a message for a response context.
   * @param message The main log message.
   * @param level The log level (error, warn, info, debug).
   * @param additionalData Optional additional data for context.
   */
  public response(message: string, level: string, additionalData: string = ''): void {
    this.log(level, message, 'RESPONSE', additionalData);
  }

  /**
   * Logs an error message with a specific context.
   * @param message The error message to log.
   * @param additionalData Optional additional data for context.
   * @param type The log context type (REQUEST or RESPONSE). Default is REQUEST.
   */
  public error(message: string, additionalData: string = '', type: 'REQUEST' | 'RESPONSE' = 'REQUEST'): void {
    this.log('error', message, type, additionalData);
  }

  /**
   * Logs a warning message with a specific context.
   * @param message The warning message to log.
   * @param additionalData Optional additional data for context.
   * @param type The log context type (REQUEST or RESPONSE). Default is REQUEST.
   */
  public warn(message: string, additionalData: string = '', type: 'REQUEST' | 'RESPONSE' = 'REQUEST'): void {
    this.log('warn', message, type, additionalData);
  }

  /**
   * Logs an informational message with a specific context.
   * @param message The informational message to log.
   * @param additionalData Optional additional data for context.
   * @param type The log context type (REQUEST or RESPONSE). Default is REQUEST.
   */
  public info(message: string, additionalData: string = '', type: 'REQUEST' | 'RESPONSE' = 'REQUEST'): void {
    this.log('info', message, type, additionalData);
  }

  /**
   * Logs a debug message with a specific context.
   * @param message The debug message to log.
   * @param additionalData Optional additional data for context.
   * @param type The log context type (REQUEST or RESPONSE). Default is REQUEST.
   */
  public debug(message: string, additionalData: string = '', type: 'REQUEST' | 'RESPONSE' = 'REQUEST'): void {
    this.log('debug', message, type, additionalData);
  }
}

```
plaintext
Copiar
Editar
[ERROR] {"time":"2025-01-23T10:00:00.000Z","message":"This is an error message","custom_message":"Additional context for the error"}
[WARN] {"time":"2025-01-23T10:00:01.000Z","message":"This is a warning","custom_message":"Custom warning info"}
[INFO] {"time":"2025-01-23T10:00:02.000Z","message":"Info message","custom_message":"More details about the info message"}
[DEBUG] {"time":"2025-01-23T10:00:03.000Z","message":"Debug message","custom_message":"Debugging context"}
