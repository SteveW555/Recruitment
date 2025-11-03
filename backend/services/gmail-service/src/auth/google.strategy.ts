import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy, VerifyCallback } from 'passport-google-oauth20';
import { ConfigService } from '@nestjs/config';

/**
 * Google OAuth 2.0 Strategy
 * Handles authentication flow with Google Identity Platform
 */
@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor(private configService: ConfigService) {
    super({
      clientID: configService.get('GOOGLE_CLIENT_ID'),
      clientSecret: configService.get('GOOGLE_CLIENT_SECRET'),
      callbackURL: configService.get('GOOGLE_CALLBACK_URL'),
      scope: [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
      ],
      accessType: 'offline', // Request refresh token
      prompt: 'consent',      // Force consent screen to get refresh token
    });
  }

  async validate(
    accessToken: string,
    refreshToken: string,
    profile: any,
    done: VerifyCallback,
  ): Promise<any> {
    // Extract user info from profile
    const user = {
      email: profile.emails[0].value,
      name: profile.displayName,
      picture: profile.photos?.[0]?.value,
      accessToken,
      refreshToken,
      profile,
    };

    // Check if email is Gmail
    if (!user.email.endsWith('@gmail.com')) {
      return done(
        new Error('Only Gmail accounts are supported'),
        false,
      );
    }

    done(null, user);
  }
}
