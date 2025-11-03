import { Injectable } from '@nestjs/common';
import * as crypto from 'crypto';

/**
 * Token encryption service using AES-256-GCM
 * Implements secure encryption/decryption for OAuth tokens
 */
@Injectable()
export class TokenService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly ivLength = 16;
  private readonly encryptionKey: Buffer;

  constructor() {
    const key = process.env.ENCRYPTION_KEY;
    if (!key || key.length !== 64) {
      throw new Error(
        'ENCRYPTION_KEY must be a 32-byte hex string (64 characters). Generate with: openssl rand -hex 32',
      );
    }
    this.encryptionKey = Buffer.from(key, 'hex');
  }

  /**
   * Encrypt a token using AES-256-GCM
   * @param token - Plain text token to encrypt
   * @returns JSON string containing iv, encrypted data, and auth tag
   */
  encryptToken(token: string): string {
    const iv = crypto.randomBytes(this.ivLength);
    const cipher = crypto.createCipheriv(
      this.algorithm,
      this.encryptionKey,
      iv,
    );

    let encrypted = cipher.update(token, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    return JSON.stringify({
      iv: iv.toString('hex'),
      encrypted,
      authTag: authTag.toString('hex'),
    });
  }

  /**
   * Decrypt a token using AES-256-GCM
   * @param encryptedData - JSON string from encryptToken
   * @returns Plain text token
   */
  decryptToken(encryptedData: string): string {
    const { iv, encrypted, authTag } = JSON.parse(encryptedData);

    const decipher = crypto.createDecipheriv(
      this.algorithm,
      this.encryptionKey,
      Buffer.from(iv, 'hex'),
    );

    decipher.setAuthTag(Buffer.from(authTag, 'hex'));

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  /**
   * Mask token for logging (show only first/last 4 chars)
   * @param token - Token to mask
   * @returns Masked token string
   */
  maskToken(token: string): string {
    if (!token || token.length < 12) return '***';
    return `${token.slice(0, 4)}...${token.slice(-4)}`;
  }
}
