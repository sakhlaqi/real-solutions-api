"""
API views with tenant isolation.

All views automatically filter data by the tenant in the request context.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from apps.authentication.permissions import IsTenantUser
from .models import Project, Task, Document
from .serializers import (
    ProjectSerializer,
    TaskSerializer,
    TaskDetailSerializer,
    DocumentSerializer,
)


class TenantScopedViewSetMixin:
    """
    Mixin that ensures all querysets are automatically filtered by tenant.
    
    Use this mixin in all ViewSets to enforce tenant isolation at the view layer.
    """
    
    def get_queryset(self):
        """
        Override to filter queryset by request tenant.
        
        This is the critical method that ensures tenant isolation.
        Every query will be automatically scoped to the authenticated tenant.
        """
        queryset = super().get_queryset()
        
        # Ensure we have a tenant in the request
        if not hasattr(self.request, 'tenant'):
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
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsTenantUser]
    
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Get all tasks for a specific project.
        
        GET /api/v1/projects/{id}/tasks/
        """
        project = self.get_object()
        tasks = Task.objects.for_tenant(request.tenant).filter(project=project)
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get project statistics for the tenant.
        
        GET /api/v1/projects/statistics/
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_projects': queryset.count(),
            'active_projects': queryset.filter(status='active').count(),
            'completed_projects': queryset.filter(status='completed').count(),
            'archived_projects': queryset.filter(status='archived').count(),
            'projects_with_tasks': queryset.annotate(
                task_count=Count('tasks')
            ).filter(task_count__gt=0).count(),
        }
        
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
