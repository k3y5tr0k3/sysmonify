"""test_views.py.

Tests for CPU app views.
"""

from django.test import TestCase
from django.urls import reverse


class TestCpuView(TestCase):
    """Test class for CpuView."""

    def test_cpu_view_status_code(self):
        """Test that the CPU view renders with a status code 200."""
        response = self.client.get(reverse("cpu"))
        self.assertEqual(response.status_code, 200)

    def test_cpu_view_template_used(self):
        """Test that the correct template is used for the CPU view."""
        response = self.client.get(reverse("cpu"))
        self.assertTemplateUsed(response, "cpu.html")
