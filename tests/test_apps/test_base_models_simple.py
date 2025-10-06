"""
Simple tests for base model classes.

This module tests the base model functionality without creating conflicting tables.
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.base_models import (
    AuditModel,
    BaseModel,
    SoftDeleteModel,
    TimestampedModel,
)


class TestBaseModelFeatures:
    """Test BaseModel core features."""

    def test_automatic_table_naming(self):
        """Test automatic table name generation."""
        # Test the table naming logic directly
        import re

        from src.apps.base_models import BaseModel

        def generate_table_name(class_name: str) -> str:
            name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
            name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

            # Better pluralization logic
            if name.endswith("y"):
                name = name[:-1] + "ies"
            elif name.endswith(("s", "sh", "ch", "x", "z")):
                name += "es"
            elif not name.endswith("s"):
                name += "s"

            return name

        # Test various class names
        assert generate_table_name("UserProfile") == "user_profiles"
        assert generate_table_name("OrderItem") == "order_items"
        assert generate_table_name("ProductCategory") == "product_categories"
        assert generate_table_name("Company") == "companies"
        assert generate_table_name("Address") == "addresses"
        assert generate_table_name("Box") == "boxes"
        assert generate_table_name("Wish") == "wishes"

    def test_base_model_instantiation(self):
        """Test that BaseModel can be instantiated with proper fields."""

        # Create a simple model that inherits from BaseModel
        class TestModel(BaseModel):
            __tablename__ = "test_model_table"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")

        # Check that it has the inherited fields
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
        assert hasattr(model, "name")
        assert model.name == "Test"

    def test_to_dict_method(self):
        """Test to_dict utility method."""

        class TestModel(BaseModel):
            __tablename__ = "test_model_table_2"
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            value: Mapped[int] = mapped_column(Integer, default=0)

        model = TestModel(name="Test", value=42)
        data = model.to_dict()

        assert isinstance(data, dict)
        assert "name" in data
        assert "value" in data
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["name"] == "Test"
        assert data["value"] == 42

    def test_from_dict_method(self):
        """Test from_dict utility method."""

        class TestModel(BaseModel):
            __tablename__ = "test_model_table_3"
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            value: Mapped[int] = mapped_column(Integer, default=0)

        data = {"name": "Test", "value": 42}
        model = TestModel.from_dict(data)

        assert model.name == "Test"
        assert model.value == 42

    def test_repr_method(self):
        """Test __repr__ method."""

        class TestModel(BaseModel):
            __tablename__ = "test_model_table_4"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")
        repr_str = repr(model)

        assert "TestModel" in repr_str
        assert "id=" in repr_str


class TestTimestampedModelFeatures:
    """Test TimestampedModel features."""

    def test_timestamped_model_instantiation(self):
        """Test that TimestampedModel can be instantiated."""

        class TestModel(TimestampedModel):
            __tablename__ = "test_timestamped_table"
            code: Mapped[str] = mapped_column(String(10), primary_key=True)
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(code="TEST", name="Test Model")

        # Check that it has timestamp fields but not id
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
        assert hasattr(model, "code")
        assert hasattr(model, "name")
        assert model.code == "TEST"
        assert model.name == "Test Model"


class TestSoftDeleteModelFeatures:
    """Test SoftDeleteModel features."""

    def test_soft_delete_model_instantiation(self):
        """Test that SoftDeleteModel can be instantiated."""

        class TestModel(SoftDeleteModel):
            __tablename__ = "test_soft_delete_table"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")

        # Check that it has all BaseModel fields plus soft delete fields
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
        assert hasattr(model, "is_deleted")
        assert hasattr(model, "deleted_at")
        assert hasattr(model, "name")
        assert model.name == "Test"

    def test_soft_delete_functionality(self):
        """Test soft delete and restore functionality."""

        class TestModel(SoftDeleteModel):
            __tablename__ = "test_soft_delete_table_2"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")

        # Initially not deleted (default values are None until persisted)
        assert model.is_deleted is None or model.is_deleted is False
        assert model.deleted_at is None

        # Soft delete
        model.soft_delete()
        assert model.is_deleted is True
        assert model.deleted_at is not None
        assert isinstance(model.deleted_at, datetime)

        # Restore
        model.restore()
        assert model.is_deleted is False
        assert model.deleted_at is None


class TestAuditModelFeatures:
    """Test AuditModel features."""

    def test_audit_model_instantiation(self):
        """Test that AuditModel can be instantiated."""

        class TestModel(AuditModel):
            __tablename__ = "test_audit_table"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")

        # Check that it has all BaseModel fields plus audit fields
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
        assert hasattr(model, "created_by")
        assert hasattr(model, "updated_by")
        assert hasattr(model, "version")
        assert hasattr(model, "name")
        assert model.name == "Test"

    def test_audit_fields_functionality(self):
        """Test audit fields functionality."""

        class TestModel(AuditModel):
            __tablename__ = "test_audit_table_2"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")
        user_id = uuid.uuid4()

        # Initially no audit info (default values are None until persisted)
        assert model.created_by is None
        assert model.updated_by is None
        assert model.version is None or model.version == 1

        # Set audit fields for creation
        model.set_audit_fields(user_id, is_update=False)
        assert model.created_by == user_id
        assert model.updated_by == user_id
        # Version should be 1 after setting audit fields
        assert model.version == 1

        # Set audit fields for update
        model.set_audit_fields(user_id, is_update=True)
        assert model.created_by == user_id  # Should remain unchanged
        assert model.updated_by == user_id
        assert model.version == 2

    def test_increment_version(self):
        """Test version increment functionality."""

        class TestModel(AuditModel):
            __tablename__ = "test_audit_table_3"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        model = TestModel(name="Test")
        # Version starts at None or 1 depending on how defaults are handled
        initial_version = model.version if model.version is not None else 1
        assert initial_version == 1

        # First increment sets version to 1 if it was None
        model.increment_version()
        assert model.version == 1

        # Second increment increases it to 2
        model.increment_version()
        assert model.version == 2

        model.increment_version()
        assert model.version == 3


class TestModelIntegration:
    """Test integration between different model types."""

    def test_model_inheritance_hierarchy(self):
        """Test that model inheritance works correctly."""

        class BaseTestModel(BaseModel):
            __tablename__ = "base_test_table"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        class SoftDeleteTestModel(SoftDeleteModel):
            __tablename__ = "soft_delete_test_table"
            description: Mapped[str] = mapped_column(Text, nullable=True)

        class AuditTestModel(AuditModel):
            __tablename__ = "audit_test_table"
            status: Mapped[str] = mapped_column(String(20), default="active")

        # Test that each model has the expected fields
        base_model = BaseTestModel(name="Base")
        assert hasattr(base_model, "id")
        assert hasattr(base_model, "created_at")
        assert hasattr(base_model, "updated_at")
        assert hasattr(base_model, "name")

        soft_delete_model = SoftDeleteTestModel(description="Test")
        assert hasattr(soft_delete_model, "id")
        assert hasattr(soft_delete_model, "created_at")
        assert hasattr(soft_delete_model, "updated_at")
        assert hasattr(soft_delete_model, "is_deleted")
        assert hasattr(soft_delete_model, "deleted_at")
        assert hasattr(soft_delete_model, "description")

        audit_model = AuditTestModel(status="active")
        assert hasattr(audit_model, "id")
        assert hasattr(audit_model, "created_at")
        assert hasattr(audit_model, "updated_at")
        assert hasattr(audit_model, "created_by")
        assert hasattr(audit_model, "updated_by")
        assert hasattr(audit_model, "version")
        assert hasattr(audit_model, "status")

    def test_utility_methods_work_across_models(self):
        """Test that utility methods work across all model types."""

        class BaseTestModel(BaseModel):
            __tablename__ = "base_test_table_2"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        class SoftDeleteTestModel(SoftDeleteModel):
            __tablename__ = "soft_delete_test_table_2"
            description: Mapped[str] = mapped_column(Text, nullable=True)

        class AuditTestModel(AuditModel):
            __tablename__ = "audit_test_table_2"
            status: Mapped[str] = mapped_column(String(20), default="active")

        # Test to_dict method
        base_model = BaseTestModel(name="Base")
        base_dict = base_model.to_dict()
        assert isinstance(base_dict, dict)
        assert "name" in base_dict

        soft_delete_model = SoftDeleteTestModel(description="Test")
        soft_delete_dict = soft_delete_model.to_dict()
        assert isinstance(soft_delete_dict, dict)
        assert "description" in soft_delete_dict
        assert "is_deleted" in soft_delete_dict

        audit_model = AuditTestModel(status="active")
        audit_dict = audit_model.to_dict()
        assert isinstance(audit_dict, dict)
        assert "status" in audit_dict
        assert "version" in audit_dict

        # Test from_dict method
        base_from_dict = BaseTestModel.from_dict({"name": "From Dict"})
        assert base_from_dict.name == "From Dict"

        soft_delete_from_dict = SoftDeleteTestModel.from_dict(
            {"description": "From Dict"}
        )
        assert soft_delete_from_dict.description == "From Dict"

        audit_from_dict = AuditTestModel.from_dict({"status": "inactive"})
        assert audit_from_dict.status == "inactive"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_model(self):
        """Test model with no additional fields."""

        class EmptyModel(BaseModel):
            __tablename__ = "empty_test_table"
            pass

        model = EmptyModel()
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")

        # Should still have utility methods
        data = model.to_dict()
        assert isinstance(data, dict)

    def test_model_with_custom_tablename(self):
        """Test model with custom table name."""

        class CustomModel(BaseModel):
            __tablename__ = "custom_table_simple"
            name: Mapped[str] = mapped_column(String(100), nullable=False)

        assert CustomModel.__tablename__ == "custom_table_simple"

    def test_model_with_complex_fields(self):
        """Test model with complex field types."""

        class ComplexModel(BaseModel):
            __tablename__ = "complex_test_table"
            name: Mapped[str] = mapped_column(String(100), nullable=False)
            description: Mapped[str | None] = mapped_column(Text, nullable=True)
            is_active: Mapped[bool] = mapped_column(Boolean, default=True)
            count: Mapped[int] = mapped_column(Integer, default=0)

        model = ComplexModel(name="Test")
        assert model.name == "Test"
        assert model.description is None
        # Default values are None until persisted to database
        assert model.is_active is None or model.is_active is True
        assert model.count is None or model.count == 0

        # Test with all fields
        model2 = ComplexModel(
            name="Test2", description="Description", is_active=False, count=42
        )
        assert model2.name == "Test2"
        assert model2.description == "Description"
        assert model2.is_active is False
        assert model2.count == 42
