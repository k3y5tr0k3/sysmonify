"""test_views.py.

Tests for memory app views.
"""

from django.test import TestCase
from django.urls import reverse


class TestMemoryView(TestCase):
    """Test class for MemoryView."""

    def test_memory_view_status_code(self):
        """Test that the memory view renders with a status code 200."""
        response = self.client.get(reverse("memory"))
        self.assertEqual(response.status_code, 200)

    def test_memory_view_template_used(self):
        """Test that the correct template is used for the memory view."""
        response = self.client.get(reverse("memory"))
        self.assertTemplateUsed(response, "memory.html")
