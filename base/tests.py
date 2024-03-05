from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase, Client


class AdminPagesTestCase(TestCase):
    def setUp(self):
        self.username = 'user01'
        self.email = 'user01@example.com'
        self.password = 'user01P4ssw0rD'
        self.user = get_user_model().objects.create_user(
            self.username,
            self.email,
            self.password,
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()

    def test_all_add_urls_run(self):
        self.client.force_login(self.user)
        index_response = self.client.get('/admin/login/')
        for app in list(admin.site.get_app_list(index_response.wsgi_request)):
            for model in app['models']:
                print(model['add_url'])
                self.client.get(model['add_url'])

    def test_all_admin_urls_run(self):
        self.client.force_login(self.user)
        index_response = self.client.get('/admin/login/')
        for app in list(admin.site.get_app_list(index_response.wsgi_request)):
            for model in app['models']:
                print(model['admin_url'])
                self.client.get(model['admin_url'])
