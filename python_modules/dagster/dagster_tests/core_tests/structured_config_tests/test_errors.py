from typing import Tuple

import pytest
from dagster import Config, asset, op, schedule, sensor
from dagster._config.structured_config import ConfigurableResource, ConfigurableResourceFactory
from dagster._core.definitions.resource_definition import ResourceDefinition
from dagster._core.errors import (
    DagsterInvalidDefinitionError,
    DagsterInvalidPythonicConfigDefinitionError,
)


def test_invalid_config_type_basic() -> None:
    class MyUnsupportedType:
        pass

    class DoSomethingConfig(Config):
        unsupported_param: MyUnsupportedType

    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class <class 'test_errors.test_invalid_config_type_basic.<locals>.DoSomethingConfig'> on field 'unsupported_param'.
Unable to resolve config type <class 'test_errors.test_invalid_config_type_basic.<locals>.MyUnsupportedType'> to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)""",
    ):

        @op
        def my_op(config: DoSomethingConfig):
            pass


def test_invalid_config_type_nested() -> None:
    class MyUnsupportedType:
        pass

    class MyNestedConfig(Config):
        unsupported_param: MyUnsupportedType

    class DoSomethingConfig(Config):
        nested_param: MyNestedConfig

    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class <class 'test_errors.test_invalid_config_type_nested.<locals>.MyNestedConfig'> on field 'unsupported_param'.
Unable to resolve config type <class 'test_errors.test_invalid_config_type_nested.<locals>.MyUnsupportedType'> to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)""",
    ):

        @op
        def my_op(config: DoSomethingConfig):
            pass


def test_invalid_resource_basic() -> None:
    class MyUnsupportedType:
        pass

    class MyBadResource(ConfigurableResource):
        unsupported_param: MyUnsupportedType

    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class <class 'test_errors.test_invalid_resource_basic.<locals>.MyBadResource'> on field 'unsupported_param'.
Unable to resolve config type <class 'test_errors.test_invalid_resource_basic.<locals>.MyUnsupportedType'> to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)


If this config type represents a resource dependency, its annotation must either:
    - Extend dagster.ConfigurableResource, dagster.ConfigurableIOManager, or
    - Be wrapped in a ResourceDependency annotation, e.g. ResourceDependency\\[MyUnsupportedType\\]""",
    ):
        MyBadResource(unsupported_param=MyUnsupportedType())


def test_invalid_config_class_directly_on_op() -> None:
    class MyUnsupportedType:
        pass

    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class.
Unable to resolve config type <class 'test_errors.test_invalid_config_class_directly_on_op.<locals>.MyUnsupportedType'> to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)""",
    ):

        @op
        def my_op(config: MyUnsupportedType):
            pass

    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class.
Unable to resolve config type <class 'test_errors.test_invalid_config_class_directly_on_op.<locals>.MyUnsupportedType'> to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)""",
    ):

        @asset
        def my_asset(config: MyUnsupportedType):
            pass


def test_unsupported_primitive_config_type_directly_on_op() -> None:
    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class.
Unable to resolve config type typing.Tuple\\[str, str\\] to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)""",
    ):

        @op
        def my_op(config: Tuple[str, str]):
            pass

    with pytest.raises(
        DagsterInvalidPythonicConfigDefinitionError,
        match="""Error defining Dagster config class.
Unable to resolve config type typing.Tuple\\[str, str\\] to a supported Dagster config type.


This config type can be a:
    - Python primitive type
        - int, float, bool, str, list
    - A Python Dict or List type containing other valid types
    - Custom data classes extending dagster.Config
    - A Pydantic discriminated union type \\(https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions\\)""",
    ):

        @asset
        def my_asset(config: Tuple[str, str]):
            pass


def test_annotate_with_resource_factory() -> None:
    class MyStringFactory(ConfigurableResourceFactory[str]):
        def create_resource(self, context: None) -> str:
            return "hello"

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_string' is annotated as '<class"
            " 'test_errors.test_annotate_with_resource_factory.<locals>.MyStringFactory'>', but"
            " '<class 'test_errors.test_annotate_with_resource_factory.<locals>.MyStringFactory'>'"
            " outputs a '<class 'str'>' value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[str\\]'"
        ),
    ):

        @op
        def my_op(my_string: MyStringFactory):
            pass

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_string' is annotated as '<class"
            " 'test_errors.test_annotate_with_resource_factory.<locals>.MyStringFactory'>', but"
            " '<class 'test_errors.test_annotate_with_resource_factory.<locals>.MyStringFactory'>'"
            " outputs a '<class 'str'>' value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[str\\]'"
        ),
    ):

        @asset
        def my_asset(my_string: MyStringFactory):
            pass

    class MyUnspecifiedFactory(ConfigurableResourceFactory):
        def create_resource(self, context: None) -> str:
            return "hello"

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_string' is annotated as '<class"
            " 'test_errors.test_annotate_with_resource_factory.<locals>.MyUnspecifiedFactory'>',"
            " but '<class"
            " 'test_errors.test_annotate_with_resource_factory.<locals>.MyUnspecifiedFactory'>'"
            " outputs an unknown value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[Any\\]' or 'Resource\\[<output type>\\]'"
        ),
    ):

        @op
        def my_op2(my_string: MyUnspecifiedFactory):
            pass

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_string' is annotated as '<class"
            " 'test_errors.test_annotate_with_resource_factory.<locals>.MyUnspecifiedFactory'>',"
            " but '<class"
            " 'test_errors.test_annotate_with_resource_factory.<locals>.MyUnspecifiedFactory'>'"
            " outputs an unknown value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[Any\\]' or 'Resource\\[<output type>\\]'"
        ),
    ):

        @asset
        def my_asset2(my_string: MyUnspecifiedFactory):
            pass


def test_annotate_with_resource_factory_schedule_sensor() -> None:
    class MyStringFactory(ConfigurableResourceFactory[str]):
        def create_resource(self, context: None) -> str:
            return "hello"

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_string' is annotated as '<class"
            " 'test_errors.test_annotate_with_resource_factory_schedule_sensor.<locals>.MyStringFactory'>',"
            " but '<class"
            " 'test_errors.test_annotate_with_resource_factory_schedule_sensor.<locals>.MyStringFactory'>'"
            " outputs a '<class 'str'>' value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[str\\]'"
        ),
    ):

        @sensor(job_name="foo")
        def my_sensor(my_string: MyStringFactory):
            pass

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_string' is annotated as '<class"
            " 'test_errors.test_annotate_with_resource_factory_schedule_sensor.<locals>.MyStringFactory'>',"
            " but '<class"
            " 'test_errors.test_annotate_with_resource_factory_schedule_sensor.<locals>.MyStringFactory'>'"
            " outputs a '<class 'str'>' value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[str\\]'"
        ),
    ):

        @schedule(job_name="foo", cron_schedule="* * * * *")
        def my_schedule(my_string: MyStringFactory):
            pass


def test_annotate_with_bare_resource_def() -> None:
    class MyResourceDef(ResourceDefinition):
        pass

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_resource' is annotated as '<class"
            " 'test_errors.test_annotate_with_bare_resource_def.<locals>.MyResourceDef'>', but"
            " '<class 'test_errors.test_annotate_with_bare_resource_def.<locals>.MyResourceDef'>'"
            " outputs an unknown value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[Any\\]' or 'Resource\\[<output type>\\]'"
        ),
    ):

        @op
        def my_op(my_resource: MyResourceDef):
            pass

    with pytest.raises(
        DagsterInvalidDefinitionError,
        match=(
            "Resource param 'my_resource' is annotated as '<class"
            " 'test_errors.test_annotate_with_bare_resource_def.<locals>.MyResourceDef'>', but"
            " '<class 'test_errors.test_annotate_with_bare_resource_def.<locals>.MyResourceDef'>'"
            " outputs an unknown value to user code such as @ops and @assets. This"
            " annotation should instead be 'Resource\\[Any\\]' or 'Resource\\[<output type>\\]'"
        ),
    ):

        @asset
        def my_asset(my_resource: MyResourceDef):
            pass