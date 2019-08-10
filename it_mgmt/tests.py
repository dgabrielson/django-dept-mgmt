#######################
from __future__ import print_function, unicode_literals

from django.test import TestCase

from .models import Computer, IPAddress

#######################
"""
Tests for the it_mgmt application.

This is not complete, but its a start.

References:
https://docs.djangoproject.com/en/dev/topics/testing/overview/
http://dougalmatthews.com/articles/2010/jan/20/testing-your-first-django-app/
http://toastdriven.com/blog/2011/apr/10/guide-to-testing-in-django/
"""

#######################################################################

#######################################################################


class ComputerIPChangeTestCase(TestCase):
    """
    Check all of the cases for a change in IP Address on the Computer model.
    This checks the computer signal handlers.
    """

    def setUp(self):
        """
        setUp is called at the start of *each* test 
        """
        self.addr1 = IPAddress.objects.create(
            number="192.168.0.1", hostname="addr-1.local"
        )
        self.addr2 = IPAddress.objects.create(
            number="192.168.0.2", hostname="addr-2.local"
        )
        self.computer1 = Computer.objects.create(
            common_name="computer 1", hardware="None", mac_address="tbd"
        )
        self.computer2 = Computer.objects.create(
            common_name="computer 2",
            hardware="None",
            mac_address="tbd",
            ip_address=self.addr2,
        )

    def test_create_without_ip(self):
        self.assertEqual(self.addr1.in_use, False)

    def test_create_with_ip(self):
        self.assertEqual(self.addr2.in_use, True)

    def test_update_no_ip(self):
        self.computer1.save()
        # force reload of addr from db data
        addr1 = IPAddress.objects.get(pk=self.addr1.pk)
        addr2 = IPAddress.objects.get(pk=self.addr2.pk)
        self.assertEqual(addr1.in_use, False)
        self.assertEqual(addr2.in_use, True)

    def test_update_ip_to_no_ip(self):
        self.computer2.ip_address = None
        self.computer2.save()
        # force reload of addr from db data
        addr1 = IPAddress.objects.get(pk=self.addr1.pk)
        addr2 = IPAddress.objects.get(pk=self.addr2.pk)
        self.assertEqual(addr1.in_use, False)
        self.assertEqual(addr2.in_use, False)

    def test_update_same_ip(self):
        self.computer2.save()
        # force reload of addr from db data
        addr1 = IPAddress.objects.get(pk=self.addr1.pk)
        addr2 = IPAddress.objects.get(pk=self.addr2.pk)
        self.assertEqual(addr1.in_use, False)
        self.assertEqual(addr2.in_use, True)

    def test_update_diff_ip(self):
        # setUp sets addr2
        self.computer2.ip_address = self.addr1
        self.computer2.save()
        # force reload of addr from db data
        addr1 = IPAddress.objects.get(pk=self.addr1.pk)
        addr2 = IPAddress.objects.get(pk=self.addr2.pk)
        self.assertEqual(addr1.in_use, True)
        self.assertEqual(addr2.in_use, False)

    def test_update_new_ip(self):
        self.computer1.ip_address = self.addr1
        self.computer1.save()
        # force reload of addr from db data
        addr1 = IPAddress.objects.get(pk=self.addr1.pk)
        addr2 = IPAddress.objects.get(pk=self.addr2.pk)
        self.assertEqual(addr1.in_use, True)
        self.assertEqual(addr2.in_use, True)

    def test_delete_with_ip(self):
        self.computer2.delete()
        self.assertEqual(self.addr1.in_use, False)
        self.assertEqual(self.addr2.in_use, False)

    def test_delete_without_ip(self):
        self.computer1.delete()
        self.assertEqual(self.addr1.in_use, False)
        self.assertEqual(self.addr2.in_use, True)
