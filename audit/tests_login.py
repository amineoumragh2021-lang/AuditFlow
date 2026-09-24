from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginSessionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('portal-test', 'portal@example.com', 'test-password-42')

    def test_session_ends_with_browser_by_default(self):
        response = self.client.post(reverse('login'), {
            'email': 'portal@example.com', 'password': 'test-password-42',
        })
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_remember_me_keeps_session_for_thirty_days(self):
        self.client.post(reverse('login'), {
            'email': 'portal@example.com', 'password': 'test-password-42', 'remember_me': '1',
        })
        self.assertFalse(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.session.get_expiry_age(), 30 * 24 * 60 * 60)

    def test_wrong_password_does_not_authenticate(self):
        response = self.client.post(reverse('login'), {
            'email': 'portal@example.com', 'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'portal@example.com')
        self.assertNotIn('_auth_user_id', self.client.session)
