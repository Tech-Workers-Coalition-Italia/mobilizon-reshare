from tortoise.contrib import test


class TestSomething(test.TestCase):
    async def test_something_async(self):
        ...

    @test.skip("Skip this")
    def test_skip(self):
        ...

    @test.expectedFailure
    def test_something(self):
        ...
