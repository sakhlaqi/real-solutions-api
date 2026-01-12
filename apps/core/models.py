"""
Example models demonstrating tenant-safe patterns.

These models show how to properly implement tenant isolation in your data layer.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.tenants.models import TenantAwareModel
from apps.tenants.managers import TenantManager


class Project(TenantAwareModel):
    """
    Example model: Project
    
    Demonstrates tenant-scoped data model with custom manager.
    All queries on this model are automatically tenant-filtered when using
    the custom manager methods.
    """
    
    name = models.CharField(
        max_length=255,
        help_text=_("Project name")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Project description")
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('archived', 'Archived'),
        ],
        default='active',
        help_text=_("Project status")
    )
    
    # Use the tenant-aware manager
    objects = TenantManager()
    
    class Meta:
        db_table = 'projects'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'name']),
        ]
        # Enforce unique project names per tenant
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_project_name_per_tenant'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant.slug})"


class Task(TenantAwareModel):
    """
    Example model: Task
    
    Demonstrates a related model with foreign key to another tenant-scoped model.
    """
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text=_("Project this task belongs to")
    )
    
    title = models.CharField(
        max_length=255,
        help_text=_("Task title")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Task description")
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('todo', 'To Do'),
            ('in_progress', 'In Progress'),
            ('done', 'Done'),
        ],
        default='todo',
        help_text=_("Task status")
    )
    
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium',
        help_text=_("Task priority")
    )
    
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Task due date")
    )
    
    # Use the tenant-aware manager
    objects = TenantManager()
    
    class Meta:
        db_table = 'tasks'
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'project', 'status']),
            models.Index(fields=['tenant', 'due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.project.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure task's tenant matches project's tenant.
        This is a critical safeguard against cross-tenant data leaks.
        """
        if self.project and self.project.tenant_id != self.tenant_id:
            raise ValueError(
                "Task tenant must match project tenant"
            )
        super().save(*args, **kwargs)


class Document(TenantAwareModel):
    """
    Example model: Document
    
    Demonstrates file/document management with tenant isolation.
    """
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        help_text=_("Optional project association")
    )
    
    name = models.CharField(
        max_length=255,
        help_text=_("Document name")
    )
    
    file_path = models.CharField(
        max_length=500,
        help_text=_("Path to document file")
    )
    
    file_size = models.BigIntegerField(
        help_text=_("File size in bytes")
    )
    
    content_type = models.CharField(
        max_length=100,
        help_text=_("MIME type of the document")
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional document metadata")
    )
    
    # Use the tenant-aware manager
    objects = TenantManager()
    
    class Meta:
        db_table = 'documents'
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'project']),
            models.Index(fields=['tenant', 'name']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.tenant.slug})"
    
    def save(self, *args, **kwargs):
        """Ensure document's tenant matches project's tenant if project is set."""
        if self.project and self.project.tenant_id != self.tenant_id:
            raise ValueError(
                "Document tenant must match project tenant"
            )
        super().save(*args, **kwargs)
