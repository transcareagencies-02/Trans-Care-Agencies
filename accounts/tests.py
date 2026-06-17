from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail

from users.models import User


class VerifyOtpTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='primary',
            email='primary@example.com',
            password='StrongPass123!',
            is_active=False,
            is_verified=False,
            otp='123456',
        )

    def test_verify_view_accepts_code_field_from_template(self):
        session = self.client.session
        session['email'] = self.user.email
        session.save()

        response = self.client.post(reverse('accounts:verify_otp'), {'code': '123456'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.get(pk=self.user.pk).is_active)
        self.assertTrue(User.objects.get(pk=self.user.pk).is_verified)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_resend_otp_sends_a_new_code_to_the_user_email(self):
        session = self.client.session
        session['email'] = self.user.email
        session.save()

        response = self.client.post(reverse('accounts:resend_otp'))

        self.assertRedirects(response, reverse('accounts:verify_otp'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn('verification', mail.outbox[0].subject.lower())
