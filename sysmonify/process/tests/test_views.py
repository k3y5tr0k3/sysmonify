"""test_views.py.

Tests for process app views.
"""

from django.test import TestCase
from django.urls import reverse


class TestProcessView(TestCase):
    """Test class for ProcessView."""

    def test_process_view_status_code(self):
        """Test that the process view renders with a status code 200.

        Asserts:
            Response status code is '200'
        """
        response = self.client.get(reverse("processes"))
        self.assertEqual(response.status_code, 200)

    def test_process_view_template_used(self):
        """Test that the correct template is used for the process view.

        Asserts:
            The correct template is rendered.
        """
        response = self.client.get(reverse("processes"))
        self.assertTemplateUsed(response, "process.html")
