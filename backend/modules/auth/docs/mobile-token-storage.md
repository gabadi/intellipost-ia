# Mobile Token Storage Guide

## Overview
This guide provides best practices for securely storing authentication tokens in mobile applications when integrating with the IntelliPost API.

## Token Types
- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

## Platform-Specific Storage

### iOS (Swift)
Use the iOS Keychain for secure token storage:

```swift
import Security

class TokenManager {
    static let shared = TokenManager()

    private let accessTokenKey = "com.intellipost.accessToken"
    private let refreshTokenKey = "com.intellipost.refreshToken"

    func saveTokens(accessToken: String, refreshToken: String) -> Bool {
        let accessSaved = save(token: accessToken, for: accessTokenKey)
        let refreshSaved = save(token: refreshToken, for: refreshTokenKey)
        return accessSaved && refreshSaved
    }

    private func save(token: String, for key: String) -> Bool {
        let data = token.data(using: .utf8)!

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        // Delete any existing item
        SecItemDelete(query as CFDictionary)

        // Add new item
        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    func getAccessToken() -> String? {
        return getToken(for: accessTokenKey)
    }

    func getRefreshToken() -> String? {
        return getToken(for: refreshTokenKey)
    }

    private func getToken(for key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            return nil
        }

        return token
    }

    func deleteTokens() {
        delete(key: accessTokenKey)
        delete(key: refreshTokenKey)
    }

    private func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        SecItemDelete(query as CFDictionary)
    }
}
```

### Android (Kotlin)
Use Android Keystore with EncryptedSharedPreferences:

```kotlin
import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

class TokenManager(private val context: Context) {

    companion object {
        private const val PREFS_NAME = "intellipost_secure_prefs"
        private const val ACCESS_TOKEN_KEY = "access_token"
        private const val REFRESH_TOKEN_KEY = "refresh_token"
    }

    private val masterKey = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        PREFS_NAME,
        masterKey,
        context,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveTokens(accessToken: String, refreshToken: String) {
        encryptedPrefs.edit().apply {
            putString(ACCESS_TOKEN_KEY, accessToken)
            putString(REFRESH_TOKEN_KEY, refreshToken)
            apply()
        }
    }

    fun getAccessToken(): String? {
        return encryptedPrefs.getString(ACCESS_TOKEN_KEY, null)
    }

    fun getRefreshToken(): String? {
        return encryptedPrefs.getString(REFRESH_TOKEN_KEY, null)
    }

    fun deleteTokens() {
        encryptedPrefs.edit().apply {
            remove(ACCESS_TOKEN_KEY)
            remove(REFRESH_TOKEN_KEY)
            apply()
        }
    }
}
```

### React Native
Use a secure storage library like `react-native-keychain`:

```javascript
import * as Keychain from 'react-native-keychain';

class TokenManager {
  static async saveTokens(accessToken, refreshToken) {
    try {
      await Keychain.setInternetCredentials(
        'intellipost.api',
        'tokens',
        JSON.stringify({ accessToken, refreshToken }),
        {
          accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY
        }
      );
      return true;
    } catch (error) {
      console.error('Failed to save tokens:', error);
      return false;
    }
  }

  static async getTokens() {
    try {
      const credentials = await Keychain.getInternetCredentials('intellipost.api');
      if (credentials) {
        return JSON.parse(credentials.password);
      }
      return null;
    } catch (error) {
      console.error('Failed to get tokens:', error);
      return null;
    }
  }

  static async deleteTokens() {
    try {
      await Keychain.resetInternetCredentials('intellipost.api');
      return true;
    } catch (error) {
      console.error('Failed to delete tokens:', error);
      return false;
    }
  }
}
```

## Security Best Practices

### 1. Never Store in Plain Text
- ❌ Don't use SharedPreferences (Android) or UserDefaults (iOS) without encryption
- ❌ Don't store tokens in SQLite without encryption
- ❌ Don't hardcode tokens in source code

### 2. Use Platform Security Features
- ✅ iOS: Use Keychain with appropriate access control
- ✅ Android: Use Android Keystore or EncryptedSharedPreferences
- ✅ Set appropriate access levels (e.g., only when device unlocked)

### 3. Token Lifecycle Management
```javascript
// Example token refresh logic
class AuthService {
  async makeAuthenticatedRequest(url, options = {}) {
    let accessToken = await TokenManager.getAccessToken();

    // Try request with current access token
    let response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${accessToken}`
      }
    });

    // If unauthorized, try refreshing
    if (response.status === 401) {
      const refreshToken = await TokenManager.getRefreshToken();
      const refreshResponse = await fetch('/api/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (refreshResponse.ok) {
        const tokens = await refreshResponse.json();
        await TokenManager.saveTokens(tokens.access_token, tokens.refresh_token);

        // Retry original request
        response = await fetch(url, {
          ...options,
          headers: {
            ...options.headers,
            'Authorization': `Bearer ${tokens.access_token}`
          }
        });
      } else {
        // Refresh failed, redirect to login
        await TokenManager.deleteTokens();
        // Navigate to login screen
      }
    }

    return response;
  }
}
```

### 4. Additional Security Measures
1. **Biometric Authentication**: Require biometric authentication to access tokens
2. **Token Expiration**: Respect token expiration times
3. **Secure Communication**: Always use HTTPS for API calls
4. **Certificate Pinning**: Consider implementing certificate pinning for additional security
5. **Jailbreak/Root Detection**: Consider detecting compromised devices

### 5. Logout Implementation
Always clear tokens on logout:
```javascript
async function logout() {
  // Clear tokens from secure storage
  await TokenManager.deleteTokens();

  // Call logout API to invalidate refresh tokens server-side
  await fetch('/api/auth/logout', { method: 'POST' });

  // Clear any cached user data
  // Navigate to login screen
}
```

## Testing Recommendations
1. Test token expiration handling
2. Test refresh token rotation
3. Test logout across all user sessions
4. Test app behavior when tokens are manually deleted
5. Test network failure scenarios during token refresh

## Compliance Notes
- Ensure compliance with data protection regulations (GDPR, CCPA)
- Implement appropriate data retention policies
- Provide users with data export/deletion options
