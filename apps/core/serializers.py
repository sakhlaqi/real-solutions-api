"""
Serializers for core models with tenant validation.

Security: All serializers that handle cross-references (e.g., Task -> Project)
must validate that the referenced object belongs to the same tenant.
"""

from rest_framework import serializers
from .models import Project, Task, Document


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for Project list views.
    
    Uses annotated tasks_count from the queryset to avoid N+1 queries.
    """
    
    # Use annotated value from queryset instead of method field
    tasks_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'status',
            'tasks_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tasks_count']


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model (detail view and create/update).
    
    Automatically filters related tasks by tenant through the view.
    """
    
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'description',
            'status',
            'tasks_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_tasks_count(self, obj):
        """
        Get count of tasks for this project.
        
        Note: For list views, use ProjectListSerializer which uses
        annotated counts to avoid N+1 queries.
        """
        # Check if annotated value exists (from queryset)
        if hasattr(obj, 'tasks_count') and isinstance(obj.tasks_count, int):
            return obj.tasks_count
        return obj.tasks.count()
    
    def create(self, validated_data):
        """
        Create a new project with tenant from request context.
        """
        # Tenant is injected from the view's perform_create
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            validated_data['tenant'] = request.tenant
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    
    Ensures that the project belongs to the same tenant as the request.
    This prevents cross-tenant data access via foreign key manipulation.
    """
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'project_name',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_project(self, value):
        """
        Validate that the project belongs to the request's tenant.
        
        This prevents a user from associating a task with a project
        from a different tenant - a critical security check.
        """
        request = self.context.get('request')
        
        if not request or not hasattr(request, 'tenant'):
            raise serializers.ValidationError(
                "Unable to validate project ownership - missing tenant context"
            )
        
        if value.tenant_id != request.tenant.id:
            raise serializers.ValidationError(
                "Project does not belong to your tenant"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Create a new task with tenant from request context.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            validated_data['tenant'] = request.tenant
        return super().create(validated_data)


class TaskDetailSerializer(TaskSerializer):
    """
    Detailed serializer for Task with nested project information.
    """
    
    project_details = ProjectListSerializer(source='project', read_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['project_details']


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model.
    """
    
    project_name = serializers.CharField(
        source='project.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Document
        fields = [
            'id',
            'project',
            'project_name',
            'name',
            'file_path',
            'file_size',
            'content_type',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_project(self, value):
        """
        Validate that the project belongs to the request's tenant.
        """
        if value is None:
            return value
        
        request = self.context.get('request')
        
        if value.tenant != request.tenant:
            raise serializers.ValidationError(
                "Project does not belong to your tenant"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Create a new document with tenant from request context.
        """
        request = self.context.get('request')
        validated_data['tenant'] = request.tenant
        return super().create(validated_data)
