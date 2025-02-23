"""test_views.py.

Tests for network app views.
"""

from django.test import TestCase
from django.urls import reverse


class TestNetworkView(TestCase):
    """Test class for CpuView."""

    def test_disk_view_status_code(self):
        """Test that the disk view renders with a status code 200.

        Asserts:
            Response status code is '200'
        """
        response = self.client.get(reverse("network"))
        self.assertEqual(response.status_code, 200)

    def test_disk_view_template_used(self):
        """Test that the correct template is used for the network view.

        Asserts:
            The correct template is rendered.
        """
        response = self.client.get(reverse("network"))
        self.assertTemplateUsed(response, "network.html")
