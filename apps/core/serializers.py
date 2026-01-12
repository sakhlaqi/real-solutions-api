"""
Serializers for core models with tenant validation.
"""

from rest_framework import serializers
from .models import Project, Task, Document


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    
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
        """Get count of tasks for this project."""
        return obj.tasks.count()
    
    def create(self, validated_data):
        """
        Create a new project with tenant from request context.
        """
        # Tenant is injected from the view
        request = self.context.get('request')
        validated_data['tenant'] = request.tenant
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    
    Ensures that the project belongs to the same tenant as the request.
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
        from a different tenant.
        """
        request = self.context.get('request')
        
        if value.tenant != request.tenant:
            raise serializers.ValidationError(
                "Project does not belong to your tenant"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Create a new task with tenant from request context.
        """
        request = self.context.get('request')
        validated_data['tenant'] = request.tenant
        return super().create(validated_data)


class TaskDetailSerializer(TaskSerializer):
    """
    Detailed serializer for Task with nested project information.
    """
    
    project_details = ProjectSerializer(source='project', read_only=True)
    
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
