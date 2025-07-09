"""
Test cases for variance in generic types.

This module tests whether type checkers correctly handle covariance,
contravariance, and invariance in generic types.
"""

from typing import TypeVar, Generic, Any, Optional, List, Dict, Callable, Union
from typing_extensions import Literal
from abc import ABC, abstractmethod


# Type variables for variance testing
T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)
T_contra = TypeVar('T_contra', contravariant=True)


# Base classes for testing inheritance
class Animal:
    """Base animal class."""

    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"


class Dog(Animal):
    """Dog class that inherits from Animal."""

    def speak(self) -> str:
        return f"{self.name} barks"

    def fetch(self) -> str:
        return f"{self.name} fetches the ball"


class Cat(Animal):
    """Cat class that inherits from Animal."""

    def speak(self) -> str:
        return f"{self.name} meows"

    def purr(self) -> str:
        return f"{self.name} purrs"


class GermanShepherd(Dog):
    """German Shepherd class that inherits from Dog."""

    def guard(self) -> str:
        return f"{self.name} guards the house"


# Invariant generic class (default)
class InvariantBox(Generic[T]):
    """Box that is invariant in T."""

    def __init__(self, value: T):
        self._value = value

    def get(self) -> T:
        return self._value

    def set(self, value: T) -> None:
        self._value = value


# Covariant generic class
class CovariantProducer(Generic[T_co]):
    """Producer that is covariant in T_co (only produces T_co)."""

    def __init__(self, value: T_co):
        self._value = value

    def get(self) -> T_co:
        return self._value

    def produce(self) -> T_co:
        return self._value


# Contravariant generic class
class ContravariantConsumer(Generic[T_contra]):
    """Consumer that is contravariant in T_contra (only consumes T_contra)."""

    def __init__(self):
        self._values: List[T_contra] = []

    def consume(self, value: T_contra) -> None:
        self._values.append(value)

    def process(self, value: T_contra) -> str:
        return f"Processing {value}"


# Read-only covariant container
class ReadOnlyContainer(Generic[T_co]):
    """Read-only container that is covariant."""

    def __init__(self, items: List[T_co]):
        self._items = items.copy()

    def get_item(self, index: int) -> T_co:
        return self._items[index]

    def get_all(self) -> List[T_co]:
        return self._items.copy()

    def __len__(self) -> int:
        return len(self._items)


# Write-only contravariant container
class WriteOnlyContainer(Generic[T_contra]):
    """Write-only container that is contravariant."""

    def __init__(self):
        self._items: List[T_contra] = []

    def add_item(self, item: T_contra) -> None:
        self._items.append(item)

    def add_all(self, items: List[T_contra]) -> None:
        self._items.extend(items)


# Function types with variance
class FunctionWrapper(Generic[T_contra, T_co]):
    """Wrapper for functions that are contravariant in input, covariant in output."""

    def __init__(self, func: Callable[[T_contra], T_co]):
        self._func = func

    def call(self, arg: T_contra) -> T_co:
        return self._func(arg)


# Test functions
def test_invariant_variance():
    """Test invariant variance behavior."""

    # Create boxes
    animal_box = InvariantBox[Animal](Animal("Generic Animal"))
    dog_box = InvariantBox[Dog](Dog("Rex"))
    cat_box = InvariantBox[Cat](Cat("Whiskers"))

    # These should work (same type)
    animal_value = animal_box.get()  # Should be Animal
    dog_value = dog_box.get()  # Should be Dog
    cat_value = cat_box.get()  # Should be Cat

    # These should fail (invariant - no subtype relationship)
    def process_animal_box(box: InvariantBox[Animal]) -> str:
        return box.get().speak()

    result1 = process_animal_box(animal_box)  # Should be OK
    result2 = process_animal_box(dog_box)  # Should cause error: Dog box is not Animal box
    result3 = process_animal_box(cat_box)  # Should cause error: Cat box is not Animal box

    # Assignment should also fail
    animal_box_ref: InvariantBox[Animal] = dog_box  # Error: invariant
    dog_box_ref: InvariantBox[Dog] = animal_box  # Error: invariant

    return animal_value, dog_value, cat_value, result1, result2, result3


def test_covariant_variance():
    """Test covariant variance behavior."""

    # Create producers
    animal_producer = CovariantProducer[Animal](Animal("Generic Animal"))
    dog_producer = CovariantProducer[Dog](Dog("Rex"))
    cat_producer = CovariantProducer[Cat](Cat("Whiskers"))
    shepherd_producer = CovariantProducer[GermanShepherd](GermanShepherd("Max"))

    # These should work (covariant - Dog is subtype of Animal)
    def process_animal_producer(producer: CovariantProducer[Animal]) -> str:
        return producer.get().speak()

    result1 = process_animal_producer(animal_producer)  # Should be OK
    result2 = process_animal_producer(dog_producer)  # Should be OK (Dog <: Animal)
    result3 = process_animal_producer(cat_producer)  # Should be OK (Cat <: Animal)

    # Assignment should work (covariant)
    animal_producer_ref: CovariantProducer[Animal] = dog_producer  # Should be OK
    dog_producer_ref: CovariantProducer[Dog] = shepherd_producer  # Should be OK

    # This should fail (wrong direction)
    dog_producer_ref2: CovariantProducer[Dog] = animal_producer  # Error: Animal is not subtype of Dog

    # Test with read-only container
    animal_container = ReadOnlyContainer[Animal]([Animal("A1"), Animal("A2")])
    dog_container = ReadOnlyContainer[Dog]([Dog("D1"), Dog("D2")])

    def process_animal_container(container: ReadOnlyContainer[Animal]) -> List[str]:
        return [container.get_item(i).speak() for i in range(len(container))]

    animal_results = process_animal_container(animal_container)  # Should be OK
    dog_results = process_animal_container(dog_container)  # Should be OK (covariant)

    return (result1, result2, result3, animal_results, dog_results)


def test_contravariant_variance():
    """Test contravariant variance behavior."""

    # Create consumers
    animal_consumer = ContravariantConsumer[Animal]()
    dog_consumer = ContravariantConsumer[Dog]()
    cat_consumer = ContravariantConsumer[Cat]()

    # These should work (contravariant - Animal consumer can consume Dog)
    def feed_dog_consumer(consumer: ContravariantConsumer[Dog]) -> None:
        consumer.consume(Dog("Rex"))

    feed_dog_consumer(dog_consumer)  # Should be OK
    feed_dog_consumer(animal_consumer)  # Should be OK (Animal consumer can consume Dog)

    # This should fail (wrong direction)
    feed_dog_consumer(cat_consumer)  # Error: Cat consumer cannot consume Dog

    # Assignment should work (contravariant)
    dog_consumer_ref: ContravariantConsumer[Dog] = animal_consumer  # Should be OK

    # This should fail (wrong direction)
    animal_consumer_ref: ContravariantConsumer[Animal] = dog_consumer  # Error: contravariant

    # Test with write-only container
    animal_writer = WriteOnlyContainer[Animal]()
    dog_writer = WriteOnlyContainer[Dog]()

    def write_dogs(writer: WriteOnlyContainer[Dog]) -> None:
        writer.add_item(Dog("D1"))
        writer.add_item(Dog("D2"))

    write_dogs(dog_writer)  # Should be OK
    write_dogs(animal_writer)  # Should be OK (Animal writer can accept Dog)

    return None


def test_function_variance():
    """Test function variance behavior."""

    # Functions with different signatures
    def process_animal(animal: Animal) -> str:
        return animal.speak()

    def process_dog(dog: Dog) -> str:
        return f"{dog.speak()} and {dog.fetch()}"

    def create_animal() -> Animal:
        return Animal("Generic")

    def create_dog() -> Dog:
        return Dog("Rex")

    # Function wrappers
    animal_to_str = FunctionWrapper[Animal, str](process_animal)
    dog_to_str = FunctionWrapper[Dog, str](process_dog)

    # Test contravariance in input (Animal function can process Dog)
    def use_dog_processor(processor: FunctionWrapper[Dog, str]) -> str:
        return processor.call(Dog("Test"))

    result1 = use_dog_processor(dog_to_str)  # Should be OK
    result2 = use_dog_processor(animal_to_str)  # Should be OK (contravariant in input)

    # Test covariance in output (Dog function can be used where Animal function expected)
    def use_animal_factory(factory: FunctionWrapper[type, Animal]) -> Animal:
        return factory.call(Animal)

    # This is more complex to test directly, so let's use Callable directly
    def test_callable_variance():
        # Callable is contravariant in args, covariant in return
        animal_func: Callable[[Animal], str] = process_animal
        dog_func: Callable[[Dog], str] = process_dog

        # This should work (contravariant in args)
        dog_func_ref: Callable[[Dog], str] = animal_func  # Should be OK

        # This should fail (wrong direction)
        animal_func_ref: Callable[[Animal], str] = dog_func  # Error: contravariant

        # Test with return type (covariant)
        animal_factory: Callable[[], Animal] = create_animal
        dog_factory: Callable[[], Dog] = create_dog

        # This should work (covariant in return)
        animal_factory_ref: Callable[[], Animal] = dog_factory  # Should be OK

        # This should fail (wrong direction)
        dog_factory_ref: Callable[[], Dog] = animal_factory  # Error: covariant

    test_callable_variance()
    return result1, result2


def test_variance_with_generics():
    """Test variance with generic types."""

    # Test List variance (invariant)
    animal_list: List[Animal] = [Animal("A1"), Animal("A2")]
    dog_list: List[Dog] = [Dog("D1"), Dog("D2")]

    # This should fail (List is invariant)
    def process_animal_list(animals: List[Animal]) -> None:
        for animal in animals:
            print(animal.speak())

    process_animal_list(animal_list)  # Should be OK
    process_animal_list(dog_list)  # Should cause error: List is invariant

    # Test with Union types (which are covariant-like)
    def process_animal_or_dog(animal: Union[Animal, Dog]) -> str:
        return animal.speak()

    animal = Animal("Generic")
    dog = Dog("Rex")

    result1 = process_animal_or_dog(animal)  # Should be OK
    result2 = process_animal_or_dog(dog)  # Should be OK

    return result1, result2


def test_variance_pitfalls():
    """Test common variance pitfalls and errors."""

    # Pitfall 1: Trying to use covariant container for writing
    class BadCovariantContainer(Generic[T_co]):
        """BAD: Covariant container that allows writing."""

        def __init__(self):
            self._items: List[T_co] = []

        def get_item(self, index: int) -> T_co:
            return self._items[index]

        def add_item(self, item: T_co) -> None:  # BAD: This breaks covariance
            self._items.append(item)

    # This would be unsafe if allowed
    bad_animal_container = BadCovariantContainer[Animal]()
    bad_dog_container = BadCovariantContainer[Dog]()

    # If this were allowed, it would be unsafe
    bad_animal_ref: BadCovariantContainer[Animal] = bad_dog_container  # Would be unsafe
    # bad_animal_ref.add_item(Cat("Whiskers"))  # Would add Cat to Dog container!

    # Pitfall 2: Trying to use contravariant container for reading
    class BadContravariantContainer(Generic[T_contra]):
        """BAD: Contravariant container that allows reading."""

        def __init__(self, items: List[T_contra]):
            self._items = items

        def add_item(self, item: T_contra) -> None:
            self._items.append(item)

        def get_item(self, index: int) -> T_contra:  # BAD: This breaks contravariance
            return self._items[index]

    # This would be unsafe if allowed
    bad_dog_container2 = BadContravariantContainer[Dog]([Dog("D1")])
    bad_animal_container2 = BadContravariantContainer[Animal]([Animal("A1")])

    # If this were allowed, it would be unsafe
    bad_dog_ref: BadContravariantContainer[Dog] = bad_animal_container2  # Would be unsafe
    # dog = bad_dog_ref.get_item(0)  # Would return Animal as Dog!

    # Pitfall 3: Incorrect variance annotations
    class WrongVarianceContainer(Generic[T_co]):
        """Container with incorrect variance annotation."""

        def __init__(self, value: T_co):
            self._value = value

        def get(self) -> T_co:
            return self._value

        def set(self, value: T_co) -> None:  # This makes it invariant, not covariant
            self._value = value

    # Type checker should catch this inconsistency
    wrong_container = WrongVarianceContainer[Dog](Dog("Rex"))

    return None


def test_practical_variance_examples():
    """Test practical examples of variance usage."""

    # Example 1: Event handlers (contravariant)
    class EventHandler(Generic[T_contra]):
        """Event handler that is contravariant in event type."""

        def handle(self, event: T_contra) -> None:
            print(f"Handling event: {event}")

    class MouseEvent:
        def __init__(self, x: int, y: int):
            self.x = x
            self.y = y

    class ClickEvent(MouseEvent):
        def __init__(self, x: int, y: int, button: str):
            super().__init__(x, y)
            self.button = button

    # Generic handler can handle specific events
    generic_handler = EventHandler[MouseEvent]()
    specific_handler = EventHandler[ClickEvent]()

    def register_click_handler(handler: EventHandler[ClickEvent]) -> None:
        handler.handle(ClickEvent(100, 200, "left"))

    register_click_handler(specific_handler)  # Should be OK
    register_click_handler(generic_handler)  # Should be OK (contravariant)

    # Example 2: Data streams (covariant)
    class DataStream(Generic[T_co]):
        """Data stream that is covariant in data type."""

        def __init__(self, data: List[T_co]):
            self._data = data
            self._index = 0

        def read(self) -> Optional[T_co]:
            if self._index < len(self._data):
                result = self._data[self._index]
                self._index += 1
                return result
            return None

    # Specific stream can be used as general stream
    dog_stream = DataStream[Dog]([Dog("D1"), Dog("D2")])
    animal_stream = DataStream[Animal]([Animal("A1"), Animal("A2")])

    def process_animal_stream(stream: DataStream[Animal]) -> List[str]:
        results = []
        while True:
            animal = stream.read()
            if animal is None:
                break
            results.append(animal.speak())
        return results

    animal_results = process_animal_stream(animal_stream)  # Should be OK
    dog_results = process_animal_stream(dog_stream)  # Should be OK (covariant)

    return animal_results, dog_results


if __name__ == "__main__":
    test_invariant_variance()
    test_covariant_variance()
    test_contravariant_variance()
    test_function_variance()
    test_variance_with_generics()
    test_variance_pitfalls()
    test_practical_variance_examples()
