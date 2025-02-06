"""test_views.py.

Tests for disk app views.
"""

from django.test import TestCase
from django.urls import reverse


class TestDiskView(TestCase):
    """Test class for CpuView."""

    def test_disk_view_status_code(self):
        """Test that the disk view renders with a status code 200."""
        response = self.client.get(reverse("disks"))
        self.assertEqual(response.status_code, 200)

    def test_disk_view_template_used(self):
        """Test that the correct template is used for the disk view."""
        response = self.client.get(reverse("disks"))
        self.assertTemplateUsed(response, "disks.html")
