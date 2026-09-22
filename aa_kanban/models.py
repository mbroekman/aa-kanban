"""Models for aa_kanban."""

from django.contrib.auth.models import AnonymousUser, Group, User
from django.db import models
from django.utils.text import slugify


class General(models.Model):
    """Meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("manage_boards", "Can manage kanban boards"),
        )


class BoardQuerySet(models.QuerySet):
    """Custom queryset for Board model."""

    def visible_to(self, user: User | AnonymousUser):
        """Filter boards visible to the given user."""
        if not user.is_authenticated:
            return self.none()
        if user.is_superuser:
            return self.all()
        user_kanban_groups = user.kanban_groups.all()
        return self.filter(
            models.Q(view_groups__in=user_kanban_groups)
            | models.Q(write_groups__in=user_kanban_groups)
            | models.Q(created_by=user)
        ).distinct()

class KanbanGroup(models.Model):
    """Custom group model for aa_kanban access management."""

    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(
        User,
        blank=True,
        related_name="kanban_groups",
    )

    class Meta:
        verbose_name = "Kanban Group"
        verbose_name_plural = "Kanban Groups"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class KanbanSetting(models.Model):
    """Global settings for aa_kanban."""

    board_creation_webhook = models.URLField(
        blank=True,
        null=True,
        help_text="Discord Webhook URL for global board creation notifications.",
    )

    class Meta:
        verbose_name = "Kanban Setting"
        verbose_name_plural = "Kanban Settings"

    def __str__(self) -> str:
        return "Global Kanban Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        if not self.pk and KanbanSetting.objects.exists():
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get the singleton settings instance, creating it if it doesn't exist."""
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings


class Board(models.Model):
    """Kanban board."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    discord_webhook_cards = models.URLField(
        blank=True,
        null=True,
        help_text="Discord Webhook URL for card movement notifications on this board.",
    )

    view_groups = models.ManyToManyField(
        KanbanGroup,
        blank=True,
        related_name="kanban_view_boards",
        help_text="Kanban groups that have read-only access to this board.",
    )
    write_groups = models.ManyToManyField(
        KanbanGroup,
        blank=True,
        related_name="kanban_write_boards",
        help_text="Kanban groups that have write/mutation access to this board.",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BoardQuerySet.as_manager()

    class Meta:
        verbose_name = "Board"
        verbose_name_plural = "Boards"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base_slug = slugify(self.name) or "board"
            slug = base_slug
            counter = 1
            while Board.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def can_user_view(self, user: User | AnonymousUser) -> bool:
        """Check if user has read-only or higher access to this board."""
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if self.created_by_id == user.id:
            return True
        user_group_ids = set(user.kanban_groups.values_list("id", flat=True))
        write_group_ids = set(self.write_groups.values_list("id", flat=True))
        view_group_ids = set(self.view_groups.values_list("id", flat=True))
        return bool(user_group_ids & (write_group_ids | view_group_ids))

    def can_user_write(self, user: User | AnonymousUser) -> bool:
        """Check if user has write/mutation access to this board."""
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if self.created_by_id == user.id:
            return True
        user_group_ids = set(user.kanban_groups.values_list("id", flat=True))
        write_group_ids = set(self.write_groups.values_list("id", flat=True))
        return bool(user_group_ids & write_group_ids)


class List(models.Model):
    """Column/List within a Kanban Board."""

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="lists",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True, default="", help_text="Optional context for this column"
    )
    wip_limit = models.PositiveIntegerField(
        default=0, help_text="Maximum cards (0 for unlimited)"
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "List"
        verbose_name_plural = "Lists"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.board.name} - {self.name}"


class Label(models.Model):
    """Color label for categorizing cards on a board."""

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="labels",
    )
    name = models.CharField(max_length=50)
    color = models.CharField(
        max_length=20,
        default="primary",
        help_text=(
            "Bootstrap badge color style "
            "(e.g. primary, success, danger, warning, info, dark)"
        ),
    )

    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"
        ordering = ["name"]
        unique_together = ("board", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.color})"


class Card(models.Model):
    """Task card within a Kanban List."""

    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    assignees = models.ManyToManyField(
        User,
        blank=True,
        related_name="assigned_kanban_cards",
    )
    labels = models.ManyToManyField(
        Label,
        blank=True,
        related_name="cards",
    )

    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Comment on a Kanban Card."""

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="kanban_comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.card.title}"
