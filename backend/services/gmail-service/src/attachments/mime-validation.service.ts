import { Injectable, Logger, BadRequestException } from '@nestjs/common';
import { fileTypeFromBuffer } from 'file-type';
import * as path from 'path';

/**
 * MIME Type Validation Service
 * Detects and validates file types for security
 * Implements FR-009: MIME type validation
 */
@Injectable()
export class MimeValidationService {
  private readonly logger = new Logger(MimeValidationService.name);

  // Allowed MIME types for CV attachments
  private readonly ALLOWED_MIME_TYPES = [
    // PDF
    'application/pdf',

    // Microsoft Word
    'application/msword', // .doc
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx

    // Rich Text Format
    'application/rtf',
    'text/rtf',

    // Plain text
    'text/plain',

    // OpenDocument
    'application/vnd.oasis.opendocument.text', // .odt
  ];

  // File extensions mapped to MIME types (fallback detection)
  private readonly EXTENSION_MIME_MAP: Record<string, string> = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.rtf': 'application/rtf',
    '.txt': 'text/plain',
    '.odt': 'application/vnd.oasis.opendocument.text',
  };

  /**
   * Detect MIME type from file buffer
   * Uses file-type library for magic number detection
   * @param buffer - File buffer
   * @param filename - Original filename (fallback)
   * @returns Detected MIME type
   */
  async detectMimeType(buffer: Buffer, filename: string): Promise<string> {
    try {
      // Try to detect from file content (magic numbers)
      const fileType = await fileTypeFromBuffer(buffer);

      if (fileType?.mime) {
        this.logger.debug(
          `Detected MIME type from buffer: ${fileType.mime} for file ${filename}`,
        );
        return fileType.mime;
      }

      // Fallback: detect from file extension
      const ext = path.extname(filename).toLowerCase();
      const mimeFromExtension = this.EXTENSION_MIME_MAP[ext];

      if (mimeFromExtension) {
        this.logger.debug(
          `Detected MIME type from extension: ${mimeFromExtension} for file ${filename}`,
        );
        return mimeFromExtension;
      }

      // Default to octet-stream if detection fails
      this.logger.warn(
        `Could not detect MIME type for ${filename}, defaulting to application/octet-stream`,
      );
      return 'application/octet-stream';
    } catch (error) {
      this.logger.error(
        `Error detecting MIME type for ${filename}: ${error.message}`,
      );
      return 'application/octet-stream';
    }
  }

  /**
   * Validate MIME type against whitelist
   * Implements FR-009: Only allow safe document types
   * @param mimeType - MIME type to validate
   * @throws BadRequestException if MIME type not allowed
   */
  async validateMimeType(mimeType: string): Promise<void> {
    if (!this.ALLOWED_MIME_TYPES.includes(mimeType)) {
      this.logger.warn(`Rejected file with MIME type: ${mimeType}`);

      throw new BadRequestException(
        `File type not allowed. Only document formats are permitted: ` +
          `PDF, Word (DOC/DOCX), RTF, TXT, ODT`,
      );
    }

    this.logger.debug(`Validated MIME type: ${mimeType}`);
  }

  /**
   * Check if MIME type is allowed
   * @param mimeType - MIME type to check
   * @returns True if allowed
   */
  isAllowedMimeType(mimeType: string): boolean {
    return this.ALLOWED_MIME_TYPES.includes(mimeType);
  }

  /**
   * Get human-readable file type description
   * @param mimeType - MIME type
   * @returns Human-readable description
   */
  getFileTypeDescription(mimeType: string): string {
    const descriptions: Record<string, string> = {
      'application/pdf': 'PDF Document',
      'application/msword': 'Microsoft Word Document (DOC)',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        'Microsoft Word Document (DOCX)',
      'application/rtf': 'Rich Text Format',
      'text/rtf': 'Rich Text Format',
      'text/plain': 'Plain Text Document',
      'application/vnd.oasis.opendocument.text': 'OpenDocument Text',
      'application/octet-stream': 'Unknown File Type',
    };

    return descriptions[mimeType] || 'Unknown File Type';
  }

  /**
   * Get file extension for MIME type
   * @param mimeType - MIME type
   * @returns Suggested file extension
   */
  getExtensionForMimeType(mimeType: string): string {
    const extensions: Record<string, string> = {
      'application/pdf': '.pdf',
      'application/msword': '.doc',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        '.docx',
      'application/rtf': '.rtf',
      'text/rtf': '.rtf',
      'text/plain': '.txt',
      'application/vnd.oasis.opendocument.text': '.odt',
    };

    return extensions[mimeType] || '';
  }

  /**
   * Validate filename for security
   * Prevents path traversal and dangerous filenames
   * @param filename - Original filename
   * @returns Sanitized filename
   */
  sanitizeFilename(filename: string): string {
    // Remove path traversal attempts
    let sanitized = filename.replace(/\.\./g, '');

    // Remove leading/trailing spaces
    sanitized = sanitized.trim();

    // Remove special characters that could cause issues
    sanitized = sanitized.replace(/[<>:"|?*]/g, '');

    // Remove leading dots (hidden files)
    sanitized = sanitized.replace(/^\.+/, '');

    // Ensure filename is not empty
    if (!sanitized) {
      sanitized = 'attachment';
    }

    // Limit filename length
    if (sanitized.length > 255) {
      const ext = path.extname(sanitized);
      const nameWithoutExt = path.basename(sanitized, ext);
      sanitized = nameWithoutExt.slice(0, 255 - ext.length) + ext;
    }

    return sanitized;
  }

  /**
   * Check if file is likely malicious based on content
   * Basic heuristics for detecting suspicious files
   * @param buffer - File buffer
   * @param mimeType - Detected MIME type
   * @returns True if file appears suspicious
   */
  async isSuspiciousFile(buffer: Buffer, mimeType: string): Promise<boolean> {
    // Check for executable signatures (MZ header for Windows PE files)
    if (buffer.length >= 2) {
      const header = buffer.toString('ascii', 0, 2);
      if (header === 'MZ') {
        this.logger.warn('Detected executable file (PE format)');
        return true;
      }
    }

    // Check for ELF header (Linux executables)
    if (buffer.length >= 4) {
      const elfHeader = buffer.toString('hex', 0, 4);
      if (elfHeader === '7f454c46') {
        this.logger.warn('Detected ELF executable');
        return true;
      }
    }

    // Check for script files that might be dangerous
    const dangerousMimeTypes = [
      'application/x-executable',
      'application/x-sh',
      'application/x-shellscript',
      'text/x-sh',
      'text/x-python',
      'text/javascript',
      'application/javascript',
    ];

    if (dangerousMimeTypes.includes(mimeType)) {
      this.logger.warn(`Detected potentially dangerous MIME type: ${mimeType}`);
      return true;
    }

    return false;
  }

  /**
   * Get list of allowed MIME types
   * @returns Array of allowed MIME types
   */
  getAllowedMimeTypes(): string[] {
    return [...this.ALLOWED_MIME_TYPES];
  }

  /**
   * Get list of allowed file extensions
   * @returns Array of allowed file extensions
   */
  getAllowedExtensions(): string[] {
    return Object.keys(this.EXTENSION_MIME_MAP);
  }
}
