import { Injectable, Logger } from '@nestjs/common';

/**
 * HTML Sanitizer Service
 * Sanitizes HTML content from emails to prevent XSS attacks
 * Implements security best practices for email preview
 */
@Injectable()
export class HtmlSanitizerService {
  private readonly logger = new Logger(HtmlSanitizerService.name);

  // Allowed HTML tags for email display
  private readonly ALLOWED_TAGS = new Set([
    'p',
    'br',
    'div',
    'span',
    'strong',
    'b',
    'em',
    'i',
    'u',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'ul',
    'ol',
    'li',
    'blockquote',
    'pre',
    'code',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
    'a',
    'img',
    'hr',
  ]);

  // Allowed attributes per tag
  private readonly ALLOWED_ATTRIBUTES: Record<string, Set<string>> = {
    a: new Set(['href', 'title', 'target', 'rel']),
    img: new Set(['src', 'alt', 'title', 'width', 'height']),
    table: new Set(['border', 'cellpadding', 'cellspacing']),
    td: new Set(['colspan', 'rowspan']),
    th: new Set(['colspan', 'rowspan']),
    '*': new Set(['style', 'class']), // Global attributes
  };

  // Dangerous URL protocols to block
  private readonly DANGEROUS_PROTOCOLS = [
    'javascript:',
    'data:',
    'vbscript:',
    'file:',
    'about:',
  ];

  // Allowed CSS properties (for style attribute)
  private readonly ALLOWED_CSS_PROPERTIES = new Set([
    'color',
    'background-color',
    'font-size',
    'font-weight',
    'font-family',
    'text-align',
    'text-decoration',
    'margin',
    'padding',
    'border',
    'width',
    'height',
  ]);

  /**
   * Sanitize HTML content
   * @param html - Raw HTML from email
   * @returns Sanitized HTML safe for display
   */
  sanitizeHtml(html: string): string {
    if (!html) {
      return '';
    }

    try {
      // Remove script tags and their content
      html = this.removeScriptTags(html);

      // Remove event handlers (onclick, onerror, etc.)
      html = this.removeEventHandlers(html);

      // Remove dangerous tags
      html = this.removeDangerousTags(html);

      // Sanitize URLs
      html = this.sanitizeUrls(html);

      // Sanitize style attributes
      html = this.sanitizeStyles(html);

      // Remove comments
      html = this.removeComments(html);

      return html;
    } catch (error) {
      this.logger.error(`Failed to sanitize HTML: ${error.message}`);
      return this.escapeHtml(html); // Fallback to full escape
    }
  }

  /**
   * Remove script tags and their content
   */
  private removeScriptTags(html: string): string {
    return html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  }

  /**
   * Remove inline event handlers
   */
  private removeEventHandlers(html: string): string {
    // Remove on* attributes (onclick, onerror, onload, etc.)
    return html.replace(/\son\w+\s*=\s*["'][^"']*["']/gi, '');
  }

  /**
   * Remove dangerous tags
   */
  private removeDangerousTags(html: string): string {
    const dangerousTags = [
      'script',
      'iframe',
      'object',
      'embed',
      'applet',
      'meta',
      'link',
      'style',
      'form',
      'input',
      'button',
      'textarea',
      'select',
    ];

    for (const tag of dangerousTags) {
      const regex = new RegExp(`<${tag}\\b[^<]*(?:(?!<\\/${tag}>)<[^<]*)*<\\/${tag}>`, 'gi');
      html = html.replace(regex, '');

      // Also remove self-closing versions
      const selfClosingRegex = new RegExp(`<${tag}\\b[^>]*/>`, 'gi');
      html = html.replace(selfClosingRegex, '');
    }

    return html;
  }

  /**
   * Sanitize URLs in href and src attributes
   */
  private sanitizeUrls(html: string): string {
    // Sanitize href attributes
    html = html.replace(
      /href\s*=\s*["']([^"']*)["']/gi,
      (match, url) => {
        if (this.isDangerousUrl(url)) {
          return 'href="#"';
        }
        return match;
      },
    );

    // Sanitize src attributes
    html = html.replace(
      /src\s*=\s*["']([^"']*)["']/gi,
      (match, url) => {
        if (this.isDangerousUrl(url)) {
          return 'src=""';
        }
        return match;
      },
    );

    return html;
  }

  /**
   * Check if URL uses dangerous protocol
   */
  private isDangerousUrl(url: string): boolean {
    const urlLower = url.toLowerCase().trim();

    for (const protocol of this.DANGEROUS_PROTOCOLS) {
      if (urlLower.startsWith(protocol)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Sanitize style attributes
   */
  private sanitizeStyles(html: string): string {
    return html.replace(
      /style\s*=\s*["']([^"']*)["']/gi,
      (match, styleContent) => {
        const sanitizedStyle = this.sanitizeCss(styleContent);
        if (!sanitizedStyle) {
          return '';
        }
        return `style="${sanitizedStyle}"`;
      },
    );
  }

  /**
   * Sanitize CSS content
   */
  private sanitizeCss(css: string): string {
    const rules = css.split(';').filter((rule) => rule.trim());
    const sanitizedRules: string[] = [];

    for (const rule of rules) {
      const [property, value] = rule.split(':').map((s) => s.trim());

      if (!property || !value) {
        continue;
      }

      // Check if property is allowed
      if (this.ALLOWED_CSS_PROPERTIES.has(property.toLowerCase())) {
        // Check for dangerous values
        if (!this.isDangerousCssValue(value)) {
          sanitizedRules.push(`${property}: ${value}`);
        }
      }
    }

    return sanitizedRules.join('; ');
  }

  /**
   * Check if CSS value is dangerous
   */
  private isDangerousCssValue(value: string): boolean {
    const valueLower = value.toLowerCase();

    // Block expressions and imports
    if (valueLower.includes('expression') || valueLower.includes('import')) {
      return true;
    }

    // Block javascript: and data: URLs in CSS
    if (valueLower.includes('javascript:') || valueLower.includes('data:')) {
      return true;
    }

    return false;
  }

  /**
   * Remove HTML comments
   */
  private removeComments(html: string): string {
    return html.replace(/<!--[\s\S]*?-->/g, '');
  }

  /**
   * Escape HTML entities
   * Fallback method for complete HTML escaping
   */
  private escapeHtml(html: string): string {
    return html
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /**
   * Extract plain text from HTML
   * Removes all HTML tags and returns text only
   */
  extractPlainText(html: string): string {
    if (!html) {
      return '';
    }

    // Remove script and style tags with content
    let text = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    text = text.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');

    // Replace <br> and <p> with newlines
    text = text.replace(/<br\s*\/?>/gi, '\n');
    text = text.replace(/<\/p>/gi, '\n\n');

    // Remove all other HTML tags
    text = text.replace(/<[^>]+>/g, '');

    // Decode HTML entities
    text = this.decodeHtmlEntities(text);

    // Normalize whitespace
    text = text.replace(/\n{3,}/g, '\n\n'); // Max 2 consecutive newlines
    text = text.replace(/ {2,}/g, ' '); // Collapse multiple spaces

    return text.trim();
  }

  /**
   * Decode common HTML entities
   */
  private decodeHtmlEntities(text: string): string {
    const entities: Record<string, string> = {
      '&amp;': '&',
      '&lt;': '<',
      '&gt;': '>',
      '&quot;': '"',
      '&#039;': "'",
      '&nbsp;': ' ',
      '&copy;': '©',
      '&reg;': '®',
      '&trade;': '™',
    };

    for (const [entity, char] of Object.entries(entities)) {
      text = text.replace(new RegExp(entity, 'g'), char);
    }

    return text;
  }

  /**
   * Validate if HTML is safe
   * Returns validation result with warnings
   */
  validateHtml(html: string): {
    isSafe: boolean;
    warnings: string[];
  } {
    const warnings: string[] = [];

    // Check for script tags
    if (/<script\b/i.test(html)) {
      warnings.push('Contains script tags');
    }

    // Check for event handlers
    if (/\son\w+\s*=/i.test(html)) {
      warnings.push('Contains inline event handlers');
    }

    // Check for dangerous URLs
    if (/(?:href|src)\s*=\s*["'](?:javascript:|data:)/i.test(html)) {
      warnings.push('Contains dangerous URLs');
    }

    // Check for iframe/object/embed
    if (/<(?:iframe|object|embed)\b/i.test(html)) {
      warnings.push('Contains embedded content');
    }

    return {
      isSafe: warnings.length === 0,
      warnings,
    };
  }
}
