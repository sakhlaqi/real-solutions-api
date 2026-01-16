"""
API views with tenant isolation.

All views automatically filter data by the tenant in the request context.
Defense in depth: Tenant isolation is enforced at multiple layers:
1. Authentication (JWT tenant claim extraction)
2. Middleware (tenant validation and logging)  
3. Permission (IsTenantUser validates tenant context)
4. View (TenantScopedViewSetMixin filters querysets)
5. Serializer (validates cross-tenant references)
6. Model (TenantAwareModel.save() enforces tenant)
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q, Prefetch
from apps.authentication.permissions import IsTenantUser
from .models import Project, Task, Document
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    TaskSerializer,
    TaskDetailSerializer,
    DocumentSerializer,
)


class TenantScopedViewSetMixin:
    """
    Mixin that ensures all querysets are automatically filtered by tenant.
    
    Use this mixin in all ViewSets to enforce tenant isolation at the view layer.
    This is part of the defense-in-depth strategy for tenant isolation.
    """
    
    def get_queryset(self):
        """
        Override to filter queryset by request tenant.
        
        This is the critical method that ensures tenant isolation.
        Every query will be automatically scoped to the authenticated tenant.
        
        Returns empty queryset if no tenant context (fail-safe).
        """
        queryset = super().get_queryset()
        
        # Fail-safe: return empty queryset if no tenant
        if not hasattr(self.request, 'tenant') or self.request.tenant is None:
            return queryset.none()
        
        # Filter by tenant using the custom manager
        return queryset.for_tenant(self.request.tenant)
    
    def perform_create(self, serializer):
        """
        Override to automatically set tenant when creating objects.
        """
        serializer.save(tenant=self.request.tenant)


class ProjectViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Project model.
    
    All operations are automatically scoped to the authenticated tenant.
    
    Endpoints:
    - GET /api/v1/projects/ - List all projects for tenant
    - POST /api/v1/projects/ - Create a new project
    - GET /api/v1/projects/{id}/ - Retrieve a project
    - PUT /api/v1/projects/{id}/ - Update a project
    - PATCH /api/v1/projects/{id}/ - Partial update a project
    - DELETE /api/v1/projects/{id}/ - Delete a project
    - GET /api/v1/projects/{id}/tasks/ - List tasks for a project
    - GET /api/v1/projects/statistics/ - Get project statistics
    """
    
    # Annotate with task count to avoid N+1 queries
    queryset = Project.objects.annotate(
        tasks_count=Count('tasks')
    ).select_related('tenant')
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    def get_serializer_class(self):
        """Use list serializer for list action to optimize response."""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Get all tasks for a specific project.
        
        GET /api/v1/projects/{id}/tasks/
        """
        project = self.get_object()
        tasks = Task.objects.for_tenant(request.tenant).filter(
            project=project
        ).select_related('project')
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get project statistics for the tenant.
        
        GET /api/v1/projects/statistics/
        
        Returns aggregated statistics in a single query to avoid N+1.
        """
        queryset = self.get_queryset()
        
        # Use aggregation to get all stats in one query
        from django.db.models import Case, When, IntegerField, Value
        
        stats = queryset.aggregate(
            total_projects=Count('id'),
            active_projects=Count(Case(
                When(status='active', then=1),
                output_field=IntegerField()
            )),
            completed_projects=Count(Case(
                When(status='completed', then=1),
                output_field=IntegerField()
            )),
            archived_projects=Count(Case(
                When(status='archived', then=1),
                output_field=IntegerField()
            )),
            projects_with_tasks=Count(Case(
                When(tasks_count__gt=0, then=1),
                output_field=IntegerField()
            )),
        )
        
        return Response(stats)


class TaskViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Task model.
    
    All operations are automatically scoped to the authenticated tenant.
    
    Endpoints:
    - GET /api/v1/tasks/ - List all tasks for tenant
    - POST /api/v1/tasks/ - Create a new task
    - GET /api/v1/tasks/{id}/ - Retrieve a task
    - PUT /api/v1/tasks/{id}/ - Update a task
    - PATCH /api/v1/tasks/{id}/ - Partial update a task
    - DELETE /api/v1/tasks/{id}/ - Delete a task
    - GET /api/v1/tasks/by-status/ - Filter tasks by status
    - POST /api/v1/tasks/{id}/complete/ - Mark task as complete
    """
    
    queryset = Task.objects.select_related('project', 'tenant').all()
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve actions."""
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Filter tasks by status.
        
        GET /api/v1/tasks/by-status/?status=todo
        """
        status_param = request.query_params.get('status')
        
        if not status_param:
            return Response(
                {'error': 'status parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tasks = self.get_queryset().filter(status=status_param)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark a task as complete.
        
        POST /api/v1/tasks/{id}/complete/
        """
        task = self.get_object()
        task.status = 'done'
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class DocumentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Document model.
    
    All operations are automatically scoped to the authenticated tenant.
    
    Endpoints:
    - GET /api/v1/documents/ - List all documents for tenant
    - POST /api/v1/documents/ - Create a new document
    - GET /api/v1/documents/{id}/ - Retrieve a document
    - PUT /api/v1/documents/{id}/ - Update a document
    - PATCH /api/v1/documents/{id}/ - Partial update a document
    - DELETE /api/v1/documents/{id}/ - Delete a document
    """
    
    queryset = Document.objects.select_related('project', 'tenant').all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    def get_queryset(self):
        """
        Override to optionally filter by project.
        
        Supports: GET /api/v1/documents/?project={project_id}
        """
        queryset = super().get_queryset()
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
