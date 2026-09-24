"""Deployment configuration checks; no external credentials or database required."""
import os
from pathlib import Path
import runpy
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, override_settings


class DeploymentSettingsTests(SimpleTestCase):
    def configuration(self, **overrides):
        env = {'DEBUG': 'True', 'SECRET_KEY': 'test-only-not-a-production-secret-' * 3}
        env.update(overrides)
        with patch.dict(os.environ, env, clear=True), patch('dotenv.load_dotenv'):
            return runpy.run_path(str(Path(__file__).with_name('settings.py')))

    def production_environment(self):
        return {
            'VERCEL': '1', 'DEBUG': 'False',
            'VERCEL_URL': 'auditflow-unique.example.vercel.app',
            'VERCEL_BRANCH_URL': 'auditflow-main.example.vercel.app',
            'VERCEL_PROJECT_PRODUCTION_URL': 'auditflow.example.vercel.app',
            'DATABASE_URL': 'postgresql://test:test@database.example.invalid/test?sslmode=require',
            'AWS_STORAGE_BUCKET_NAME': 'test-private-documents',
            'AWS_S3_ENDPOINT_URL': 'https://storage.example.invalid',
            'AWS_S3_REGION_NAME': 'eu-west-3',
            'AWS_ACCESS_KEY_ID': 'fake-test-id',
            'AWS_SECRET_ACCESS_KEY': 'fake-test-key',
        }

    def test_local_sqlite_and_filesystem_preserved(self):
        settings = self.configuration()
        self.assertEqual(settings['DATABASES']['default']['ENGINE'], 'django.db.backends.sqlite3')
        self.assertEqual(settings['DATABASES']['default']['NAME'].name, 'db.sqlite3')
        self.assertEqual(settings['STORAGES']['default']['BACKEND'], 'django.core.files.storage.FileSystemStorage')
        self.assertFalse(settings['SESSION_COOKIE_SECURE'])

    def test_vercel_configuration_is_private_and_secure(self):
        settings = self.configuration(**self.production_environment())
        db = settings['DATABASES']['default']
        self.assertEqual(db['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(db['CONN_MAX_AGE'], 0)
        self.assertTrue(db['DISABLE_SERVER_SIDE_CURSORS'])
        self.assertEqual(db['OPTIONS']['sslmode'], 'require')
        self.assertIsNone(db['OPTIONS']['prepare_threshold'])
        self.assertEqual(settings['SECURE_PROXY_SSL_HEADER'], ('HTTP_X_FORWARDED_PROTO', 'https'))
        self.assertTrue(settings['SESSION_COOKIE_SECURE'])
        self.assertTrue(settings['CSRF_COOKIE_SECURE'])
        self.assertNotIn('.vercel.app', settings['ALLOWED_HOSTS'])
        self.assertIn('https://auditflow.example.vercel.app', settings['CSRF_TRUSTED_ORIGINS'])
        self.assertEqual(settings['STORAGES']['default']['BACKEND'], 'storages.backends.s3.S3Storage')
        self.assertIsNone(settings['STORAGES']['default']['OPTIONS']['default_acl'])
        self.assertFalse(settings['STORAGES']['default']['OPTIONS']['file_overwrite'])
        self.assertIn('CompressedManifestStaticFilesStorage', settings['STORAGES']['staticfiles']['BACKEND'])

    def test_vercel_never_falls_back_to_sqlite_or_local_uploads(self):
        env = self.production_environment()
        env['DATABASE_URL'] = ''
        with self.assertRaisesMessage(ImproperlyConfigured, 'DATABASE_URL is required'):
            self.configuration(**env)
        env = self.production_environment()
        del env['AWS_SECRET_ACCESS_KEY']
        with self.assertRaisesMessage(ImproperlyConfigured, 'AWS_SECRET_ACCESS_KEY'):
            self.configuration(**env)

    def test_invalid_or_missing_settings_fail_explicitly(self):
        for values in ({'SECRET_KEY': ''}, {'DEBUG': 'maybe'}, {'DATABASE_URL': 'sqlite:///remote.db'}):
            with self.assertRaises(ImproperlyConfigured):
                self.configuration(**values)
        env = self.production_environment()
        env['DEBUG'] = 'True'
        with self.assertRaisesMessage(ImproperlyConfigured, 'DEBUG must be False'):
            self.configuration(**env)

    def test_local_asset_sources_are_present(self):
        for asset in ['audit/css/style.css', 'audit/css/dashboard.css', 'audit/css/theme.css', 'audit/js/app.js', 'audit/js/dashboard.js']:
            self.assertTrue(finders.find(asset), asset)

    @override_settings(SECURE_SSL_REDIRECT=True, SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
    def test_proxy_https_does_not_redirect_loop(self):
        self.assertEqual(self.client.get('/login/').status_code, 301)
        response = self.client.get('/login/', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(response.status_code, 200)
