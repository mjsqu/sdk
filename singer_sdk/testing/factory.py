"""Test Class Factory."""

from __future__ import annotations

from typing import Any, cast

import pytest

from .runners import TapTestRunner, TargetTestRunner


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Pytest Hook, responsible for parameterizing tests.

    Called once per each test function, this hook will check if the function name is
    registered in the parent classes 'params' dict, and if so will parameterize
    the given test function with the values therein.

    Args:
        metafunc: Pytest MetaFunc instance, representing a test function or method.
    """
    if metafunc.cls and hasattr(metafunc.cls, "params"):
        funcarglist = metafunc.cls.params.get(metafunc.definition.name)
        funcargids = (
            metafunc.cls.param_ids.get(metafunc.definition.name)
            if hasattr(metafunc.cls, "param_ids")
            else None
        )
        if funcarglist:
            argnames = funcarglist[0].keys()
            metafunc.parametrize(
                ",".join(argnames),
                [[funcargs[name] for name in argnames] for funcargs in funcarglist],
                ids=funcargids,
            )


def get_test_class(
    test_runner: TapTestRunner | TargetTestRunner, test_suites: list
) -> object:
    """Construct a valid pytest test class from given suites.

    Args:
        test_runner: A Tap or Target test runner instance.
        test_suites: A list of Test Suits to apply.

    Returns:
        A test class usable by pytest.
    """

    class BaseTestClass:
        """Base test class."""

        params: dict = {}
        param_ids: dict = {}

        @pytest.fixture
        def resource(self) -> Any:  # noqa: ANN401
            yield

        @pytest.fixture(scope="class")
        def runner(self) -> TapTestRunner | TargetTestRunner:
            return test_runner

    for suite in test_suites:

        # make sure given runner is of type TapTestRunner
        expected_runner_class = (  # type: ignore[valid-type]
            TapTestRunner
            if suite.kind in {"tap", "tap_stream", "tap_stream_attribute"}
            else TargetTestRunner
        )
        assert isinstance(test_runner, expected_runner_class), (
            f"Test suite of kind {suite.kind} passed, "
            f"but test runner if of type {type(test_runner)}."
        )
        test_runner = cast(
            expected_runner_class, test_runner  # type: ignore[valid-type]
        )

        if suite.kind in {"tap", "target"}:
            for TestClass in suite.tests:
                test = TestClass()
                test_name = f"test_{suite.kind}_{test.name}"
                setattr(BaseTestClass, f"test_{suite.kind}_{test.name}", test.run)

        if suite.kind in {"tap_stream", "tap_stream_attribute"}:

            # Populate runner class with records for use in stream/attribute tests
            test_runner.sync_all()

            if suite.kind == "tap_stream":

                params = [
                    {
                        "stream": stream,
                        "stream_records": test_runner.records[stream.name],
                    }
                    for stream in test_runner.tap.streams.values()
                ]
                param_ids = [stream.name for stream in test_runner.tap.streams.values()]

                for TestClass in suite.tests:
                    test = TestClass()
                    test_name = f"test_{suite.kind}_{test.name}"
                    setattr(
                        BaseTestClass,
                        test_name,
                        test.run,
                    )
                    BaseTestClass.params[test_name] = params
                    BaseTestClass.param_ids[test_name] = param_ids

            if suite.kind == "tap_stream_attribute":

                for TestClass in suite.tests:
                    test = TestClass()
                    test_name = f"test_{suite.kind}_{test.name}"
                    test_params = []
                    test_ids = []
                    for stream in test_runner.tap.streams.values():
                        test_params.extend(
                            [
                                {
                                    "stream": stream,
                                    "stream_records": test_runner.records[stream.name],
                                    "attribute_name": property_name,
                                }
                                for property_name, property_schema in stream.schema[
                                    "properties"
                                ].items()
                                if TestClass.evaluate(
                                    stream=stream,
                                    property_name=property_name,
                                    property_schema=property_schema,
                                )
                            ]
                        )
                        test_ids.extend(
                            [
                                f"{stream.name}.{property_name}"
                                for property_name, property_schema in stream.schema[
                                    "properties"
                                ].items()
                                if TestClass.evaluate(
                                    stream=stream,
                                    property_name=property_name,
                                    property_schema=property_schema,
                                )
                            ]
                        )

                    if test_params:
                        setattr(
                            BaseTestClass,
                            test_name,
                            test.run,
                        )
                        BaseTestClass.params[test_name] = test_params
                        BaseTestClass.param_ids[test_name] = test_ids

    return BaseTestClass
