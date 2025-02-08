"""test_views.py.

Tests for GPU app views.
"""

from django.test import TestCase
from django.urls import reverse


class TestGpuView(TestCase):
    """Test class for GpuView."""

    def test_gpu_view_status_code(self):
        """Test that the GPU view renders with a status code 200."""
        response = self.client.get(reverse("gpu"))
        self.assertEqual(response.status_code, 200)

    def test_gpu_view_template_used(self):
        """Test that the correct template is used for the GPU view."""
        response = self.client.get(reverse("gpu"))
        self.assertTemplateUsed(response, "gpu.html")
