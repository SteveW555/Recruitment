import { Test, TestingModule } from '@nestjs/testing';
import { HtmlSanitizerService } from './html-sanitizer.service';

describe('HtmlSanitizerService', () => {
  let service: HtmlSanitizerService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [HtmlSanitizerService],
    }).compile();

    service = module.get<HtmlSanitizerService>(HtmlSanitizerService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  // =============================================================================
  // XSS Attack Prevention Tests
  // =============================================================================

  describe('XSS Prevention', () => {
    it('should remove script tags', () => {
      const html = '<div>Hello</div><script>alert("XSS")</script><p>World</p>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('alert');
      expect(sanitized).toContain('Hello');
      expect(sanitized).toContain('World');
    });

    it('should remove inline event handlers', () => {
      const html = '<div onclick="alert(\'XSS\')">Click me</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('onclick');
      expect(sanitized).not.toContain('alert');
      expect(sanitized).toContain('Click me');
    });

    it('should remove javascript: URLs in href', () => {
      const html = '<a href="javascript:alert(\'XSS\')">Click</a>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('javascript:');
      expect(sanitized).toContain('href="#"');
    });

    it('should remove javascript: URLs in src', () => {
      const html = '<img src="javascript:alert(\'XSS\')" />';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('javascript:');
      expect(sanitized).toContain('src=""');
    });

    it('should remove data: URLs', () => {
      const html = '<a href="data:text/html,<script>alert(\'XSS\')</script>">Click</a>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('data:');
      expect(sanitized).toContain('href="#"');
    });

    it('should remove multiple event handlers', () => {
      const html = '<div onmouseover="alert(1)" onerror="alert(2)" onload="alert(3)">Test</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('onmouseover');
      expect(sanitized).not.toContain('onerror');
      expect(sanitized).not.toContain('onload');
    });

    it('should remove nested script tags', () => {
      const html = '<div><p><script>alert("XSS")</script></p></div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('alert');
    });
  });

  // =============================================================================
  // Dangerous Tag Removal Tests
  // =============================================================================

  describe('Dangerous Tag Removal', () => {
    it('should remove iframe tags', () => {
      const html = '<iframe src="https://evil.com"></iframe>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<iframe');
      expect(sanitized).not.toContain('evil.com');
    });

    it('should remove object tags', () => {
      const html = '<object data="https://evil.com"></object>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<object');
    });

    it('should remove embed tags', () => {
      const html = '<embed src="https://evil.com" />';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<embed');
    });

    it('should remove form tags', () => {
      const html = '<form action="/submit"><input name="data" /></form>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<form');
      expect(sanitized).not.toContain('<input');
    });

    it('should remove style tags', () => {
      const html = '<style>body { background: red; }</style>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<style>');
    });

    it('should remove meta tags', () => {
      const html = '<meta http-equiv="refresh" content="0;url=https://evil.com" />';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<meta');
    });
  });

  // =============================================================================
  // CSS Sanitization Tests
  // =============================================================================

  describe('CSS Sanitization', () => {
    it('should allow safe CSS properties', () => {
      const html = '<div style="color: blue; font-size: 14px;">Text</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('color: blue');
      expect(sanitized).toContain('font-size: 14px');
    });

    it('should remove CSS expressions', () => {
      const html = '<div style="width: expression(alert(\'XSS\'));">Text</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('expression');
      expect(sanitized).not.toContain('alert');
    });

    it('should remove CSS import statements', () => {
      const html = '<div style="background: url(\'javascript:alert(1)\');">Text</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('javascript:');
    });

    it('should remove dangerous CSS properties', () => {
      const html = '<div style="position: fixed; top: 0; left: 0; z-index: 9999;">Overlay</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('position');
      expect(sanitized).not.toContain('z-index');
    });

    it('should sanitize multiple style rules', () => {
      const html = '<div style="color: blue; expression(alert(1)); font-size: 14px;">Text</div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('color: blue');
      expect(sanitized).toContain('font-size: 14px');
      expect(sanitized).not.toContain('expression');
    });
  });

  // =============================================================================
  // Safe Content Preservation Tests
  // =============================================================================

  describe('Safe Content Preservation', () => {
    it('should preserve safe HTML structure', () => {
      const html = '<div><p>Paragraph</p><strong>Bold</strong><em>Italic</em></div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('<div>');
      expect(sanitized).toContain('<p>');
      expect(sanitized).toContain('<strong>');
      expect(sanitized).toContain('<em>');
      expect(sanitized).toContain('Paragraph');
      expect(sanitized).toContain('Bold');
      expect(sanitized).toContain('Italic');
    });

    it('should preserve safe links', () => {
      const html = '<a href="https://example.com" title="Example">Link</a>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('<a');
      expect(sanitized).toContain('href="https://example.com"');
      expect(sanitized).toContain('title="Example"');
      expect(sanitized).toContain('Link');
    });

    it('should preserve safe images', () => {
      const html = '<img src="https://example.com/image.jpg" alt="Image" />';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('<img');
      expect(sanitized).toContain('src="https://example.com/image.jpg"');
      expect(sanitized).toContain('alt="Image"');
    });

    it('should preserve tables', () => {
      const html = '<table><tr><th>Header</th></tr><tr><td>Cell</td></tr></table>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('<table>');
      expect(sanitized).toContain('<tr>');
      expect(sanitized).toContain('<th>');
      expect(sanitized).toContain('<td>');
      expect(sanitized).toContain('Header');
      expect(sanitized).toContain('Cell');
    });

    it('should preserve lists', () => {
      const html = '<ul><li>Item 1</li><li>Item 2</li></ul>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('<ul>');
      expect(sanitized).toContain('<li>');
      expect(sanitized).toContain('Item 1');
      expect(sanitized).toContain('Item 2');
    });
  });

  // =============================================================================
  // Comment Removal Tests
  // =============================================================================

  describe('Comment Removal', () => {
    it('should remove HTML comments', () => {
      const html = '<div><!-- This is a comment --><p>Text</p></div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<!--');
      expect(sanitized).not.toContain('This is a comment');
      expect(sanitized).toContain('<p>Text</p>');
    });

    it('should remove conditional comments', () => {
      const html = '<!--[if IE]><script>alert("XSS")</script><![endif]-->';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('<!--');
      expect(sanitized).not.toContain('<script>');
    });
  });

  // =============================================================================
  // Plain Text Extraction Tests
  // =============================================================================

  describe('extractPlainText', () => {
    it('should extract plain text from HTML', () => {
      const html = '<div><p>Hello <strong>World</strong></p></div>';
      const text = service.extractPlainText(html);

      expect(text).toBe('Hello World');
      expect(text).not.toContain('<');
      expect(text).not.toContain('>');
    });

    it('should replace br tags with newlines', () => {
      const html = '<p>Line 1<br>Line 2<br />Line 3</p>';
      const text = service.extractPlainText(html);

      expect(text).toContain('Line 1\n');
      expect(text).toContain('Line 2\n');
      expect(text).toContain('Line 3');
    });

    it('should replace p tags with double newlines', () => {
      const html = '<p>Paragraph 1</p><p>Paragraph 2</p>';
      const text = service.extractPlainText(html);

      expect(text).toContain('Paragraph 1\n\n');
      expect(text).toContain('Paragraph 2');
    });

    it('should decode HTML entities', () => {
      const html = '<p>&amp; &lt; &gt; &quot; &#039;</p>';
      const text = service.extractPlainText(html);

      expect(text).toContain('& < > " \'');
    });

    it('should normalize whitespace', () => {
      const html = '<p>Too     many    spaces</p>';
      const text = service.extractPlainText(html);

      expect(text).toBe('Too many spaces');
    });

    it('should remove script content', () => {
      const html = '<p>Text</p><script>alert("XSS")</script><p>More</p>';
      const text = service.extractPlainText(html);

      expect(text).not.toContain('alert');
      expect(text).not.toContain('XSS');
      expect(text).toContain('Text');
      expect(text).toContain('More');
    });
  });

  // =============================================================================
  // HTML Validation Tests
  // =============================================================================

  describe('validateHtml', () => {
    it('should detect script tags', () => {
      const html = '<script>alert("XSS")</script>';
      const result = service.validateHtml(html);

      expect(result.isSafe).toBe(false);
      expect(result.warnings).toContain('Contains script tags');
    });

    it('should detect inline event handlers', () => {
      const html = '<div onclick="alert(1)">Click</div>';
      const result = service.validateHtml(html);

      expect(result.isSafe).toBe(false);
      expect(result.warnings).toContain('Contains inline event handlers');
    });

    it('should detect dangerous URLs', () => {
      const html = '<a href="javascript:alert(1)">Click</a>';
      const result = service.validateHtml(html);

      expect(result.isSafe).toBe(false);
      expect(result.warnings).toContain('Contains dangerous URLs');
    });

    it('should detect embedded content', () => {
      const html = '<iframe src="https://evil.com"></iframe>';
      const result = service.validateHtml(html);

      expect(result.isSafe).toBe(false);
      expect(result.warnings).toContain('Contains embedded content');
    });

    it('should pass safe HTML', () => {
      const html = '<div><p>Safe <strong>HTML</strong></p></div>';
      const result = service.validateHtml(html);

      expect(result.isSafe).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });
  });

  // =============================================================================
  // Edge Cases and Special Scenarios
  // =============================================================================

  describe('Edge Cases', () => {
    it('should handle empty string', () => {
      const sanitized = service.sanitizeHtml('');
      expect(sanitized).toBe('');
    });

    it('should handle null/undefined', () => {
      const sanitized1 = service.sanitizeHtml(null as any);
      const sanitized2 = service.sanitizeHtml(undefined as any);

      expect(sanitized1).toBe('');
      expect(sanitized2).toBe('');
    });

    it('should handle plain text without HTML', () => {
      const text = 'Just plain text';
      const sanitized = service.sanitizeHtml(text);

      expect(sanitized).toBe(text);
    });

    it('should handle malformed HTML gracefully', () => {
      const html = '<div><p>Unclosed tags<div>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toBeDefined();
      expect(sanitized).toContain('Unclosed tags');
    });

    it('should handle very long HTML', () => {
      const html = '<p>' + 'a'.repeat(10000) + '</p>';
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('a'.repeat(100)); // Should process successfully
    });

    it('should handle multiple XSS vectors in one HTML', () => {
      const html = `
        <script>alert(1)</script>
        <div onclick="alert(2)">
          <a href="javascript:alert(3)">Click</a>
          <img src="x" onerror="alert(4)" />
        </div>
        <iframe src="javascript:alert(5)"></iframe>
      `;
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).not.toContain('alert');
      expect(sanitized).not.toContain('<script>');
      expect(sanitized).not.toContain('onclick');
      expect(sanitized).not.toContain('javascript:');
      expect(sanitized).not.toContain('onerror');
      expect(sanitized).not.toContain('<iframe');
    });
  });

  // =============================================================================
  // Real-World Email HTML Tests
  // =============================================================================

  describe('Real-World Email HTML', () => {
    it('should sanitize typical email HTML', () => {
      const html = `
        <div style="font-family: Arial; color: #333;">
          <p>Dear Candidate,</p>
          <p>Thank you for your <strong>CV submission</strong>.</p>
          <p>Please click <a href="https://example.com/apply">here</a> to continue.</p>
          <p>Best regards,<br />Recruitment Team</p>
        </div>
      `;
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('Dear Candidate');
      expect(sanitized).toContain('CV submission');
      expect(sanitized).toContain('href="https://example.com/apply"');
      expect(sanitized).toContain('font-family: Arial');
      expect(sanitized).toContain('color: #333');
    });

    it('should handle email with images and tables', () => {
      const html = `
        <table border="1">
          <tr>
            <td><img src="https://example.com/logo.png" alt="Logo" /></td>
            <td><h2>Company Name</h2></td>
          </tr>
        </table>
      `;
      const sanitized = service.sanitizeHtml(html);

      expect(sanitized).toContain('<table');
      expect(sanitized).toContain('<img');
      expect(sanitized).toContain('src="https://example.com/logo.png"');
      expect(sanitized).toContain('<h2>');
    });
  });
});
