"""Tests for aa_kanban image upload and safe markdown rendering."""

import pytest
from allianceauth.tests.auth_utils import AuthUtils
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.urls import reverse

from aa_kanban.markdown import render_markdown
from aa_kanban.models import KanbanAttachment

TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00"
    b"\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)
TINY_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00"
    b"\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01"
    b"\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05"
    b"\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
)
TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00"
    b"\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)
TINY_WEBP = (
    b"RIFF\x1a\x00\x00\x00WEBPVP8 \x0e\x00\x00\x00\x30\x01\x00\x9d\x01\x2a\x01\x00\x01"
    b"\x00\x02\x00\x34\x25"
)


@pytest.fixture
def kanban_user(db):
    user = AuthUtils.create_user("upload_user")
    AuthUtils.add_main_character(user, "Upload Char", character_id=12345)
    AuthUtils.add_permission_to_user_by_name("aa_kanban.basic_access", user)
    return user


@pytest.fixture
def ticket_user(db):
    user = AuthUtils.create_user("ticket_only_user")
    AuthUtils.add_main_character(user, "Ticket Char", character_id=12346)
    AuthUtils.add_permission_to_user_by_name("aa_kanban.create_ticket", user)
    return user


@pytest.fixture
def unauthorized_user(db):
    user = AuthUtils.create_user("unauth_user")
    AuthUtils.add_main_character(user, "Unauth Char", character_id=12347)
    return user


@pytest.mark.django_db
class TestImageUploadEndpoint:
    def test_upload_valid_png(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)
        uploaded = SimpleUploadedFile(
            "screenshot.png", TINY_PNG, content_type="image/png"
        )

        url = reverse("aa_kanban:upload_image")
        response = client.post(url, {"image": uploaded})

        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert data["filename"] == "screenshot.png"
        assert f"![screenshot.png]({data['url']})" in data["markdown"]

        # Verify record in database
        attachment = KanbanAttachment.objects.get(pk=data["id"])
        assert attachment.uploader == kanban_user
        assert attachment.original_filename == "screenshot.png"
        assert attachment.size == len(TINY_PNG)

    def test_upload_valid_jpeg_and_gif(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)

        # JPEG
        up_jpg = SimpleUploadedFile("photo.jpg", TINY_JPEG, content_type="image/jpeg")
        resp1 = client.post(reverse("aa_kanban:upload_image"), {"image": up_jpg})
        assert resp1.status_code == 200

        # GIF
        up_gif = SimpleUploadedFile("anim.gif", TINY_GIF, content_type="image/gif")
        resp2 = client.post(reverse("aa_kanban:upload_image"), {"image": up_gif})
        assert resp2.status_code == 200

        # WEBP
        up_webp = SimpleUploadedFile(
            "modern.webp", TINY_WEBP, content_type="image/webp"
        )
        resp3 = client.post(reverse("aa_kanban:upload_image"), {"image": up_webp})
        assert resp3.status_code == 200

    def test_upload_by_ticket_user(self, ticket_user):
        client = Client()
        client.force_login(ticket_user)
        uploaded = SimpleUploadedFile(
            "ticket_shot.png", TINY_PNG, content_type="image/png"
        )

        response = client.post(reverse("aa_kanban:upload_image"), {"image": uploaded})
        assert response.status_code == 200
        assert response.json()["filename"] == "ticket_shot.png"

    def test_upload_unauthorized_user(self, unauthorized_user):
        client = Client()
        client.force_login(unauthorized_user)
        uploaded = SimpleUploadedFile("shot.png", TINY_PNG, content_type="image/png")

        response = client.post(reverse("aa_kanban:upload_image"), {"image": uploaded})
        assert response.status_code == 403

    def test_upload_unauthenticated(self):
        client = Client()
        uploaded = SimpleUploadedFile("shot.png", TINY_PNG, content_type="image/png")

        response = client.post(reverse("aa_kanban:upload_image"), {"image": uploaded})
        assert response.status_code == 302  # redirects to login

    def test_upload_missing_file(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)

        response = client.post(reverse("aa_kanban:upload_image"), {})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_upload_disallowed_extension(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)
        uploaded = SimpleUploadedFile(
            "script.sh", b"echo hello", content_type="text/plain"
        )

        response = client.post(reverse("aa_kanban:upload_image"), {"image": uploaded})
        assert response.status_code == 400
        assert "Unsupported" in response.json()["error"]

    def test_upload_spoofed_file(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)
        # File has .png extension but plain text payload
        uploaded = SimpleUploadedFile(
            "fake.png", b"Not a PNG image", content_type="image/png"
        )

        response = client.post(reverse("aa_kanban:upload_image"), {"image": uploaded})
        assert response.status_code == 400
        assert "Invalid" in response.json()["error"]

    def test_upload_exceeds_size_limit(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)
        # Create a payload larger than 5MB
        huge_payload = TINY_PNG + (b"\x00" * (5 * 1024 * 1024 + 100))
        uploaded = SimpleUploadedFile(
            "huge.png", huge_payload, content_type="image/png"
        )

        response = client.post(reverse("aa_kanban:upload_image"), {"image": uploaded})
        assert response.status_code == 400
        assert "exceeds" in response.json()["error"]

    def test_upload_method_not_allowed(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)

        response = client.get(reverse("aa_kanban:upload_image"))
        assert response.status_code == 405


@pytest.mark.django_db
class TestMarkdownRendering:
    def test_render_basic_markdown(self):
        md = "# Heading 1\n\n**Bold text** and *italic text* and `inline code`."
        html = render_markdown(md)
        assert "<h1>Heading 1</h1>" in html
        assert "<strong>Bold text</strong>" in html
        assert "<em>italic text</em>" in html
        assert "<code>inline code</code>" in html

    def test_render_inline_images(self):
        md = "Here is a screenshot:\n\n![My Screenshot](/media/aa_kanban/uploads/shot.png)"
        html = render_markdown(md)
        assert "<img" in html
        assert 'src="/media/aa_kanban/uploads/shot.png"' in html
        assert 'alt="My Screenshot"' in html
        assert "kanban-rendered-image" in html
        assert "img-fluid" in html
        assert 'data-image-zoom="true"' in html

    def test_render_table(self):
        md = "| Col 1 | Col 2 |\n| --- | --- |\n| Val 1 | Val 2 |"
        html = render_markdown(md)
        assert "<table" in html
        assert "table-sm" in html
        assert "Val 1" in html

    def test_render_strips_dangerous_html(self):
        malicious = (
            '<script>alert("XSS")</script>'
            '<img src="x" onerror="alert(1)">'
            '<a href="javascript:alert(1)">Click Me</a>'
            '<iframe src="https://evil.com"></iframe>'
        )
        html = render_markdown(malicious)
        assert "<script>" not in html
        assert "onerror" not in html
        assert "javascript:" not in html
        assert "<iframe>" not in html

    def test_preview_markdown_endpoint(self, kanban_user):
        client = Client()
        client.force_login(kanban_user)

        url = reverse("aa_kanban:preview_markdown")
        response = client.post(url, {"text": "### Test Ticket\n\nHello world!"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "<h3>Test Ticket</h3>" in content
        assert "Hello world!" in content
