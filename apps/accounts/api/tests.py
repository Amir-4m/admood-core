from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.accounts.models import Verification


class AccountsTest(APITestCase):
    def setUp(self):
        self.username = 'test_user'
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@example.com',
            password='F3DkePaSs0d'
        )
        self.user.is_active = True
        self.user.is_verified = True
        self.user.save()
        self.access_token = str(RefreshToken.for_user(user=self.user).access_token)
        super().setUp()

    def test_register_user_by_email(self):
        url = reverse('register_user_by_email')
        data = {'email': 'email@gmail.com', 'password': 'test@password', 'confirm_password': 'test@password'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.last().email, 'email@gmail.com')
        self.assertEqual(Verification.objects.count(), 1)

        url = reverse('register_verify')
        verification = Verification.objects.get()
        data['rc'] = verification.verify_code

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(Verification.objects.get().verified_time)

    def test_register_user_by_phone(self):
        url = reverse('register_user_by_phone')
        data = {'phone_number': '9121111111'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.last().phone_number, 9121111111)
        self.assertEqual(Verification.objects.count(), 1)

    def test_reset_password(self):
        url = reverse('reset_pass')
        data = {'email': 'test_user@example.com'}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verification = Verification.objects.get()

        url = reverse('reset_pass_confirm')
        data = {'password': 'set_p@ssword', 'confirm_password': 'set_p@ssword'}

        response = self.client.put(url + f'?rc={verification.verify_code}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(Verification.objects.get().verified_time)
        self.assertTrue(User.objects.get().check_password('set_p@ssword'))

    def test_set_pass(self):
        url = reverse('set_pass')
        data = {'password': 'new_p@ssword', 'confirm_password': 'new_p@ssword'}

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.get().check_password('new_p@ssword'))

    def test_set_phone_number(self):
        url = reverse('set_phone_number')
        data = {'phone_number': 9121111111}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        verification = Verification.objects.get(user=self.user,
                                                verify_type=Verification.VERIFY_TYPE_PHONE)
        verify_url = reverse('verify_phone_number')
        data = {'phone_number': 9121111111, 'verify_code': verification.verify_code}
        response = self.client.post(verify_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().phone_number, 9121111111)
