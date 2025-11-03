import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import helmet from 'helmet';
import * as session from 'express-session';
import * as RedisStore from 'connect-redis';
import { createClient } from 'redis';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule, {
    logger: ['error', 'warn', 'log', 'debug', 'verbose'],
  });

  const configService = app.get(ConfigService);

  // Security headers
  app.use(helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'", "'unsafe-inline'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'", 'https://www.googleapis.com'],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  }));

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // Redis client for session store
  const redisClient = createClient({
    host: configService.get('REDIS_HOST'),
    port: configService.get('REDIS_PORT'),
    password: configService.get('REDIS_PASSWORD'),
  });

  await redisClient.connect();

  // Session configuration
  app.use(
    session({
      store: new (RedisStore as any)({ client: redisClient }),
      secret: configService.get('SESSION_SECRET'),
      resave: false,
      saveUninitialized: false,
      cookie: {
        secure: configService.get('NODE_ENV') === 'production',
        httpOnly: true,
        sameSite: 'lax',
        maxAge: null, // Session cookie (browser close)
      },
    }),
  );

  // CORS configuration
  app.enableCors({
    origin: configService.get('FRONTEND_URL'),
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-CSRF-Token'],
  });

  // Global prefix
  app.setGlobalPrefix('api/v1');

  // Swagger API Documentation (development only)
  if (configService.get('NODE_ENV') !== 'production') {
    const config = new DocumentBuilder()
      .setTitle('Gmail Email Search & CV Extraction API')
      .setDescription(
        'RESTful API for Gmail email search, CV extraction, and attachment management. ' +
        'Provides comprehensive email search, advanced filtering, saved searches, email preview with HTML sanitization, ' +
        'and secure attachment downloads.\n\n' +
        '## Features\n' +
        '- **Email Search (US1)**: Search with date range, sender, subject filters\n' +
        '- **Attachment Downloads (US2)**: Individual and bulk ZIP downloads\n' +
        '- **Advanced Filtering (US3)**: Domain, keyword, file type filters with saved searches\n' +
        '- **Email Preview (US4)**: Full HTML preview with XSS protection\n' +
        '- **Security**: HTML sanitization, rate limiting, session authentication\n' +
        '- **Compliance**: GDPR-compliant data handling and 24-hour retention',
      )
      .setVersion('1.0.0')
      .setContact(
        'ProActive People',
        'https://proactivepeople.com',
        'info@proactivepeople.com',
      )
      .addTag('gmail', 'Gmail email search and retrieval')
      .addTag('advanced', 'Advanced filtering and saved searches')
      .addTag('attachments', 'Attachment downloads and management')
      .addTag('auth', 'Authentication and session management')
      .addCookieAuth('gmail.sid', {
        type: 'apiKey',
        in: 'cookie',
        name: 'gmail.sid',
        description: 'Session cookie for authenticated requests',
      })
      .addServer('http://localhost:8080/api/v1', 'Development server')
      .addServer('https://api.proactivepeople.com/api/v1', 'Production server')
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup('api/docs', app, document, {
      swaggerOptions: {
        persistAuthorization: true,
        docExpansion: 'none',
        filter: true,
        showRequestDuration: true,
      },
      customSiteTitle: 'Gmail API Documentation',
    });
  }

  const port = configService.get('PORT') || 8080;
  await app.listen(port);

  console.log('='.repeat(80));
  console.log('Gmail Email Search & CV Extraction Service'.padStart(50));
  console.log('='.repeat(80));
  console.log(`🚀 Server running:        http://localhost:${port}/api/v1`);
  if (configService.get('NODE_ENV') !== 'production') {
    console.log(`📚 API Documentation:    http://localhost:${port}/api/docs`);
  }
  console.log(`🔒 Security:             Helmet, CORS, CSRF protection enabled`);
  console.log(`📝 Session Store:        Redis (${configService.get('REDIS_HOST')}:${configService.get('REDIS_PORT')})`);
  console.log(`🌍 Environment:          ${configService.get('NODE_ENV') || 'development'}`);
  console.log(`📊 Rate Limiting:        Enabled per endpoint`);
  console.log(`🛡️  GDPR Compliance:     24-hour data retention`);
  console.log('='.repeat(80));
}

bootstrap();
